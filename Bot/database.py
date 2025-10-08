import sqlite3
import asyncio
import aiosqlite
from datetime import datetime

class MessageDatabase:
    def __init__(self, db_path='messages.db'):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS processed_messages (
                    message_id INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    guild_id INTEGER,
                    author_id INTEGER,
                    content TEXT,
                    matched_keywords TEXT,
                    created_at TIMESTAMP,
                    forwarded_at TIMESTAMP
                )
            ''')
            await db.commit()
    
    async def is_message_processed(self, message_id):
        """Check if message has already been processed"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                'SELECT 1 FROM processed_messages WHERE message_id = ?',
                (message_id,)
            ) as cursor:
                return await cursor.fetchone() is not None
    
    async def mark_message_processed(self, message, matched_keywords):
        """Mark message as processed"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO processed_messages 
                (message_id, channel_id, guild_id, author_id, content, matched_keywords, created_at, forwarded_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    message.id,
                    message.channel.id,
                    message.guild.id if message.guild else None,
                    message.author.id,
                    message.content,
                    ','.join(matched_keywords),
                    message.created_at.isoformat(),
                    datetime.utcnow().isoformat()
                )
            )
            await db.commit()
