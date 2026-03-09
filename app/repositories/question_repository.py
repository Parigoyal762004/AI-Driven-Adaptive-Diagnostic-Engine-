"""
Question repository for database operations on questions collection.
"""
from typing import Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.question import QuestionModel
from app.utils.exceptions import QuestionNotFoundException


class QuestionRepository:
    """Data access layer for questions."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.questions
    
    async def get_by_id(self, question_id: str) -> QuestionModel:
        """
        Retrieve a question by ID.
        
        Args:
            question_id: Question ObjectId as string
        
        Returns:
            QuestionModel
        
        Raises:
            QuestionNotFoundException: If question doesn't exist
        """
        try:
            doc = await self.collection.find_one({"_id": ObjectId(question_id)})
        except Exception:
            raise QuestionNotFoundException(f"Invalid question ID format: {question_id}")
        
        if not doc:
            raise QuestionNotFoundException(f"Question not found: {question_id}")
        
        doc["_id"] = str(doc["_id"])
        return QuestionModel(**doc)
    
    async def find_by_difficulty_range(
        self,
        min_difficulty: float,
        max_difficulty: float,
        limit: int = 50
    ) -> list[QuestionModel]:
        """
        Find questions within difficulty range.
        
        Args:
            min_difficulty: Minimum difficulty
            max_difficulty: Maximum difficulty
            limit: Maximum number of questions to return
        
        Returns:
            List of QuestionModel
        """
        cursor = self.collection.find({
            "difficulty": {"$gte": min_difficulty, "$lte": max_difficulty},
            "is_active": True
        }).limit(limit)
        
        questions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            questions.append(QuestionModel(**doc))
        
        return questions
    
    async def get_all_active(self) -> list[QuestionModel]:
        """
        Get all active questions.
        
        Returns:
            List of all active QuestionModel instances
        """
        cursor = self.collection.find({"is_active": True})
        
        questions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            questions.append(QuestionModel(**doc))
        
        return questions
    
    async def get_by_topic(self, topic: str, limit: int = 20) -> list[QuestionModel]:
        """
        Get questions by topic.
        
        Args:
            topic: Topic name
            limit: Maximum number of questions
        
        Returns:
            List of QuestionModel
        """
        cursor = self.collection.find({
            "topic": topic,
            "is_active": True
        }).limit(limit)
        
        questions = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            questions.append(QuestionModel(**doc))
        
        return questions
    
    async def get_random_questions(
        self,
        count: int,
        difficulty_min: Optional[float] = None,
        difficulty_max: Optional[float] = None
    ) -> list[QuestionModel]:
        """
        Get random questions, optionally filtered by difficulty.
        
        Args:
            count: Number of questions to return
            difficulty_min: Optional minimum difficulty
            difficulty_max: Optional maximum difficulty
        
        Returns:
            List of random QuestionModel instances
        """
        match_filter = {"is_active": True}
        
        if difficulty_min is not None and difficulty_max is not None:
            match_filter["difficulty"] = {
                "$gte": difficulty_min,
                "$lte": difficulty_max
            }
        
        pipeline = [
            {"$match": match_filter},
            {"$sample": {"size": count}}
        ]
        
        questions = []
        async for doc in self.collection.aggregate(pipeline):
            doc["_id"] = str(doc["_id"])
            questions.append(QuestionModel(**doc))
        
        return questions
    
    async def count_active(self) -> int:
        """Count total active questions."""
        return await self.collection.count_documents({"is_active": True})
    
    async def get_topics(self) -> list[str]:
        """Get list of unique topics."""
        topics = await self.collection.distinct("topic", {"is_active": True})
        return sorted(topics)
