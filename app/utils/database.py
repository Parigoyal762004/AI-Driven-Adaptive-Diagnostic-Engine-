"""
Database connection management for MongoDB.
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from app.utils.exceptions import DatabaseConnectionException


class Database:
    """MongoDB database connection manager."""
    
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None
    
    @classmethod
    async def connect(cls) -> None:
        """Establish database connection."""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_uri)
            cls.database = cls.client[settings.mongodb_database]
            
            # Test connection
            await cls.client.admin.command('ping')
            print(f"✓ Connected to MongoDB: {settings.mongodb_database}")
            
        except Exception as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            raise DatabaseConnectionException(f"Could not connect to database: {e}")
    
    @classmethod
    async def disconnect(cls) -> None:
        """Close database connection."""
        if cls.client:
            cls.client.close()
            print("✓ Disconnected from MongoDB")
    
    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Get database instance."""
        if cls.database is None:
            raise DatabaseConnectionException("Database not initialized")
        return cls.database
    
    @classmethod
    async def create_indexes(cls) -> None:
        """Create database indexes for optimal query performance."""
        db = cls.get_database()
        
        # Questions collection indexes
        questions = db.questions
        await questions.create_index("difficulty")
        await questions.create_index("topic")
        await questions.create_index("is_active")
        await questions.create_index([("difficulty", 1), ("is_active", 1)])
        await questions.create_index([("difficulty", 1), ("topic", 1), ("is_active", 1)])
        
        # Sessions collection indexes
        sessions = db.user_sessions
        await sessions.create_index("session_id", unique=True)
        await sessions.create_index("user_id")
        await sessions.create_index("status")
        await sessions.create_index("last_activity")
        await sessions.create_index([("user_id", 1), ("status", 1)])
        
        print("✓ Database indexes created")


# Dependency for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database instance."""
    return Database.get_database()
