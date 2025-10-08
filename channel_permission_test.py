import discord
import asyncio
from config import Config

class ChannelPermissionTest:
    def __init__(self, token):
        self.token = token
        intents = discord.Intents.all()
        self.client = discord.Client(intents=intents)
    
    async def test_channel_manipulation(self):
        """Test channel creation and permission manipulation"""
        @self.client.event
        async def on_ready():
            print(f'Testing channel manipulation as {self.client.user}')
            
            guild = self.client.get_guild(Config.TARGET_SERVER_ID)
            
            print("\n📢 TESTING CHANNEL MANIPULATION:")
            
            # Test 1: Channel creation with custom permissions
            await self.test_channel_creation(guild)
            
            # Test 2: Channel permission overrides
            await self.test_permission_overrides(guild)
            
            # Test 3: Channel deletion
            await self.test_channel_deletion(guild)
            
            await self.client.close()
        
        await self.client.start(self.token)
    
    async def test_channel_creation(self, guild):
        """Test creating channels with elevated permissions"""
        print("\n1. Testing Channel Creation:")
        try:
            # Try to create channel with admin permissions for self
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    manage_messages=True,
                    manage_channels=True,
                    administrator=True
                )
            }
            
            channel = await guild.create_text_channel(
                f"test-channel-{self.client.user.id}",
                overwrites=overwrites,
                reason="Security testing"
            )
            print("   ✅ SUCCESS: Created channel with custom permissions!")
            
            # Test if we actually have the permissions
            perms = channel.permissions_for(guild.me)
            if perms.administrator:
                print("   🚨 CRITICAL: Have ADMINISTRATOR in created channel!")
            if perms.manage_channels:
                print("   🚨 CRITICAL: Have MANAGE_CHANNELS in created channel!")
            
            # Cleanup
            await channel.delete()
            print("   ✅ Cleaned up test channel")
            
        except discord.Forbidden:
            print("   ❌ FAILED: Cannot create channels")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    async def test_permission_overrides(self, guild):
        """Test modifying existing channel permissions"""
        print("\n2. Testing Permission Overrides:")
        
        # Test on a channel we might have access to
        for channel in guild.channels:
            if isinstance(channel, discord.TextChannel):
                try:
                    # Try to modify permissions
                    await channel.set_permissions(
                        guild.me,
                        read_messages=True,
                        send_messages=True,
                        manage_messages=True
                    )
                    print(f"   ✅ SUCCESS: Modified permissions in #{channel.name}!")
                    
                    # Revert changes
                    await channel.set_permissions(guild.me, overwrite=None)
                    break
                    
                except discord.Forbidden:
                    continue
                except Exception as e:
                    print(f"   ❌ ERROR in #{channel.name}: {e}")
                    break
    
    async def test_channel_deletion(self, guild):
        """Test channel deletion capabilities"""
        print("\n3. Testing Channel Deletion:")
        
        # Try to delete a test channel we create first
        try:
            test_channel = await guild.create_text_channel(
                f"delete-test-{self.client.user.id}",
                reason="Security testing deletion"
            )
            
            # Try to delete it
            await test_channel.delete()
            print("   ✅ SUCCESS: Can create and delete channels!")
            
        except discord.Forbidden:
            print("   ❌ FAILED: Cannot delete channels")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")

if __name__ == "__main__":
    tester = ChannelPermissionTest(Config.USER_TOKEN)
    asyncio.run(tester.test_channel_manipulation())
