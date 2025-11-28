"""
MongoDB database operations for CodeLens AI
Handles connection, CRUD operations, and data persistence
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import logging

from models import CodeAnalysisResult, AnalysisHistory, DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages MongoDB connections and operations"""
    
    def __init__(self):
        self.config = DatabaseConfig(
            mongodb_url=os.getenv("MONGODB_URL", "mongodb://localhost:27017"),
            database_name=os.getenv("DATABASE_NAME", "codelens_ai"),
            collection_name=os.getenv("COLLECTION_NAME", "analysis_results")
        )
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None
        self.collection = None
        self.connected = False

    async def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.config.mongodb_url)
            # Test the connection
            await self.client.admin.command('ping')
            
            self.database = self.client[self.config.database_name]
            self.collection = self.database[self.config.collection_name]
            self.connected = True
            
            # Create indexes for better performance
            await self._create_indexes()
            
            logger.info("Successfully connected to MongoDB")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            self.connected = False
            return False

    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("Disconnected from MongoDB")

    async def _create_indexes(self):
        """Create database indexes for performance"""
        try:
            # Index on created_at for time-based queries (descending for recent first)
            await self.collection.create_index([("created_at", -1)])
            # Index on language for filtering
            await self.collection.create_index("language")
            # Index on user_id for user-specific queries
            await self.collection.create_index("user_id")
            # Compound index for user + time queries
            await self.collection.create_index([("user_id", 1), ("created_at", -1)])
            # Index on quality score for analytics and sorting
            await self.collection.create_index([("summary.score", -1)])
            # Text search index for code snippets (optional, can be slow on large datasets)
            # await self.collection.create_index([("code_snippet", "text")])
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Failed to create indexes: {e}")

    async def save_analysis(self, analysis_result: CodeAnalysisResult) -> str:
        """Save analysis result to database"""
        if not self.connected:
            logger.warning("Database not connected, skipping save")
            return None
            
        try:
            # Convert Pydantic model to dict for MongoDB
            result_dict = analysis_result.dict(by_alias=True)
            
            # Insert into database
            insert_result = await self.collection.insert_one(result_dict)
            
            logger.info(f"Saved analysis result with ID: {insert_result.inserted_id}")
            return str(insert_result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to save analysis result: {e}")
            return None

    async def get_analysis_by_id(self, analysis_id: str) -> Optional[CodeAnalysisResult]:
        """Retrieve analysis result by ID"""
        if not self.connected:
            return None
            
        try:
            from bson import ObjectId
            result = await self.collection.find_one({"_id": ObjectId(analysis_id)})
            
            if result:
                return CodeAnalysisResult(**result)
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve analysis {analysis_id}: {e}")
            return None

    async def get_recent_analyses(self, limit: int = 10, user_id: Optional[str] = None) -> List[CodeAnalysisResult]:
        """Get recent analysis results"""
        if not self.connected:
            return []
            
        try:
            # Build query filter
            query_filter = {}
            if user_id:
                query_filter["user_id"] = user_id
            
            # Query with sorting and limit
            cursor = self.collection.find(query_filter).sort("created_at", -1).limit(limit)
            results = []
            
            async for document in cursor:
                try:
                    results.append(CodeAnalysisResult(**document))
                except Exception as e:
                    logger.warning(f"Failed to parse analysis result: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve recent analyses: {e}")
            return []

    async def get_analysis_history(self, user_id: Optional[str] = None, days: int = 30) -> AnalysisHistory:
        """Get analysis history and statistics"""
        if not self.connected:
            return AnalysisHistory(
                total_analyses=0,
                languages_used=[],
                average_score=0.0,
                recent_analyses=[]
            )
            
        try:
            # Date range for history
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # Build query filter
            query_filter = {"created_at": {"$gte": since_date}}
            if user_id:
                query_filter["user_id"] = user_id
            
            # Get all matching analyses
            cursor = self.collection.find(query_filter)
            analyses = []
            
            async for document in cursor:
                try:
                    analyses.append(CodeAnalysisResult(**document))
                except Exception as e:
                    logger.warning(f"Failed to parse analysis result: {e}")
                    continue
            
            # Calculate statistics
            total_analyses = len(analyses)
            languages_used = list(set(analysis.language for analysis in analyses))
            
            # Calculate average score
            if analyses:
                total_score = sum(analysis.summary.score for analysis in analyses)
                average_score = total_score / len(analyses)
            else:
                average_score = 0.0
            
            # Get recent analyses (last 10)
            recent_analyses = sorted(analyses, key=lambda x: x.created_at, reverse=True)[:10]
            
            return AnalysisHistory(
                total_analyses=total_analyses,
                languages_used=languages_used,
                average_score=round(average_score, 1),
                recent_analyses=recent_analyses
            )
            
        except Exception as e:
            logger.error(f"Failed to get analysis history: {e}")
            return AnalysisHistory(
                total_analyses=0,
                languages_used=[],
                average_score=0.0,
                recent_analyses=[]
            )

    async def delete_old_analyses(self, days: int = 90) -> int:
        """Delete analyses older than specified days"""
        if not self.connected:
            return 0
            
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            result = await self.collection.delete_many({"created_at": {"$lt": cutoff_date}})
            
            deleted_count = result.deleted_count
            logger.info(f"Deleted {deleted_count} old analysis records")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to delete old analyses: {e}")
            return 0

    async def get_language_statistics(self) -> Dict[str, int]:
        """Get statistics by programming language"""
        if not self.connected:
            return {}
            
        try:
            pipeline = [
                {"$group": {"_id": "$language", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            cursor = self.collection.aggregate(pipeline)
            stats = {}
            
            async for result in cursor:
                stats[result["_id"]] = result["count"]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get language statistics: {e}")
            return {}


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> DatabaseManager:
    """Dependency injection for database manager"""
    if not db_manager.connected:
        await db_manager.connect()
    return db_manager