"""
Database seeding script for the Adaptive Testing Engine.
Populates the database with sample GRE questions.
"""
import asyncio
import json
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "adaptive_testing")


async def seed_questions():
    """Seed the database with sample questions."""
    print("🌱 Starting database seeding...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    questions_collection = db.questions
    
    # Load questions from JSON file
    questions_file = Path(__file__).parent / "gre_questions.json"
    
    if not questions_file.exists():
        print(f"❌ Questions file not found: {questions_file}")
        return
    
    with open(questions_file, 'r') as f:
        questions = json.load(f)
    
    print(f"📚 Loaded {len(questions)} questions from {questions_file.name}")
    
    # Clear existing questions (optional - comment out to preserve existing data)
    existing_count = await questions_collection.count_documents({})
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing questions")
        choice = input("Delete existing questions? (y/N): ")
        if choice.lower() == 'y':
            await questions_collection.delete_many({})
            print("🗑️  Deleted existing questions")
        else:
            print("📝 Keeping existing questions, will add new ones")
    
    # Insert questions
    if questions:
        result = await questions_collection.insert_many(questions)
        print(f"✅ Inserted {len(result.inserted_ids)} questions")
    
    # Create indexes for optimal performance
    print("📇 Creating indexes...")
    
    await questions_collection.create_index("difficulty")
    await questions_collection.create_index("topic")
    await questions_collection.create_index("is_active")
    await questions_collection.create_index([("difficulty", 1), ("is_active", 1)])
    await questions_collection.create_index([("difficulty", 1), ("topic", 1), ("is_active", 1)])
    
    print("✅ Indexes created")
    
    # Verify distribution
    print("\n📊 Question Distribution:")
    
    # By difficulty
    pipeline = [
        {"$match": {"is_active": True}},
        {
            "$bucket": {
                "groupBy": "$difficulty",
                "boundaries": [0.0, 0.4, 0.7, 1.0],
                "default": "Other",
                "output": {"count": {"$sum": 1}}
            }
        }
    ]
    
    distribution = await questions_collection.aggregate(pipeline).to_list(length=10)
    print("\n  Difficulty Levels:")
    for bucket in distribution:
        level = "Easy" if bucket['_id'] < 0.4 else "Medium" if bucket['_id'] < 0.7 else "Hard"
        print(f"    {level} ({bucket['_id']:.1f}+): {bucket['count']} questions")
    
    # By topic
    topic_distribution = await questions_collection.aggregate([
        {"$match": {"is_active": True}},
        {"$group": {"_id": "$topic", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]).to_list(length=20)
    
    print("\n  Topics:")
    for item in topic_distribution:
        print(f"    {item['_id']}: {item['count']} questions")
    
    # Summary statistics
    total = await questions_collection.count_documents({"is_active": True})
    avg_difficulty = await questions_collection.aggregate([
        {"$match": {"is_active": True}},
        {"$group": {"_id": None, "avg": {"$avg": "$difficulty"}}}
    ]).to_list(length=1)
    
    print(f"\n📈 Summary:")
    print(f"  Total active questions: {total}")
    print(f"  Average difficulty: {avg_difficulty[0]['avg']:.2f}")
    print(f"  Number of topics: {len(topic_distribution)}")
    
    client.close()
    print("\n✅ Database seeding completed successfully!")


async def verify_setup():
    """Verify database setup and connection."""
    print("🔍 Verifying database setup...")
    
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    
    try:
        # Test connection
        await client.admin.command('ping')
        print("✅ Database connection successful")
        
        # Check collections
        collections = await db.list_collection_names()
        print(f"📁 Collections: {collections}")
        
        # Check questions
        questions_count = await db.questions.count_documents({"is_active": True})
        print(f"📚 Active questions: {questions_count}")
        
        if questions_count == 0:
            print("⚠️  No questions found. Run the seeding script first!")
        
        # Check sessions
        sessions_count = await db.user_sessions.count_documents({})
        print(f"👥 Total sessions: {sessions_count}")
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
    finally:
        client.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        asyncio.run(verify_setup())
    else:
        asyncio.run(seed_questions())
