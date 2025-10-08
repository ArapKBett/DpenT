import discord
import asyncio
from config import Config

class RoleEscalationTest:
    def __init__(self, token):
        self.token = token
        intents = discord.Intents.all()
        self.client = discord.Client(intents=intents)
    
    async def test_role_manipulation(self):
        """Test various role manipulation techniques"""
        @self.client.event
        async def on_ready():
            print(f'Testing role escalation as {self.client.user}')
            
            guild = self.client.get_guild(Config.TARGET_SERVER_ID)
            if not guild:
                print("Server not found!")
                await self.client.close()
                return
            
            member = guild.get_member(self.client.user.id)
            
            print("\n🎯 TESTING ROLE ESCALATION VECTORS:")
            
            # Test 1: Try to create a new role with admin permissions
            await self.test_role_creation(guild, member)
            
            # Test 2: Try to modify existing roles
            await self.test_role_modification(guild, member)
            
            # Test 3: Try to assign roles to self
            await self.test_role_assignment(guild, member)
            
            await self.client.close()
        
        await self.client.start(self.token)
    
    async def test_role_creation(self, guild, member):
        """Test if user can create roles with elevated permissions"""
        print("\n1. Testing Role Creation:")
        try:
            # Try to create role with various permission levels
            role = await guild.create_role(
                name="TestRole_" + str(self.client.user.id),
                permissions=discord.Permissions(administrator=True),
                reason="Security testing"
            )
            print("   ✅ SUCCESS: Created role with admin permissions!")
            
            # Try to assign to self
            await member.add_roles(role, reason="Security testing")
            print("   ✅ SUCCESS: Assigned admin role to self!")
            
            # Cleanup
            await role.delete()
            
        except discord.Forbidden:
            print("   ❌ FAILED: Cannot create roles or insufficient permissions")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    async def test_role_modification(self, guild, member):
        """Test if user can modify existing roles"""
        print("\n2. Testing Role Modification:")
        
        # Test on lower-level roles first
        for role in guild.roles:
            if role.position < guild.me.top_role.position:
                try:
                    original_name = role.name
                    await role.edit(name=f"Modified_{original_name}")
                    print(f"   ✅ SUCCESS: Modified role {original_name}")
                    
                    # Revert change
                    await role.edit(name=original_name)
                    break
                    
                except discord.Forbidden:
                    continue
                except Exception as e:
                    print(f"   ❌ ERROR modifying {role.name}: {e}")
                    break
    
    async def test_role_assignment(self, guild, member):
        """Test if user can assign roles to themselves"""
        print("\n3. Testing Self-Role Assignment:")
        
        # Find roles that might be assignable
        for role in guild.roles:
            if role.name in ["@everyone"]:  # Skip everyone role
                continue
                
            try:
                # Check if we already have the role
                if role in member.roles:
                    continue
                    
                # Try to add role
                await member.add_roles(role, reason="Security testing")
                print(f"   ✅ SUCCESS: Assigned role {role.name} to self!")
                
                # Remove role
                await member.remove_roles(role, reason="Security testing cleanup")
                break
                
            except discord.Forbidden:
                continue
            except Exception as e:
                print(f"   ❌ ERROR assigning {role.name}: {e}")

if __name__ == "__main__":
    tester = RoleEscalationTest(Config.USER_TOKEN)
    asyncio.run(tester.test_role_manipulation())
