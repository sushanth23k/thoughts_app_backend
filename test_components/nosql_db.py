import os
from dotenv import load_dotenv
from pymongo import MongoClient


def get_mongodb_connection():
    """
    Establishes a connection to MongoDB Atlas using the connection URL from .env file
    Returns:
        MongoClient: MongoDB client instance
    """
    try:
        
        # Get MongoDB connection URL from environment variables
        connection_url = os.getenv('mongodb_connection_url')
        
        if not connection_url:
            raise ValueError("MongoDB connection URL not found in environment variables")
        
        # Create MongoDB client with SSL configuration
        client = MongoClient(
            connection_url,
            tls=True,
            tlsAllowInvalidCertificates=True  # Only use in development
        )
        print("Successfully connected to MongoDB Atlas!")

        # Get the database
        db_name = os.getenv('mongodb_database')
        if not db_name:
            raise ValueError("MongoDB database name not found in environment variables")
            
        db = client[db_name]
        print(f"Connected to database: {db.name}")
        
        return db
    
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        raise

# if __name__ == "__main__":
#     db = get_mongodb_connection()
#     print(f"Connected to database: {db.name}")
