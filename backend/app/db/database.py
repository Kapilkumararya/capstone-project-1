from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

async def init_db():
    logger.info("Initializing MongoDB connection...")
    
    # Create Motor client
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    
    # Extract database name from URI, default to ai_cooking_db
    db_name = settings.MONGODB_URI.split("/")[-1].split("?")[0]
    if not db_name:
        db_name = "ai_cooking_db"
        
    db = client[db_name]
    
    # Define models to be initialized here
    from app.models.user import User
    from app.models.recipe import Recipe
    from app.models.detection import DetectionRun
    from app.models.session import CookingSession

    # Initialize beanie with all document models
    await init_beanie(database=db, document_models=[User, Recipe, DetectionRun, CookingSession])
    logger.info("Database initialized successfully.")

