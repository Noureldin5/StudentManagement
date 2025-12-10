# MongoDB Configuration and Connection Manager
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()


class MongoDBConnection:
    """Singleton MongoDB connection manager"""
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self):
        """Establish MongoDB connection"""
        try:
            # Get MongoDB URI from environment or use default
            mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGODB_DB_NAME', 'student_management_logs')

            # Create MongoDB client
            self._client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000
            )

            # Test connection
            self._client.admin.command('ping')
            
            # Get database
            self._db = self._client[db_name]
            
            print(f"✓ Connected to MongoDB database: {db_name}")
            
            # Create indexes for better performance
            self._create_indexes()

        except ConnectionFailure as e:
            print(f"✗ Failed to connect to MongoDB: {e}")
            print("  MongoDB logging will be disabled.")
            self._client = None
            self._db = None
        except Exception as e:
            print(f"✗ MongoDB connection error: {e}")
            self._client = None
            self._db = None

    def _create_indexes(self):
        """Create indexes for collections"""
        if self._db is not None:
            # Activity logs indexes
            self._db.activity_logs.create_index([("timestamp", -1)])  # Descending for recent first
            self._db.activity_logs.create_index([("action_type", 1)])
            self._db.activity_logs.create_index([("user_id", 1)])
            self._db.activity_logs.create_index([("user_type", 1)])
            
            # Notification logs indexes
            self._db.notification_logs.create_index([("created_at", -1)])
            self._db.notification_logs.create_index([("recipient_email", 1)])
            self._db.notification_logs.create_index([("status", 1)])

    @property
    def db(self):
        return self._db

    @property
    def is_connected(self):
        return self._db is not None

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            print("✓ MongoDB connection closed")


mongo_connection = MongoDBConnection()

