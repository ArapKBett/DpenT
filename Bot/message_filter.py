import re
from config import Config

class MessageFilter:
    def __init__(self):
        self.keywords = Config.KEYWORDS
        # Create regex pattern for case-insensitive matching
        self.pattern = re.compile(
            r'\b(' + '|'.join(re.escape(keyword) for keyword in self.keywords) + r')\b',
            re.IGNORECASE
        )
    
    def contains_keywords(self, content):
        """Check if message content contains any of the keywords"""
        return bool(self.pattern.search(content))
    
    def get_matched_keywords(self, content):
        """Return list of matched keywords"""
        matches = self.pattern.findall(content)
        return [match.lower() for match in matches]
    
    def should_forward(self, message):
        """Determine if message should be forwarded"""
        # Skip messages from bots
        if message.author.bot:
            return False
        
        # Check if message contains keywords
        if self.contains_keywords(message.content):
            return True
        
        # Also check embeds
        for embed in message.embeds:
            if embed.title and self.contains_keywords(embed.title):
                return True
            if embed.description and self.contains_keywords(embed.description):
                return True
            if embed.fields:
                for field in embed.fields:
                    if field.name and self.contains_keywords(field.name):
                        return True
                    if field.value and self.contains_keywords(field.value):
                        return True
        
        return False
