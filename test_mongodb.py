"""
MongoDB Connection Test Script

Run this script to test your MongoDB connection:
    python test_mongodb.py
"""

from mongo_config import mongo_connection

def test_mongodb_connection():
    print("=" * 60)
    print("MongoDB Connection Test")
    print("=" * 60)

    if mongo_connection.is_connected:
        print("✓ MongoDB is connected!")
        print(f"  Database: {mongo_connection.db.name}")

        # Test write operation
        try:
            test_doc = {
                "test": "connection",
                "message": "MongoDB is working!"
            }
            result = mongo_connection.db.test_collection.insert_one(test_doc)
            print(f"✓ Write test successful (ID: {result.inserted_id})")

            # Clean up test document
            mongo_connection.db.test_collection.delete_one({"_id": result.inserted_id})
            print("✓ Cleanup successful")

        except Exception as e:
            print(f"✗ Write test failed: {e}")

        # Show collections
        collections = mongo_connection.db.list_collection_names()
        if collections:
            print(f"\n📂 Existing collections:")
            for col in collections:
                count = mongo_connection.db[col].count_documents({})
                print(f"   - {col}: {count} documents")
        else:
            print("\n📂 No collections yet (will be created on first activity)")

    else:
        print("✗ MongoDB is NOT connected!")
        print("\nPossible issues:")
        print("  1. MongoDB service is not running")
        print("  2. MONGODB_URI in .env is incorrect")
        print("  3. MongoDB is not installed")
        print("\nThe app will still work, but activity logging will be disabled.")
        print("\nSee MONGODB_SETUP.md for installation instructions.")

    print("=" * 60)

if __name__ == "__main__":
    test_mongodb_connection()

