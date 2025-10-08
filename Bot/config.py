import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Discord Bot Token
    TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Target Server IDs
    TARGET_SERVER_IDS = [
        int(server_id.strip()) for server_id in 
        os.getenv('TARGET_SERVER_IDS', '').split(',') 
        if server_id.strip()
    ]
    
    # Output Channel ID
    OUTPUT_CHANNEL_ID = int(os.getenv('OUTPUT_CHANNEL_ID'))
    
    # Keywords to monitor
    KEYWORDS = [
        'urgent', 'dev', 'developer', 'scripter', 'script', 'pay', 'paying',
        'hiring', 'recruit', 'recruiting', 'bounty', 'reward', 'bug bounty',
        'vulnerability', 'pentest', 'penetration test', 'security researcher',
        'ctf', 'forensics', 'malware analysis', 'reverse engineering',
        'exploit', 'looking for', 'need help', 'freelance', 'contract',
        'project', 'opportunity', 'position', 'job', 'work', 'gig'
    ]
    
    # Check if all required environment variables are set
    @classmethod
    def validate(cls):
        if not cls.TOKEN:
            raise ValueError("DISCORD_TOKEN is not set in .env file")
        if not cls.TARGET_SERVER_IDS:
            raise ValueError("TARGET_SERVER_IDS are not set in .env file")
        if not cls.OUTPUT_CHANNEL_ID:
            raise ValueError("OUTPUT_CHANNEL_ID is not set in .env file")
