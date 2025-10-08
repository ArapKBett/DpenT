import discord
from discord.ext import commands
import asyncio
import logging
from config import Config
from message_filter import MessageFilter
from database import MessageDatabase

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CybersecurityLabBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        
        self.config = Config
        self.filter = MessageFilter()
        self.db = MessageDatabase()
        
        # Track monitored servers
        self.monitored_servers = set()
        
    async def setup_hook(self):
        """Called when bot is starting up"""
        await self.db.init_db()
        logger.info("Database initialized")
        
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info('------')
        
        # Validate configuration
        try:
            self.config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            await self.close()
            return
        
        # Setup monitoring for target servers
        await self.setup_monitoring()
        
    async def setup_monitoring(self):
        """Setup monitoring for target servers"""
        for server_id in self.config.TARGET_SERVER_IDS:
            server = self.get_guild(server_id)
            if server:
                self.monitored_servers.add(server_id)
                logger.info(f"Monitoring server: {server.name} (ID: {server.id})")
            else:
                logger.warning(f"Could not find server with ID: {server_id}")
        
        if not self.monitored_servers:
            logger.error("No servers available for monitoring!")
            return
        
        logger.info(f"Monitoring {len(self.monitored_servers)} server(s)")
        logger.info("Bot is ready to filter messages!")
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Don't process our own messages
        if message.author == self.user:
            return
        
        # Only process messages from monitored servers
        if not message.guild or message.guild.id not in self.monitored_servers:
            return
        
        # Check if we've already processed this message
        if await self.db.is_message_processed(message.id):
            return
        
        # Check if message should be forwarded
        if self.filter.should_forward(message):
            await self.process_and_forward(message)
        
        # Process commands
        await self.process_commands(message)
    
    async def process_and_forward(self, message):
        """Process message and forward to output channel"""
        try:
            matched_keywords = self.filter.get_matched_keywords(message.content)
            
            # Create embed for forwarded message
            embed = discord.Embed(
                title="🚨 Keyword Match Found",
                description=message.content,
                color=0x00ff00,
                timestamp=message.created_at
            )
            
            embed.add_field(
                name="Server",
                value=f"{message.guild.name} (`{message.guild.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Channel",
                value=f"{message.channel.mention} (`{message.channel.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Author",
                value=f"{message.author} (`{message.author.id}`)",
                inline=True
            )
            
            embed.add_field(
                name="Matched Keywords",
                value=", ".join(matched_keywords) or "Unknown",
                inline=False
            )
            
            embed.add_field(
                name="Message Link",
                value=f"[Jump to Message]({message.jump_url})",
                inline=False
            )
            
            embed.set_footer(text=f"Message ID: {message.id}")
            
            # Get output channel
            output_channel = self.get_channel(self.config.OUTPUT_CHANNEL_ID)
            if output_channel:
                await output_channel.send(embed=embed)
                logger.info(f"Forwarded message from {message.author} in {message.guild.name}")
                
                # Mark as processed
                await self.db.mark_message_processed(message, matched_keywords)
            else:
                logger.error(f"Could not find output channel with ID: {self.config.OUTPUT_CHANNEL_ID}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f"Command error: {error}")

# Bot commands
@commands.command(name='status')
async def status_command(ctx):
    """Check bot status and monitored servers"""
    bot = ctx.bot
    embed = discord.Embed(title="Bot Status", color=0x7289DA)
    
    embed.add_field(
        name="Monitored Servers",
        value=str(len(bot.monitored_servers)),
        inline=True
    )
    
    embed.add_field(
        name="Uptime",
        value=f"<t:{int(bot.start_time.timestamp())}:R>",
        inline=True
    )
    
    if bot.monitored_servers:
        servers_info = []
        for server_id in bot.monitored_servers:
            server = bot.get_guild(server_id)
            if server:
                servers_info.append(f"• {server.name} (`{server.id}`)")
        
        embed.add_field(
            name="Servers Being Monitored",
            value="\n".join(servers_info) or "None",
            inline=False
        )
    
    await ctx.send(embed=embed)

@commands.command(name='keywords')
async def keywords_command(ctx):
    """Show current keywords being monitored"""
    embed = discord.Embed(title="Monitored Keywords", color=0x7289DA)
    
    keywords = Config.KEYWORDS
    chunks = [keywords[i:i + 10] for i in range(0, len(keywords), 10)]
    
    for i, chunk in enumerate(chunks):
        embed.add_field(
            name=f"Group {i+1}" if len(chunks) > 1 else "Keywords",
            value="\n".join(f"• {keyword}" for keyword in chunk),
            inline=True
        )
    
    await ctx.send(embed=embed)

def main():
    """Main function to run the bot"""
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    bot = CybersecurityLabBot()
    
    # Add commands
    bot.add_command(status_command)
    bot.add_command(keywords_command)
    
    # Run the bot
    bot.run(Config.TOKEN)

if __name__ == "__main__":
    main()
