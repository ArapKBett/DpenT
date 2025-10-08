import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # User account token (for testing as regular member)
    USER_TOKEN = os.getenv('USER_TOKEN')
    
    # Bot token (for comparison/testing)
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # Target server ID
    TARGET_SERVER_ID = int(os.getenv('TARGET_SERVER_ID'))
    
    # Test channel ID
    TEST_CHANNEL_ID = int(os.getenv('TEST_CHANNEL_ID'))
    
    # Your user ID for targeting
    YOUR_USER_ID = int(os.getenv('YOUR_USER_ID'))
