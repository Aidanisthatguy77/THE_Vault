from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ============ MODELS ============

# Game Models
class GameBase(BaseModel):
    title: str
    year: str
    cover_image: str
    hook_text: str
    cover_athletes: str
    description: str
    youtube_embed: Optional[str] = None
    order: int = 0
    is_active: bool = True

class GameCreate(GameBase):
    pass

class GameUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[str] = None
    cover_image: Optional[str] = None
    hook_text: Optional[str] = None
    cover_athletes: Optional[str] = None
    description: Optional[str] = None
    youtube_embed: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None

class Game(GameBase):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Comment Models
class CommentCreate(BaseModel):
    author_name: str
    content: str
    parent_id: Optional[str] = None

class Comment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_name: str
    content: str
    parent_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    replies: List["Comment"] = []

# Email Subscription Model
class EmailSubscriptionCreate(BaseModel):
    email: str

class EmailSubscription(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    subscribed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Admin Auth Model
class AdminLogin(BaseModel):
    password: str

# ============ GAME ROUTES ============

@api_router.get("/games", response_model=List[Game])
async def get_games():
    games = await db.games.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)
    return games

@api_router.get("/games/all", response_model=List[Game])
async def get_all_games():
    """Admin route to get all games including inactive"""
    games = await db.games.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return games

@api_router.get("/games/{game_id}", response_model=Game)
async def get_game(game_id: str):
    game = await db.games.find_one({"id": game_id}, {"_id": 0})
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game

@api_router.post("/games", response_model=Game)
async def create_game(game_data: GameCreate):
    game = Game(**game_data.model_dump())
    doc = game.model_dump()
    await db.games.insert_one(doc)
    return game

@api_router.put("/games/{game_id}", response_model=Game)
async def update_game(game_id: str, game_data: GameUpdate):
    existing = await db.games.find_one({"id": game_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Game not found")
    
    update_data = {k: v for k, v in game_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.games.update_one({"id": game_id}, {"$set": update_data})
    updated = await db.games.find_one({"id": game_id}, {"_id": 0})
    return updated

@api_router.delete("/games/{game_id}")
async def delete_game(game_id: str):
    result = await db.games.delete_one({"id": game_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Game not found")
    return {"message": "Game deleted successfully"}

# ============ COMMENT ROUTES ============

@api_router.get("/comments", response_model=List[Comment])
async def get_comments():
    # Get all top-level comments (no parent_id)
    comments = await db.comments.find({"parent_id": None}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    # For each comment, get replies
    for comment in comments:
        replies = await db.comments.find({"parent_id": comment["id"]}, {"_id": 0}).sort("created_at", 1).to_list(100)
        comment["replies"] = replies
    
    return comments

@api_router.post("/comments", response_model=Comment)
async def create_comment(comment_data: CommentCreate):
    comment = Comment(
        author_name=comment_data.author_name,
        content=comment_data.content,
        parent_id=comment_data.parent_id
    )
    doc = comment.model_dump()
    await db.comments.insert_one(doc)
    return comment

@api_router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str):
    # Delete comment and all its replies
    await db.comments.delete_many({"parent_id": comment_id})
    result = await db.comments.delete_one({"id": comment_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"message": "Comment deleted successfully"}

# ============ EMAIL SUBSCRIPTION ROUTES ============

@api_router.post("/subscribe", response_model=EmailSubscription)
async def subscribe_email(subscription: EmailSubscriptionCreate):
    # Check if email already exists
    existing = await db.subscriptions.find_one({"email": subscription.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already subscribed")
    
    sub = EmailSubscription(email=subscription.email)
    doc = sub.model_dump()
    await db.subscriptions.insert_one(doc)
    return sub

@api_router.get("/subscriptions", response_model=List[EmailSubscription])
async def get_subscriptions():
    subs = await db.subscriptions.find({}, {"_id": 0}).sort("subscribed_at", -1).to_list(1000)
    return subs

# ============ ADMIN AUTH ============

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'legacyvault2k')

@api_router.post("/admin/login")
async def admin_login(login_data: AdminLogin):
    if login_data.password == ADMIN_PASSWORD:
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid password")

# ============ SEED DATA ============

@api_router.post("/seed")
async def seed_games():
    """Seed initial game data"""
    # Check if games already exist
    count = await db.games.count_documents({})
    if count > 0:
        return {"message": "Games already seeded", "count": count}
    
    default_games = [
        {
            "id": str(uuid.uuid4()),
            "title": "NBA 2K15",
            "year": "2014",
            "cover_image": "https://images.unsplash.com/photo-1546519638-68e109498ee2?auto=format&fit=crop&w=600&q=80",
            "hook_text": "Where the modern 2K era truly began",
            "cover_athletes": "Kevin Durant (Oklahoma City Thunder)",
            "description": "Pharrell curated the soundtrack. First true story-driven MyCAREER. Pro-Am leagues that felt alive. The game that made everyone say 'this is next-gen.' This is where the modern 2K era truly began.",
            "youtube_embed": "https://www.youtube.com/embed/Qe8c2cQo1No",
            "order": 1,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "NBA 2K16",
            "year": "2015",
            "cover_image": "https://images.unsplash.com/photo-1504450758481-7338eba7524a?auto=format&fit=crop&w=600&q=80",
            "hook_text": "The one OGs still call the GOAT",
            "cover_athletes": "Stephen Curry / James Harden / Anthony Davis + Michael Jordan Special Edition",
            "description": "Spike Lee wrote and directed MyCAREER. Jordan: The Legend mode. The Park was pure chaos and glory. Customization went crazy. This is the one OGs still call the GOAT.",
            "youtube_embed": "https://www.youtube.com/embed/aV2DLkDPwM8",
            "order": 2,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "NBA 2K17",
            "year": "2016",
            "cover_image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=600&q=80",
            "hook_text": "Pure basketball soul",
            "cover_athletes": "Paul George + Kobe Bryant Legend Edition",
            "description": "Refined shooting, buttery gameplay, deep MyGM/MyLeague. Kobe tribute everywhere. The last game before everything changed — pure basketball soul.",
            "youtube_embed": "https://www.youtube.com/embed/ZsGDAPlboCk",
            "order": 3,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "NBA 2K20",
            "year": "2019",
            "cover_image": "https://images.unsplash.com/photo-1533923156502-be31530547c4?auto=format&fit=crop&w=600&q=80",
            "hook_text": "The final masterpiece",
            "cover_athletes": "Anthony Davis + Dwyane Wade Legend Edition",
            "description": "The Neighborhood exploded. WNBA arrived. Legends flooded MyTEAM. Best graphics and animations of the decade. The final masterpiece before the yearly reset cycle got old.",
            "youtube_embed": "https://www.youtube.com/embed/OmQoeqvAYmo",
            "order": 4,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "NBA 2K27",
            "year": "2026",
            "cover_image": "https://images.unsplash.com/photo-1574623452334-1e0ac2b3ccb4?auto=format&fit=crop&w=600&q=80",
            "hook_text": "The newest era continues",
            "cover_athletes": "TBD - Update cover athlete",
            "description": "The latest installment in the 2K franchise. Update this description with the latest features and innovations.",
            "youtube_embed": "",
            "order": 5,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.games.insert_many(default_games)
    return {"message": "Games seeded successfully", "count": len(default_games)}

@api_router.get("/")
async def root():
    return {"message": "NBA 2K Legacy Vault API"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
