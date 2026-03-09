"""
Session repository for database operations on user sessions.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.session import UserSessionModel
from app.utils.exceptions import SessionNotFoundException, SessionExpiredException


class SessionRepository:
    """Data access layer for user sessions."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.user_sessions
        self.session_timeout_hours = 24  # Sessions expire after 24 hours
    
    async def create_session(
        self,
        user_id: Optional[str] = None,
        user_name: Optional[str] = None,
        test_type: str = "GRE",
        max_questions: int = 10,
        initial_ability: float = 0.0
    ) -> UserSessionModel:
        """
        Create a new testing session.
        
        Args:
            user_id: Optional user identifier
            user_name: Optional user name
            test_type: Type of test
            max_questions: Maximum questions for session
            initial_ability: Starting ability estimate
        
        Returns:
            Created UserSessionModel
        """
        session_id = f"sess_{uuid.uuid4().hex[:12]}"
        
        session = UserSessionModel(
            session_id=session_id,
            user_id=user_id,
            user_name=user_name,
            test_type=test_type,
            current_ability=initial_ability,
            questions_remaining=max_questions
        )
        
        # Convert to dict for MongoDB
        session_dict = session.model_dump(exclude={"id"}, by_alias=True)
        
        # Insert into database
        result = await self.collection.insert_one(session_dict)
        
        # Set the MongoDB _id
        session_dict["_id"] = str(result.inserted_id)
        
        return UserSessionModel(**session_dict)
    
    async def get_session(self, session_id: str) -> UserSessionModel:
        """
        Retrieve session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            UserSessionModel
        
        Raises:
            SessionNotFoundException: If session doesn't exist
            SessionExpiredException: If session has expired
        """
        doc = await self.collection.find_one({"session_id": session_id})
        
        if not doc:
            raise SessionNotFoundException(f"Session not found: {session_id}")
        
        # Check if session has expired
        last_activity = doc.get("last_activity")
        if last_activity:
            time_since_activity = datetime.utcnow() - last_activity
            if time_since_activity > timedelta(hours=self.session_timeout_hours):
                # Mark as expired
                await self.collection.update_one(
                    {"session_id": session_id},
                    {"$set": {"status": "expired"}}
                )
                raise SessionExpiredException(
                    f"Session expired (inactive for {self.session_timeout_hours} hours)"
                )
        
        doc["_id"] = str(doc["_id"])
        return UserSessionModel(**doc)
    
    async def update_session(self, session: UserSessionModel) -> UserSessionModel:
        """
        Update existing session.
        
        Args:
            session: Session to update
        
        Returns:
            Updated UserSessionModel
        """
        session_dict = session.model_dump(exclude={"id"}, by_alias=True)
        
        await self.collection.update_one(
            {"session_id": session.session_id},
            {"$set": session_dict}
        )
        
        return session
    
    async def get_user_sessions(
        self,
        user_id: str,
        limit: int = 10
    ) -> list[UserSessionModel]:
        """
        Get sessions for a specific user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of sessions to return
        
        Returns:
            List of UserSessionModel
        """
        cursor = self.collection.find(
            {"user_id": user_id}
        ).sort("started_at", -1).limit(limit)
        
        sessions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            sessions.append(UserSessionModel(**doc))
        
        return sessions
    
    async def mark_completed(self, session_id: str) -> None:
        """
        Mark a session as completed.
        
        Args:
            session_id: Session to mark as completed
        """
        await self.collection.update_one(
            {"session_id": session_id},
            {
                "$set": {
                    "status": "completed",
                    "completed_at": datetime.utcnow()
                }
            }
        )
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session to delete
        
        Returns:
            True if deleted, False if not found
        """
        result = await self.collection.delete_one({"session_id": session_id})
        return result.deleted_count > 0
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (older than timeout period).
        
        Returns:
            Number of sessions deleted
        """
        expiry_threshold = datetime.utcnow() - timedelta(hours=self.session_timeout_hours)
        
        result = await self.collection.delete_many({
            "last_activity": {"$lt": expiry_threshold},
            "status": {"$in": ["in_progress", "expired"]}
        })
        
        return result.deleted_count
    
    async def count_active_sessions(self) -> int:
        """Count currently active sessions."""
        return await self.collection.count_documents({"status": "in_progress"})
