import discord
import asyncio
from config import Config

class PermissionAnalyzer:
    def __init__(self, token):
        self.token = token
        intents = discord.Intents.all()
        self.client = discord.Client(intents=intents)
        
    async def analyze_permissions(self):
        """Analyze current user permissions and potential escalation points"""
        @self.client.event
        async def on_ready():
            print(f'Logged in as {self.client.user} (ID: {self.client.user.id})')
            print('------')
            
            target_guild = self.client.get_guild(Config.TARGET_SERVER_ID)
            if not target_guild:
                print("Target server not found!")
                await self.client.close()
                return
            
            # Get current member object
            member = target_guild.get_member(self.client.user.id)
            if not member:
                print("Not a member of target server!")
                await self.client.close()
                return
            
            print(f"=== Permission Analysis for {member} ===")
            
            # Analyze current permissions
            await self.analyze_current_permissions(member, target_guild)
            
            # Analyze role vulnerabilities
            await self.analyze_role_vulnerabilities(member, target_guild)
            
            # Analyze channel permission overrides
            await self.analyze_channel_overrides(member, target_guild)
            
            await self.client.close()
        
        try:
            await self.client.start(self.token)
        except Exception as e:
            print(f"Error: {e}")
    
    async def analyze_current_permissions(self, member, guild):
        """Analyze current permissions of the user"""
        print("\n📋 CURRENT PERMISSIONS:")
        permissions = member.guild_permissions
        
        critical_perms = [
            'administrator', 'manage_guild', 'manage_roles',
            'manage_channels', 'manage_webhooks', 'manage_nicknames',
            'kick_members', 'ban_members', 'mention_everyone'
        ]
        
        for perm in critical_perms:
            value = getattr(permissions, perm)
            status = "✅" if value else "❌"
            print(f"  {status} {perm.upper()}: {value}")
    
    async def analyze_role_vulnerabilities(self, member, guild):
        """Analyze potential role manipulation vulnerabilities"""
        print("\n🔍 ROLE VULNERABILITY ANALYSIS:")
        
        # Check if user can manage their own roles
        print(f"  Can manage roles: {member.guild_permissions.manage_roles}")
        
        # Analyze existing roles
        for role in guild.roles:
            if role in member.roles:
                print(f"  👤 Current role: {role.name} (ID: {role.id})")
                
                # Check for dangerous permissions in current roles
                dangerous_perms = []
                if role.permissions.administrator:
                    dangerous_perms.append("ADMINISTRATOR")
                if role.permissions.manage_roles:
                    dangerous_perms.append("MANAGE_ROLES")
                if role.permissions.manage_guild:
                    dangerous_perms.append("MANAGE_GUILD")
                
                if dangerous_perms:
                    print(f"    ⚠️  Dangerous permissions: {', '.join(dangerous_perms)}")
    
    async def analyze_channel_overrides(self, member, guild):
        """Analyze channel-specific permission overrides"""
        print("\n📁 CHANNEL PERMISSION OVERRIDES:")
        
        for channel in guild.channels:
            if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                overwrites = channel.overwrites_for(member)
                if overwrites.pair() != (discord.Permissions.none(), discord.Permissions.none()):
                    print(f"  📍 {channel.name} has custom permissions")
                    
                    allowed, denied = overwrites.pair()
                    if allowed.administrator:
                        print(f"    🚨 ADMINISTRATOR permission granted in channel!")
                    if allowed.manage_roles:
                        print(f"    🚨 MANAGE_ROLES permission granted in channel!")
                    if allowed.manage_channels:
                        print(f"    🚨 MANAGE_CHANNELS permission granted in channel!")

if __name__ == "__main__":
    analyzer = PermissionAnalyzer(Config.USER_TOKEN)
    asyncio.run(analyzer.analyze_permissions())
