import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database connection details
print("Database Connection Details:")
print(f"POSTGRES_SERVER: {os.getenv('POSTGRES_SERVER')}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

# Test database connection
async def test_connection():
    from sqlalchemy.ext.asyncio import create_async_engine
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("\nError: DATABASE_URL is not set")
        return
    
    # Make sure the URL uses asyncpg
    if db_url.startswith('postgresql://'):
        db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    
    print(f"\nAttempting to connect to: {db_url.split('@')[-1]}")
    
    try:
        engine = create_async_engine(db_url, echo=True)
        async with engine.connect() as conn:
            print("Connected to database successfully!")
            result = await conn.execute("SELECT version()")
            print(f"Database version: {result.scalar()}")
    except Exception as e:
        print(f"\nError connecting to database:")
        print(f"Type: {type(e).__name__}")
        print(f"Error: {str(e)}")
    finally:
        if 'engine' in locals():
            await engine.dispose()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_connection())
