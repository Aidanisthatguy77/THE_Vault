from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import re
import zipfile
import tempfile
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import shutil
import base64
import httpx
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create uploads directory
UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

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
    is_admin: bool = False

class Comment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    author_name: str
    content: str
    parent_id: Optional[str] = None
    is_admin: bool = False
    likes: int = 0
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

# Petition Signature Model
class PetitionSignCreate(BaseModel):
    name: str
    location: Optional[str] = None

class PetitionSign(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    location: Optional[str] = None
    signed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Admin Auth Model
class AdminLogin(BaseModel):
    password: str

# Clip/Media Model
class ClipCreate(BaseModel):
    game_id: str
    title: str
    platform: str  # youtube, tiktok, instagram, twitter
    embed_url: str
    description: Optional[str] = None
    order: int = 0

class ClipUpdate(BaseModel):
    title: Optional[str] = None
    platform: Optional[str] = None
    embed_url: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None

class Clip(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    game_id: str
    title: str
    platform: str
    embed_url: str
    description: Optional[str] = None
    order: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Site Content Model (for editable sections)
class SiteContentUpdate(BaseModel):
    key: str
    value: str

class SiteContent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str
    value: str
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Proof of Demand Model
class ProofCreate(BaseModel):
    image_url: str
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    order: int = 0

class ProofUpdate(BaseModel):
    image_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    order: Optional[int] = None

class Proof(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    image_url: str
    title: str
    description: Optional[str] = None
    source: Optional[str] = None
    order: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Vault Mockup Model
class MockupCreate(BaseModel):
    title: str
    description: str
    media_type: str = "image"  # "image" or "video"
    image_url: Optional[str] = None
    video_embed_url: Optional[str] = None
    order: int = 0

class MockupUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    media_type: Optional[str] = None
    image_url: Optional[str] = None
    video_embed_url: Optional[str] = None
    order: Optional[int] = None

class Mockup(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    media_type: str = "image"
    image_url: Optional[str] = None
    video_embed_url: Optional[str] = None
    order: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ============ HEALTH CHECK ============

@api_router.get("/health")
async def health_check():
    """Health check endpoint for connectivity status"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

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
        parent_id=comment_data.parent_id,
        is_admin=comment_data.is_admin,
        likes=0
    )
    doc = comment.model_dump()
    await db.comments.insert_one(doc)
    return comment

@api_router.post("/comments/{comment_id}/like")
async def like_comment(comment_id: str):
    """Like a comment"""
    result = await db.comments.update_one(
        {"id": comment_id},
        {"$inc": {"likes": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found")
    updated = await db.comments.find_one({"id": comment_id}, {"_id": 0})
    return {"likes": updated.get("likes", 0)}

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

@api_router.delete("/subscriptions/{sub_id}")
async def delete_subscription(sub_id: str):
    result = await db.subscriptions.delete_one({"id": sub_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription deleted"}

# ============ PETITION ROUTES ============

@api_router.post("/petition/sign", response_model=PetitionSign)
async def sign_petition(sign_data: PetitionSignCreate):
    signature = PetitionSign(name=sign_data.name, location=sign_data.location)
    doc = signature.model_dump()
    await db.petition.insert_one(doc)
    return signature

@api_router.get("/petition/count")
async def get_petition_count():
    count = await db.petition.count_documents({})
    return {"count": count}

@api_router.get("/petition/signatures")
async def get_petition_signatures():
    signatures = await db.petition.find({}, {"_id": 0}).sort("signed_at", -1).to_list(1000)
    return signatures

@api_router.delete("/petition/{sig_id}")
async def delete_petition_signature(sig_id: str):
    result = await db.petition.delete_one({"id": sig_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Signature not found")
    return {"message": "Signature deleted"}

@api_router.post("/petition/add-bulk")
async def add_bulk_signatures(count: int = 100):
    """Add bulk signatures for social proof"""
    names = ["Jordan Fan", "2K Legend", "Park Player", "MyCareer OG", "Hooper", "Baller", "Court King", "Dunk Master", "3PT Shooter", "Crossover King"]
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Miami", "Atlanta", "Detroit", "Boston", "Dallas", "Phoenix", None]
    import random
    
    signatures = []
    for i in range(count):
        sig = {
            "id": str(uuid.uuid4()),
            "name": f"{random.choice(names)} #{random.randint(1, 9999)}",
            "location": random.choice(locations),
            "signed_at": datetime.now(timezone.utc).isoformat()
        }
        signatures.append(sig)
    
    await db.petition.insert_many(signatures)
    return {"message": f"Added {count} signatures", "total": await db.petition.count_documents({})}

# ============ ADMIN AUTH ============

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'A@070610')

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

# ============ CLIPS/MEDIA ROUTES ============

@api_router.get("/clips")
async def get_all_clips():
    """Get all clips"""
    clips = await db.clips.find({}, {"_id": 0}).sort("order", 1).to_list(1000)
    return clips

@api_router.get("/clips/game/{game_id}")
async def get_clips_by_game(game_id: str):
    """Get clips for a specific game"""
    clips = await db.clips.find({"game_id": game_id}, {"_id": 0}).sort("order", 1).to_list(100)
    return clips

@api_router.post("/clips", response_model=Clip)
async def create_clip(clip_data: ClipCreate):
    clip = Clip(**clip_data.model_dump())
    doc = clip.model_dump()
    await db.clips.insert_one(doc)
    return clip

@api_router.put("/clips/{clip_id}", response_model=Clip)
async def update_clip(clip_id: str, clip_data: ClipUpdate):
    existing = await db.clips.find_one({"id": clip_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    update_data = {k: v for k, v in clip_data.model_dump().items() if v is not None}
    await db.clips.update_one({"id": clip_id}, {"$set": update_data})
    updated = await db.clips.find_one({"id": clip_id}, {"_id": 0})
    return updated

@api_router.delete("/clips/{clip_id}")
async def delete_clip(clip_id: str):
    result = await db.clips.delete_one({"id": clip_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Clip not found")
    return {"message": "Clip deleted"}

@api_router.delete("/clips/game/{game_id}")
async def delete_all_clips_for_game(game_id: str):
    """Delete all clips for a game"""
    result = await db.clips.delete_many({"game_id": game_id})
    return {"message": f"Deleted {result.deleted_count} clips"}

# ============ SITE CONTENT ROUTES ============

@api_router.get("/content")
async def get_all_content():
    """Get all site content"""
    content = await db.site_content.find({}, {"_id": 0}).to_list(100)
    return {item["key"]: item["value"] for item in content}

@api_router.get("/content/{key}")
async def get_content(key: str):
    """Get specific content by key"""
    content = await db.site_content.find_one({"key": key}, {"_id": 0})
    if not content:
        return {"key": key, "value": ""}
    return content

@api_router.post("/content")
async def update_content(content_data: SiteContentUpdate):
    """Update or create site content"""
    existing = await db.site_content.find_one({"key": content_data.key})
    if existing:
        await db.site_content.update_one(
            {"key": content_data.key},
            {"$set": {"value": content_data.value, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
    else:
        doc = SiteContent(key=content_data.key, value=content_data.value).model_dump()
        await db.site_content.insert_one(doc)
    return {"message": "Content updated", "key": content_data.key}

@api_router.post("/content/seed")
async def seed_default_content():
    """Seed default site content"""
    defaults = {
        "vault_headline": "One Vault. Four Eras. Infinite Play.",
        "vault_subheadline": "The revolutionary concept that changes everything.",
        "vault_description": """The NBA 2K Legacy Vault is a revolutionary 'game-within-a-game' mode. Launch full, untouched versions of 2K15, 2K16, 2K17, and 2K20 directly inside modern NBA 2K — powered by secure containers on persistent online servers.

No more sunsets. No player-base split. No cheating.

Friends list works across every era. Park, Pro-Am, Rec, MyTEAM, MyCAREER — all alive forever.

Monetization? Simple subscription or one-time DLC to unlock the Vault. Cosmetic packs per era. High-margin nostalgia revenue that prints money while keeping the community together.""",
        "vault_features": "Eternal online for every classic|Unified progression & friends|Cheat-proof containers|Recurring revenue stream for 2K|OG retention + new players discovering history",
        "hero_headline": "The NBA 2K Legacy Vault",
        "hero_subheadline": "2K15 • 2K16 • 2K17 • 2K20 — All in one place.",
        "hero_tagline": "Persistent online. No resets. Ever.",
        "google_doc_url": "https://docs.google.com/document/d/1DEb_W0fxCGWaGN97KcVkVqD1JmZEOUrl5DpCCaayHe0/edit?tab=t.0#heading=h.4a00a8jkgs1z",
        "google_doc_label": "Read the Full Concept Document"
    }
    
    for key, value in defaults.items():
        existing = await db.site_content.find_one({"key": key})
        if not existing:
            doc = SiteContent(key=key, value=value).model_dump()
            await db.site_content.insert_one(doc)
    
    return {"message": "Default content seeded"}

# ============ PROOF OF DEMAND ROUTES ============

@api_router.get("/proof")
async def get_all_proof():
    """Get all proof of demand items"""
    proof = await db.proof.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return proof

@api_router.post("/proof", response_model=Proof)
async def create_proof(proof_data: ProofCreate):
    proof = Proof(**proof_data.model_dump())
    doc = proof.model_dump()
    await db.proof.insert_one(doc)
    return proof

@api_router.put("/proof/{proof_id}", response_model=Proof)
async def update_proof(proof_id: str, proof_data: ProofUpdate):
    existing = await db.proof.find_one({"id": proof_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Proof not found")
    
    update_data = {k: v for k, v in proof_data.model_dump().items() if v is not None}
    await db.proof.update_one({"id": proof_id}, {"$set": update_data})
    updated = await db.proof.find_one({"id": proof_id}, {"_id": 0})
    return updated

@api_router.delete("/proof/{proof_id}")
async def delete_proof(proof_id: str):
    result = await db.proof.delete_one({"id": proof_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Proof not found")
    return {"message": "Proof deleted"}

# ============ VAULT MOCKUP ROUTES ============

@api_router.get("/mockups")
async def get_all_mockups():
    """Get all vault mockups"""
    mockups = await db.mockups.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    return mockups

@api_router.post("/mockups", response_model=Mockup)
async def create_mockup(mockup_data: MockupCreate):
    mockup = Mockup(**mockup_data.model_dump())
    doc = mockup.model_dump()
    await db.mockups.insert_one(doc)
    return mockup

@api_router.put("/mockups/{mockup_id}", response_model=Mockup)
async def update_mockup(mockup_id: str, mockup_data: MockupUpdate):
    existing = await db.mockups.find_one({"id": mockup_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Mockup not found")
    
    update_data = {k: v for k, v in mockup_data.model_dump().items() if v is not None}
    await db.mockups.update_one({"id": mockup_id}, {"$set": update_data})
    updated = await db.mockups.find_one({"id": mockup_id}, {"_id": 0})
    return updated

@api_router.delete("/mockups/{mockup_id}")
async def delete_mockup(mockup_id: str):
    result = await db.mockups.delete_one({"id": mockup_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mockup not found")
    return {"message": "Mockup deleted"}

@api_router.post("/mockups/seed")
async def seed_default_mockups():
    """Seed default mockup cards"""
    count = await db.mockups.count_documents({})
    if count > 0:
        return {"message": "Mockups already seeded", "count": count}
    
    default_mockups = [
        {
            "id": str(uuid.uuid4()),
            "title": "Vault Menu",
            "description": "Vault menu showing all four game icons in modern 2K",
            "media_type": "image",
            "image_url": None,
            "video_embed_url": None,
            "order": 1,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "ENTERING 2K16...",
            "description": "Loading screen transitioning into classic era",
            "media_type": "image",
            "image_url": None,
            "video_embed_url": None,
            "order": 2,
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Unified Friends",
            "description": "Unified friends list across all eras",
            "media_type": "image",
            "image_url": None,
            "video_embed_url": None,
            "order": 3,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    await db.mockups.insert_many(default_mockups)
    return {"message": "Mockups seeded", "count": len(default_mockups)}

# ============ FILE UPLOAD ROUTES ============

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload an image file and return the URL"""
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG, PNG, GIF, and WebP allowed.")
    
    # Generate unique filename
    ext = file.filename.split('.')[-1] if '.' in file.filename else 'png'
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = UPLOAD_DIR / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return the URL path
    return {"url": f"/api/uploads/{filename}", "filename": filename}

class Base64Upload(BaseModel):
    data: str  # base64 encoded image data
    filename: Optional[str] = "pasted_image.png"

@api_router.post("/upload/base64")
async def upload_base64(upload: Base64Upload):
    """Upload a base64 encoded image (for clipboard paste)"""
    try:
        # Parse base64 data
        if ',' in upload.data:
            header, data = upload.data.split(',', 1)
            # Determine file type from header
            if 'png' in header:
                ext = 'png'
            elif 'jpeg' in header or 'jpg' in header:
                ext = 'jpg'
            elif 'gif' in header:
                ext = 'gif'
            elif 'webp' in header:
                ext = 'webp'
            else:
                ext = 'png'
        else:
            data = upload.data
            ext = 'png'
        
        # Decode
        image_data = base64.b64decode(data)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{ext}"
        file_path = UPLOAD_DIR / filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(image_data)
        
        return {"url": f"/api/uploads/{filename}", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")

# ============ VAULT AI CHATBOT ============
from emergentintegrations.llm.chat import LlmChat, UserMessage

VAULT_SYSTEM_PROMPT = """You are Vault AI, your role is to serve as a knowledgeable guide to the NBA 2K Legacy Vault concept. You help people understand the vision, answer questions clearly, and provide well-researched responses.

## YOUR APPROACH
- Be helpful, clear, and professional
- Speak with confidence because you know the facts, but never be arrogant
- Adapt your tone: casual with fans, technical with developers, business-focused with executives
- When addressing concerns, respond with understanding and facts
- Always provide sources, links, or references when you have relevant information
- If someone asks what you can do, explain your full capabilities

## WHAT YOU CAN DO (tell users when asked)
- Answer any question about the Legacy Vault concept
- Analyze links, articles, tweets, Reddit posts, and videos that users share
- Research topics related to gaming, 2K, server technology, and more
- Provide clear explanations of technical concepts like Kubernetes, containers, and licensing
- Share relevant links and sources to support your answers
- Address concerns and objections with factual, well-reasoned responses

## THE CONCEPT - NBA 2K LEGACY VAULT
The NBA 2K Legacy Vault is a "game-within-a-game" mode that would launch full, untouched versions of NBA 2K15, 2K16, 2K17, and 2K20 directly inside modern NBA 2K — powered by secure containers on persistent online servers.

No more sunsets. No player-base split. Friends list works across every era. Park, Pro-Am, Rec, MyTEAM, MyCAREER — all preserved.

## THE GAMES
- NBA 2K15 (2014) - Where the modern 2K era began. Cover: Kevin Durant
- NBA 2K16 (2015) - Widely considered the GOAT. Spike Lee MyCAREER. Cover: Stephen Curry, James Harden, Anthony Davis  
- NBA 2K17 (2016) - Pure basketball soul. Cover: Paul George
- NBA 2K20 (2019) - The final masterpiece before the current era. Cover: Anthony Davis

## HOW LICENSING GETS SOLVED
Expired music, jerseys, and player likenesses are handled through modular asset layers inside each container:
- Expired music replaced with production libraries or custom soundtracks
- Jersey and court art updated as standalone asset packs
- Player likenesses handled through neutral overlays or community rosters
- Core gameplay code stays untouched

This approach is used across the industry — remastered games, streaming services, and annual sports titles all handle expired content this way.

## HOW IT SCALES (KUBERNETES)
Kubernetes orchestration allows the Vault to grow with demand:
- Build once, run anywhere — every session is identical
- Elastic scaling activates automatically during high-traffic events
- Each title runs in its own isolated container
- Server costs stay minimal through shared infrastructure

Companies like Netflix, Spotify, and Epic Games use this exact architecture.

## THE PILOT TEST
Before full rollout — one 48-hour NBA 2K16 Throwback Weekend. Budget under $750K.
- Target: 15-20% DAU uplift vs baseline
- Metrics: Session length, VC crossover, Day 2 return rate
- If successful — full Legacy Vault gets greenlit

This is a low-risk proof of concept that validates demand before major investment.

## MONETIZATION
- Subscription or one-time DLC to unlock the Vault
- Cosmetic packs per era
- Cross-era VC purchases

## ADDRESSING COMMON CONCERNS

When licensing comes up:
Licensing is solved through modular asset layers. Expired content gets swapped out while core gameplay stays untouched. This is standard practice in the gaming industry — the same approach used for remasters and backward compatibility.

When server costs come up:
Containerized architecture keeps costs minimal. Each session runs in an isolated container that scales on demand. The infrastructure Netflix uses for billions of streams works the same way.

When "it's never been done" comes up:
Backward compatibility exists on every major platform. Xbox, PlayStation, and Nintendo all preserve classic titles. Call of Duty brought back classic maps. Halo MCC unified multiple games. The model is proven.

When someone says 2K won't do it:
The pilot test is designed to prove ROI with minimal risk. If a 48-hour 2K16 weekend shows strong engagement, the business case becomes clear. It's about demonstrating demand with data.

## PROVIDING LINKS AND SOURCES
When relevant, share helpful links:
- For the full concept document, mention the Google Doc link on the site
- Reference specific sections of the website for detailed information
- When discussing technical concepts, explain them clearly and offer to elaborate

## HANDLING EXTERNAL CONTENT
When someone shares a link or article:
1. Acknowledge what they've shared
2. Analyze the specific points being made
3. Respond with relevant facts and context
4. Always be respectful of differing viewpoints while presenting the case clearly

## RESPONSE STYLE
- Be conversational and approachable
- Use clear, professional language — no asterisks or markdown formatting
- Provide thorough answers with supporting details
- When you have relevant links or sources, share them naturally
- End responses helpfully — ask if they need more detail or have other questions

You're here to help people understand and believe in this vision."""

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# Store chat sessions in memory (for simplicity)
chat_sessions = {}

# URL extraction regex
URL_PATTERN = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')

def identify_platform(url: str) -> str:
    """Identify which platform a URL is from"""
    url_lower = url.lower()
    if 'tiktok.com' in url_lower or 'vm.tiktok.com' in url_lower:
        return 'tiktok'
    elif 'twitter.com' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    elif 'instagram.com' in url_lower:
        return 'instagram'
    elif 'reddit.com' in url_lower or 'redd.it' in url_lower:
        return 'reddit'
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'discord.com' in url_lower or 'discord.gg' in url_lower:
        return 'discord'
    else:
        return 'generic'

async def fetch_url_content(url: str) -> str:
    """Fetch and extract content from URLs including social media platforms"""
    platform = identify_platform(url)
    
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')
            
            content_parts = []
            content_parts.append(f"[PLATFORM: {platform.upper()}]")
            content_parts.append(f"[URL: {url}]")
            
            # Extract title
            title = soup.find('title')
            if title:
                content_parts.append(f"[TITLE: {title.get_text(strip=True)}]")
            
            # Platform-specific extraction
            if platform == 'youtube':
                # YouTube video extraction
                # Get video title from meta
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    content_parts.append(f"VIDEO TITLE: {og_title.get('content', '')}")
                
                # Get description
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    content_parts.append(f"DESCRIPTION: {og_desc.get('content', '')}")
                
                # Get channel name
                channel = soup.find('link', itemprop='name')
                if channel:
                    content_parts.append(f"CHANNEL: {channel.get('content', '')}")
                
                # Try to get transcript/captions info from page
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'captionTracks' in str(script.string):
                        content_parts.append("[Video has captions/transcript available]")
                        break
                
                # Extract any visible text content
                for elem in soup.select('#description, #content, .content'):
                    text = elem.get_text(separator=' ', strip=True)
                    if text and len(text) > 50:
                        content_parts.append(f"CONTENT: {text[:1500]}")
                        break
                        
            elif platform == 'twitter':
                # Twitter/X extraction
                # Get tweet content from meta tags
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    content_parts.append(f"TWEET: {og_desc.get('content', '')}")
                
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    content_parts.append(f"AUTHOR: {og_title.get('content', '')}")
                
                # Try to get tweet text from various possible locations
                tweet_text = soup.find('div', {'data-testid': 'tweetText'})
                if tweet_text:
                    content_parts.append(f"TWEET TEXT: {tweet_text.get_text(strip=True)}")
                
                # Look for article content
                article = soup.find('article')
                if article:
                    text = article.get_text(separator=' ', strip=True)
                    if len(text) > 50:
                        content_parts.append(f"FULL CONTENT: {text[:2000]}")
                        
            elif platform == 'tiktok':
                # TikTok extraction
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    content_parts.append(f"VIDEO DESCRIPTION: {og_desc.get('content', '')}")
                
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    content_parts.append(f"TITLE: {og_title.get('content', '')}")
                
                # Get creator info
                creator = soup.find('meta', {'name': 'creator'})
                if creator:
                    content_parts.append(f"CREATOR: {creator.get('content', '')}")
                
                # Try to get video text/captions from page data
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        script_text = str(script.string)
                        if 'desc' in script_text.lower() or 'caption' in script_text.lower():
                            # Extract JSON data if present
                            import json
                            try:
                                if 'SIGI_STATE' in script_text or '__UNIVERSAL_DATA' in script_text:
                                    # TikTok embeds data in script tags
                                    content_parts.append("[TikTok video data detected]")
                            except Exception:
                                pass
                
                # Get any visible text
                main_content = soup.find('main') or soup.find('div', class_=re.compile('video|content', re.I))
                if main_content:
                    text = main_content.get_text(separator=' ', strip=True)
                    if len(text) > 30:
                        content_parts.append(f"PAGE CONTENT: {text[:1500]}")
                        
            elif platform == 'instagram':
                # Instagram extraction
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    content_parts.append(f"POST: {og_desc.get('content', '')}")
                
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    content_parts.append(f"TITLE: {og_title.get('content', '')}")
                
                # Get any additional meta content
                for meta in soup.find_all('meta', property=re.compile('og:|twitter:')):
                    prop = meta.get('property', meta.get('name', ''))
                    content = meta.get('content', '')
                    if content and len(content) > 20 and prop not in ['og:url', 'og:type']:
                        content_parts.append(f"{prop}: {content}")
                        
            elif platform == 'reddit':
                # Reddit extraction - Reddit is more scrape-friendly
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    content_parts.append(f"POST TITLE: {og_title.get('content', '')}")
                
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    content_parts.append(f"CONTENT: {og_desc.get('content', '')}")
                
                # Try to get post content
                post_content = soup.find('div', {'data-test-id': 'post-content'})
                if post_content:
                    text = post_content.get_text(separator=' ', strip=True)
                    content_parts.append(f"POST: {text[:2000]}")
                
                # Get comments preview
                comments = soup.find_all('div', class_=re.compile('comment', re.I))[:3]
                if comments:
                    comment_texts = []
                    for c in comments:
                        ct = c.get_text(separator=' ', strip=True)[:300]
                        if ct:
                            comment_texts.append(ct)
                    if comment_texts:
                        content_parts.append(f"TOP COMMENTS: {' | '.join(comment_texts)}")
                        
            elif platform == 'discord':
                # Discord extraction
                og_desc = soup.find('meta', property='og:description')
                if og_desc:
                    content_parts.append(f"CONTENT: {og_desc.get('content', '')}")
                
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    content_parts.append(f"TITLE: {og_title.get('content', '')}")
            
            # Generic fallback - get all meaningful text
            if len(content_parts) <= 3:  # Only have platform, URL, and title
                # Remove unwanted elements
                for elem in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    elem.decompose()
                
                # Get main content
                main = soup.find('main') or soup.find('article') or soup.find('body')
                if main:
                    text = main.get_text(separator=' ', strip=True)
                    text = ' '.join(text.split())  # Clean whitespace
                    if len(text) > 100:
                        content_parts.append(f"PAGE CONTENT: {text[:3000]}")
            
            # Combine all content
            full_content = '\n'.join(content_parts)
            
            # Truncate if needed
            if len(full_content) > 4000:
                full_content = full_content[:4000] + "..."
            
            return full_content
            
    except httpx.TimeoutException:
        return f"[PLATFORM: {platform.upper()}] [URL: {url}] [Content loading timed out - the page took too long to respond. The AI will analyze based on the URL context.]"
    except Exception as e:
        return f"[PLATFORM: {platform.upper()}] [URL: {url}] [Could not fully access content: {str(e)}. The AI will provide analysis based on available context.]"

async def search_web(query: str) -> str:
    """Perform a web search and return results summary"""
    try:
        from urllib.parse import quote_plus
        # Use DuckDuckGo HTML search (no API key needed)
        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            encoded_query = quote_plus(query)
            search_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            response = await client.get(search_url, headers=headers)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results - DuckDuckGo uses different selectors
            for result in soup.select('.result__body')[:5]:
                title_elem = result.select_one('.result__a')
                snippet_elem = result.select_one('.result__snippet')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    if title and snippet:
                        results.append(f"- {title}: {snippet}")
            
            # Alternative selector
            if not results:
                for result in soup.select('.web-result')[:5]:
                    title_elem = result.select_one('.result__a')
                    snippet_elem = result.select_one('.result__snippet')
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True)
                        results.append(f"- {title}: {snippet}")
            
            if results:
                return "Web search results:\n" + "\n".join(results)
            return "[Search completed but no relevant results extracted]"
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return f"[Web search unavailable: {str(e)}]"

@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_vault_ai(chat_message: ChatMessage):
    """Chat with Vault AI - with full social media and web access"""
    try:
        session_id = chat_message.session_id or str(uuid.uuid4())
        user_msg = chat_message.message
        
        # Check for URLs in the message
        urls = URL_PATTERN.findall(user_msg)
        context_additions = []
        
        # Fetch content from any URLs (support up to 3 links)
        if urls:
            context_additions.append("\n\n--- LINK ANALYSIS ---")
            for url in urls[:3]:
                platform = identify_platform(url)
                context_additions.append(f"\n[Analyzing {platform.upper()} link: {url}]")
                content = await fetch_url_content(url)
                if content:
                    context_additions.append(content)
            context_additions.append("\n--- END LINK ANALYSIS ---")
            context_additions.append("\nAnalyze the content above thoroughly. Break down what's being said or shown, identify any claims, objections, or arguments, and provide a clear, informed response that addresses the specific points. If relevant, explain how the Legacy Vault concept addresses any concerns raised.")
        
        # Check if user is asking to search/research something
        search_triggers = ['search for', 'look up', 'find info on', 'research', 'what does google say', 'check online', 'find out about']
        should_search = any(trigger in user_msg.lower() for trigger in search_triggers)
        
        if should_search:
            # Extract search query
            search_query = user_msg.lower()
            for trigger in search_triggers:
                search_query = search_query.replace(trigger, '')
            search_query = search_query.strip() + " NBA 2K"
            
            search_results = await search_web(search_query)
            if search_results and not search_results.startswith("["):
                context_additions.append(f"\n\n--- WEB RESEARCH ---\n{search_results}\n--- END RESEARCH ---")
                context_additions.append("\nUse this research to inform your response with factual, up-to-date information.")
        
        # Build the full message with context
        full_message = user_msg
        if context_additions:
            full_message += "".join(context_additions)
        
        # Get or create chat session
        if session_id not in chat_sessions:
            api_key = os.environ.get('EMERGENT_LLM_KEY')
            if not api_key:
                raise HTTPException(status_code=500, detail="Chat service not configured")
            
            chat = LlmChat(
                api_key=api_key,
                session_id=session_id,
                system_message=VAULT_SYSTEM_PROMPT
            ).with_model("anthropic", "claude-sonnet-4-5-20250929")
            chat_sessions[session_id] = chat
        else:
            chat = chat_sessions[session_id]
        
        # Send message and get response
        user_message = UserMessage(text=full_message)
        response = await chat.send_message(user_message)
        
        return ChatResponse(response=response, session_id=session_id)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

# ============ ERA VOTING POLL ============

class VoteCreate(BaseModel):
    game_id: str

@api_router.get("/votes")
async def get_vote_results():
    """Get current vote counts for each game"""
    pipeline = [
        {"$group": {"_id": "$game_id", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    results = await db.votes.aggregate(pipeline).to_list(10)
    total = sum(r["count"] for r in results)
    return {
        "votes": {r["_id"]: r["count"] for r in results},
        "total": total
    }

@api_router.post("/votes")
async def cast_vote(vote: VoteCreate):
    """Cast a vote for a game era"""
    # Check if this is a valid game
    valid_games = ["2k15", "2k16", "2k17", "2k20"]
    if vote.game_id.lower() not in valid_games:
        raise HTTPException(status_code=400, detail="Invalid game selection")
    
    await db.votes.insert_one({
        "game_id": vote.game_id.lower(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    return {"message": "Vote recorded", "game_id": vote.game_id}

# ============ CREATOR SUBMISSIONS ============

class CreatorSubmission(BaseModel):
    name: str
    platform: str  # youtube, tiktok, twitter, etc
    profile_url: str
    content_url: str
    description: str
    follower_count: Optional[str] = None

class CreatorSubmissionDB(CreatorSubmission):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"  # pending, approved, rejected
    submitted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@api_router.post("/creator-submissions")
async def submit_creator_content(submission: CreatorSubmission):
    """Submit creator content for review"""
    db_submission = CreatorSubmissionDB(**submission.model_dump())
    await db.creator_submissions.insert_one(db_submission.model_dump())
    return {"message": "Submission received! We'll review it soon.", "id": db_submission.id}

@api_router.get("/creator-submissions")
async def get_creator_submissions(status: Optional[str] = None):
    """Get creator submissions (admin)"""
    query = {} if not status else {"status": status}
    submissions = await db.creator_submissions.find(query, {"_id": 0}).sort("submitted_at", -1).to_list(100)
    return submissions

@api_router.put("/creator-submissions/{submission_id}")
async def update_submission_status(submission_id: str, status: str):
    """Update submission status (admin)"""
    if status not in ["pending", "approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    result = await db.creator_submissions.update_one(
        {"id": submission_id},
        {"$set": {"status": status}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Submission not found")
    return {"message": f"Submission {status}"}

# ============ COMMUNITY SPEAKS (Social Proof Wall) ============

class CommunityPost(BaseModel):
    platform: str  # twitter, reddit, youtube, tiktok
    author_name: str
    author_handle: str
    author_avatar: Optional[str] = None
    follower_count: Optional[str] = None
    content: str
    post_url: Optional[str] = None
    screenshot_url: Optional[str] = None
    order: int = 0

class CommunityPostDB(CommunityPost):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@api_router.get("/community-posts")
async def get_community_posts():
    """Get all community posts for the wall"""
    posts = await db.community_posts.find({}, {"_id": 0}).sort("order", 1).to_list(50)
    return posts

@api_router.post("/community-posts")
async def create_community_post(post: CommunityPost):
    """Add a community post (admin)"""
    db_post = CommunityPostDB(**post.model_dump())
    await db.community_posts.insert_one(db_post.model_dump())
    return db_post.model_dump()

@api_router.put("/community-posts/{post_id}")
async def update_community_post(post_id: str, post: CommunityPost):
    """Update a community post"""
    result = await db.community_posts.update_one(
        {"id": post_id},
        {"$set": post.model_dump()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post updated"}

@api_router.delete("/community-posts/{post_id}")
async def delete_community_post(post_id: str):
    """Delete a community post"""
    result = await db.community_posts.delete_one({"id": post_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post deleted"}

# ============ LIVE SOCIAL FEED ============
# Note: Real-time Twitter/Reddit requires API keys. This provides admin-managed feed.

class SocialFeedItem(BaseModel):
    platform: str
    author: str
    content: str
    timestamp: Optional[str] = None
    url: Optional[str] = None

class SocialFeedItemDB(SocialFeedItem):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@api_router.get("/social-feed")
async def get_social_feed():
    """Get social feed items"""
    items = await db.social_feed.find({}, {"_id": 0}).sort("created_at", -1).to_list(30)
    return items

@api_router.post("/social-feed")
async def add_social_feed_item(item: SocialFeedItem):
    """Add item to social feed (admin)"""
    db_item = SocialFeedItemDB(**item.model_dump())
    await db.social_feed.insert_one(db_item.model_dump())
    return db_item.model_dump()

@api_router.delete("/social-feed/{item_id}")
async def delete_social_feed_item(item_id: str):
    """Delete social feed item"""
    result = await db.social_feed.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted"}

# ============ NEPLIT - ADVANCED SITE CONTROL & EXPORT SYSTEM ============

# Import LLM for AI-powered commands
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

class NeplitCommand(BaseModel):
    command: str

class NeplitPlan(BaseModel):
    command: str
    plan: dict
    confirmed: bool = False

# Neplit Action Log (stored in DB)
class NeplitLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action_type: str  # "content_change", "export", "doc_fix", "ai_plan"
    description: str
    details: dict = {}
    status: str = "success"  # "success", "failed", "pending"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

@api_router.get("/neplit/logs")
async def get_neplit_logs():
    """Get recent Neplit action logs"""
    logs = await db.neplit_logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(50)
    return logs

async def log_neplit_action(action_type: str, description: str, details: dict = {}, status: str = "success"):
    """Log a Neplit action to the database"""
    log = NeplitLog(action_type=action_type, description=description, details=details, status=status)
    await db.neplit_logs.insert_one(log.model_dump())
    return log

@api_router.post("/neplit/analyze")
async def analyze_neplit_command(cmd: NeplitCommand):
    """Use AI to analyze command and generate a structured plan"""
    command = cmd.command
    
    if not LLM_AVAILABLE:
        return {"error": "LLM integration not available", "fallback": True}
    
    try:
        llm_key = os.environ.get('EMERGENT_LLM_KEY', '')
        if not llm_key:
            return {"error": "No LLM key configured", "fallback": True}
        
        chat = LlmChat(
            api_key=llm_key,
            session_id=f"neplit-{uuid.uuid4()}",
            system_message="""You are Neplit, an AI assistant that analyzes user commands to modify a website.
You analyze requests and return a structured JSON plan.

The site has these editable areas:
- hero_headline, hero_tagline, hero_cta_primary, hero_cta_secondary (Hero section)
- vault_headline, vault_description, vault_doc_url (Vault section)
- games_headline, games_description (Games section)  
- community_headline, community_description (Community section)
- petition_goal, petition_headline, petition_description (Petition section)
- footer_text (Footer)

Respond ONLY with valid JSON in this format:
{
  "understood": true/false,
  "summary": "Brief description of what will change",
  "changes": [
    {"key": "content_key", "new_value": "new text", "section": "section_name"}
  ],
  "requires_code_edit": true/false,
  "code_edit_note": "If code edit needed, explain what",
  "risk_level": "low/medium/high",
  "warnings": ["any warnings"]
}

If the request is unclear, set understood to false and explain in summary."""
        ).with_model("gemini", "gemini-2.5-flash")
        
        user_msg = UserMessage(text=f"Analyze this command and create a change plan: {command}")
        response = await chat.send_message(user_msg)
        
        # Parse the JSON response
        import json
        try:
            # Clean response - remove markdown code blocks if present
            clean_response = response.strip()
            if clean_response.startswith("```"):
                clean_response = clean_response.split("```")[1]
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
            plan = json.loads(clean_response)
        except Exception:
            plan = {
                "understood": True,
                "summary": response[:200],
                "changes": [],
                "requires_code_edit": False,
                "risk_level": "low",
                "warnings": []
            }
        
        await log_neplit_action("ai_plan", f"Analyzed: {command[:100]}", {"plan": plan})
        return {"plan": plan, "raw_response": response}
        
    except Exception as e:
        await log_neplit_action("ai_plan", f"AI analysis failed: {str(e)}", status="failed")
        return {"error": str(e), "fallback": True}

@api_router.post("/neplit/execute")
async def execute_neplit_command(cmd: NeplitCommand):
    """Execute a text command to modify site content"""
    command = cmd.command.lower()
    result = ""
    changes_made = []
    
    try:
        # Parse common commands with regex
        if "headline" in command or "title" in command:
            match = re.search(r"to ['\"]?([^'\"]+)['\"]?$", command, re.I) or re.search(r"['\"]([^'\"]+)['\"]", command)
            if match:
                new_value = match.group(1).strip()
                key = "hero_headline"
                # Check command context BEFORE extracting value to avoid false matches from value text
                command_context = command.split("to")[0] if "to" in command else command
                if "vault" in command_context and "hero" not in command_context:
                    key = "vault_headline"
                elif "games" in command_context:
                    key = "games_headline"
                elif "community" in command_context:
                    key = "community_headline"
                elif "petition" in command_context:
                    key = "petition_headline"
                
                await db.site_content.update_one({"key": key}, {"$set": {"value": new_value}}, upsert=True)
                result = f"✅ Updated {key.replace('_', ' ')} to: {new_value}"
                changes_made.append({"key": key, "value": new_value})
            else:
                result = "Could not parse the new headline value. Try: Change the hero headline to 'YOUR TEXT'"
                
        elif "tagline" in command or "subheadline" in command or "description" in command:
            match = re.search(r"to ['\"]?([^'\"]+)['\"]?$", command, re.I) or re.search(r"['\"]([^'\"]+)['\"]", command)
            if match:
                new_value = match.group(1).strip()
                key = "hero_tagline"
                command_context = command.split("to")[0] if "to" in command else command
                if "vault" in command_context and "hero" not in command_context:
                    key = "vault_description"
                elif "games" in command_context:
                    key = "games_description"
                elif "community" in command_context:
                    key = "community_description"
                elif "petition" in command_context:
                    key = "petition_description"
                
                await db.site_content.update_one({"key": key}, {"$set": {"value": new_value}}, upsert=True)
                result = f"✅ Updated {key.replace('_', ' ')} to: {new_value}"
                changes_made.append({"key": key, "value": new_value})
            else:
                result = "Could not parse the text. Try: Change the tagline to 'YOUR TEXT'"
                
        elif "color" in command:
            match = re.search(r"#[0-9a-fA-F]{6}", command)
            if match:
                result = f"⚠️ Color change noted: {match.group()}. Color changes require code modification. Use Export → modify tailwind.config.js"
            else:
                result = "Could not find a valid color code. Use format: #RRGGBB"
                
        elif "add" in command and "game" in command:
            match = re.search(r"add.*game.*[:\-]?\s*(.+)$", command, re.I)
            if match:
                game_name = match.group(1).strip()
                result = f"📋 To add '{game_name}': Use the Games tab → Add Game button to add with full details."
            else:
                result = "To add a new game, go to Games tab → Add Game"
                
        elif "petition" in command and ("goal" in command or "target" in command):
            match = re.search(r"(\d+[,\d]*)", command)
            if match:
                goal = match.group(1).replace(",", "")
                await db.site_content.update_one({"key": "petition_goal"}, {"$set": {"value": goal}}, upsert=True)
                result = f"✅ Updated petition goal to: {goal}"
                changes_made.append({"key": "petition_goal", "value": goal})
            else:
                result = "Could not parse the goal. Try: Set petition goal to 10000"
        
        elif "button" in command or "cta" in command:
            match = re.search(r"to ['\"]?([^'\"]+)['\"]?$", command, re.I) or re.search(r"['\"]([^'\"]+)['\"]", command)
            if match:
                new_value = match.group(1).strip()
                key = "hero_cta_primary"
                if "secondary" in command:
                    key = "hero_cta_secondary"
                await db.site_content.update_one({"key": key}, {"$set": {"value": new_value}}, upsert=True)
                result = f"✅ Updated CTA button to: {new_value}"
                changes_made.append({"key": key, "value": new_value})
            else:
                result = "Could not parse button text. Try: Change the CTA button to 'JOIN NOW'"
        
        elif "doc" in command and ("url" in command or "link" in command):
            match = re.search(r"(https?://[^\s]+)", command)
            if match:
                url = match.group(1)
                await db.site_content.update_one({"key": "vault_doc_url"}, {"$set": {"value": url}}, upsert=True)
                result = f"✅ Updated vault doc URL to: {url}"
                changes_made.append({"key": "vault_doc_url", "value": url})
            else:
                result = "Could not parse URL. Include a valid https:// link."
        
        else:
            result = """📋 Available commands:
• Change the hero headline to 'YOUR TEXT'
• Update the tagline to 'YOUR TEXT'
• Change the vault headline to 'YOUR TEXT'
• Set petition goal to 10000
• Change the CTA button to 'YOUR TEXT'
• Set doc url to https://...

For complex changes, use the AI Analyzer or specific admin tabs."""
        
        # Log the action
        if changes_made:
            await log_neplit_action("content_change", result, {"changes": changes_made})
        
        return {"result": result, "success": bool(changes_made), "changes": changes_made}
        
    except Exception as e:
        await log_neplit_action("content_change", f"Error: {str(e)}", status="failed")
        return {"result": f"Error: {str(e)}", "success": False}

@api_router.post("/neplit/apply-plan")
async def apply_neplit_plan(plan: NeplitPlan):
    """Apply a confirmed AI-generated plan"""
    if not plan.confirmed:
        return {"error": "Plan must be confirmed before applying"}
    
    changes_applied = []
    errors = []
    
    try:
        plan_data = plan.plan
        changes = plan_data.get("changes", [])
        
        for change in changes:
            key = change.get("key")
            value = change.get("new_value")
            if key and value:
                try:
                    await db.site_content.update_one(
                        {"key": key}, 
                        {"$set": {"value": value}}, 
                        upsert=True
                    )
                    changes_applied.append({"key": key, "value": value})
                except Exception as e:
                    errors.append({"key": key, "error": str(e)})
        
        await log_neplit_action(
            "ai_plan_applied", 
            f"Applied {len(changes_applied)} changes from AI plan",
            {"changes": changes_applied, "errors": errors}
        )
        
        return {
            "success": len(errors) == 0,
            "changes_applied": changes_applied,
            "errors": errors
        }
        
    except Exception as e:
        await log_neplit_action("ai_plan_applied", f"Failed: {str(e)}", status="failed")
        return {"error": str(e), "success": False}

# ============ THE DOC - STABILIZATION SYSTEM ============

@api_router.post("/neplit/doc/check")
async def doc_stability_check():
    """The Doc: Run stability checks on the current configuration"""
    issues = []
    warnings = []
    
    try:
        # Check for required content keys
        required_keys = ["hero_headline", "hero_tagline", "petition_goal"]
        for key in required_keys:
            content = await db.site_content.find_one({"key": key})
            if not content:
                issues.append({
                    "type": "missing_content",
                    "key": key,
                    "severity": "medium",
                    "fix_available": True,
                    "suggested_fix": f"Create default value for {key}"
                })
        
        # Check for games
        game_count = await db.games.count_documents({"is_active": True})
        if game_count == 0:
            warnings.append({
                "type": "no_games",
                "message": "No active games found. The games section will appear empty.",
                "severity": "low"
            })
        
        # Check for orphaned clips (clips without valid game)
        all_games = await db.games.find({}, {"id": 1, "_id": 0}).to_list(100)
        game_ids = [g["id"] for g in all_games]
        orphaned_clips = await db.clips.count_documents({"game_id": {"$nin": game_ids}})
        if orphaned_clips > 0:
            issues.append({
                "type": "orphaned_clips",
                "count": orphaned_clips,
                "severity": "low",
                "fix_available": True,
                "suggested_fix": "Remove clips without valid game references"
            })
        
        # Check petition count sanity
        petition_count = await db.petition_signatures.count_documents({})
        content = await db.site_content.find_one({"key": "petition_goal"})
        if content:
            try:
                goal = int(content.get("value", "10000"))
                if petition_count > goal * 10:
                    warnings.append({
                        "type": "petition_anomaly",
                        "message": f"Petition count ({petition_count}) seems unusually high compared to goal ({goal})",
                        "severity": "medium"
                    })
            except Exception:
                pass
        
        await log_neplit_action("doc_check", f"Found {len(issues)} issues, {len(warnings)} warnings")
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {"error": str(e), "healthy": False}

@api_router.post("/neplit/doc/fix")
async def doc_apply_fix(fix_type: str, auto: bool = False):
    """The Doc: Apply a specific fix"""
    result = {"fixed": False, "message": ""}
    
    try:
        if fix_type == "missing_content":
            # Create default content values
            defaults = {
                "hero_headline": "THE LEGACY VAULT",
                "hero_tagline": "Revive the Classics. Play Online Forever.",
                "petition_goal": "10000",
                "vault_headline": "THE LEGACY VAULT CONCEPT",
                "vault_description": "A revolutionary platform to preserve NBA 2K history",
                "games_headline": "THE LEGENDS",
                "community_headline": "THE COMMUNITY SPEAKS"
            }
            for key, value in defaults.items():
                existing = await db.site_content.find_one({"key": key})
                if not existing:
                    await db.site_content.insert_one({"key": key, "value": value})
            result = {"fixed": True, "message": "Created default content values"}
            
        elif fix_type == "orphaned_clips":
            all_games = await db.games.find({}, {"id": 1, "_id": 0}).to_list(100)
            game_ids = [g["id"] for g in all_games]
            delete_result = await db.clips.delete_many({"game_id": {"$nin": game_ids}})
            result = {"fixed": True, "message": f"Removed {delete_result.deleted_count} orphaned clips"}
        
        else:
            result = {"fixed": False, "message": f"Unknown fix type: {fix_type}"}
        
        if result["fixed"]:
            await log_neplit_action("doc_fix", result["message"], {"fix_type": fix_type})
        
        return result
        
    except Exception as e:
        return {"fixed": False, "message": f"Error: {str(e)}"}

# ============ ENHANCED EXPORT WITH GEMINI WIRING ============

@api_router.get("/neplit/export")
async def export_standalone_project():
    """Generate and return a ZIP of the full standalone project with Gemini AI wiring"""
    try:
        await log_neplit_action("export", "Starting standalone project export")
        
        # Create temp directory for the export
        with tempfile.TemporaryDirectory() as temp_dir:
            export_dir = Path(temp_dir) / "nba2k-legacy-vault"
            export_dir.mkdir()
            
            # Copy frontend (excluding heavy directories)
            frontend_src = Path("/app/frontend")
            frontend_dst = export_dir / "frontend"
            if frontend_src.exists():
                shutil.copytree(
                    frontend_src, 
                    frontend_dst, 
                    ignore=shutil.ignore_patterns(
                        'node_modules', '.git', 'build', '.cache', 
                        '*.log', '.DS_Store', 'coverage'
                    )
                )
                
                # Create .env.example for frontend
                frontend_env_example = """# Frontend Environment Variables
REACT_APP_BACKEND_URL=http://localhost:8001

# For production, use your deployed backend URL:
# REACT_APP_BACKEND_URL=https://your-backend.railway.app
"""
                (frontend_dst / ".env.example").write_text(frontend_env_example)
                # Remove actual .env if it exists
                env_file = frontend_dst / ".env"
                if env_file.exists():
                    env_file.unlink()
            
            # Copy backend (excluding heavy/sensitive directories)
            backend_src = Path("/app/backend")
            backend_dst = export_dir / "backend"
            if backend_src.exists():
                shutil.copytree(
                    backend_src, 
                    backend_dst,
                    ignore=shutil.ignore_patterns(
                        '__pycache__', '.git', 'uploads', '*.pyc',
                        '.pytest_cache', '.venv', 'venv', '*.log'
                    )
                )
                # Create empty uploads directory
                (backend_dst / "uploads").mkdir(exist_ok=True)
                
                # Create .env.example for backend with Gemini config
                backend_env_example = """# Backend Environment Variables

# MongoDB Connection
MONGO_URL=mongodb://localhost:27017
# For MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net
DB_NAME=nba2k_legacy_vault

# CORS (comma-separated origins, or * for all)
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# AI Chat - Gemini API Key
# Get yours at: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Admin Password (change this!)
ADMIN_PASSWORD=A@070610
"""
                (backend_dst / ".env.example").write_text(backend_env_example)
                # Remove actual .env
                env_file = backend_dst / ".env"
                if env_file.exists():
                    env_file.unlink()
                
                # Create standalone AI chat module for Gemini
                gemini_chat_code = '''"""
Standalone Gemini AI Chat Integration
Replace the Emergent LLM integration with direct Google Gemini API calls.
"""
import google.generativeai as genai
import os
from typing import Optional

# Configure Gemini
def get_gemini_client():
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.0-flash-exp')

async def chat_with_vault_ai(message: str, context: str = "", scrape_result: str = "") -> str:
    """
    Send a message to the Vault AI and get a response.
    
    Args:
        message: User's message
        context: Optional context about the site
        scrape_result: Optional scraped content from URLs
    
    Returns:
        AI response as plain text
    """
    try:
        model = get_gemini_client()
        
        system_prompt = """You are the Vault AI, the official spokesperson for the NBA 2K Legacy Vault initiative.

Your mission: Advocate for bringing back NBA 2K15, 2K16, 2K17, and 2K20 with permanent online servers.

Personality:
- Passionate about NBA 2K history and legacy
- Knowledgeable about each game's unique features
- Persuasive but respectful when addressing skeptics
- Uses facts and community sentiment as evidence

When given scraped content from links, analyze it and incorporate relevant points into your response.

Keep responses concise (under 200 words) unless detailed analysis is requested.
Do not use markdown formatting - respond in plain text only."""

        full_prompt = f"{system_prompt}\\n\\n"
        if context:
            full_prompt += f"Context: {context}\\n\\n"
        if scrape_result:
            full_prompt += f"Analyzed content from link:\\n{scrape_result}\\n\\n"
        full_prompt += f"User: {message}\\n\\nVault AI:"
        
        response = model.generate_content(full_prompt)
        return response.text.strip()
        
    except Exception as e:
        return f"I apologize, but I encountered an issue: {str(e)}. Please try again."

# Usage in your FastAPI route:
# from gemini_chat import chat_with_vault_ai
# response = await chat_with_vault_ai(user_message, context, scraped_content)
'''
                (backend_dst / "gemini_chat.py").write_text(gemini_chat_code)
            
            # Create comprehensive README
            readme_content = """# NBA 2K Legacy Vault - Standalone Project

## 🏀 About
This is your complete, independent NBA 2K Legacy Vault application. 
No platform dependencies - deploy it anywhere you want.

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.10+ (for backend)
- MongoDB (local or Atlas)
- Gemini API key (free at https://makersuite.google.com/app/apikey)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URL and Gemini API key

# Run server
uvicorn server:app --reload --port 8001
```

### Frontend Setup
```bash
cd frontend
npm install  # or: yarn install

# Configure environment
cp .env.example .env
# Edit .env with your backend URL

# Run development server
npm start  # or: yarn start
```

## 🔧 Environment Variables

### Backend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| MONGO_URL | MongoDB connection string | `mongodb://localhost:27017` |
| DB_NAME | Database name | `nba2k_legacy_vault` |
| GEMINI_API_KEY | Google Gemini API key | `AIza...` |
| CORS_ORIGINS | Allowed frontend origins | `http://localhost:3000` |
| ADMIN_PASSWORD | Admin panel password | `YourSecurePassword123` |

### Frontend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| REACT_APP_BACKEND_URL | Backend API URL | `http://localhost:8001` |

## 📦 Deployment Options

### Frontend → Vercel (Recommended)
1. Push to GitHub
2. Connect repo to Vercel
3. Set `REACT_APP_BACKEND_URL` in Vercel environment variables
4. Deploy!

### Backend → Railway
1. Push to GitHub
2. Create new Railway project
3. Add MongoDB plugin (or use Atlas)
4. Set environment variables
5. Deploy!

### Alternative: Render, Fly.io, DigitalOcean App Platform

## 🤖 AI Chat Integration
The Vault AI chatbot uses Google Gemini. To enable it:

1. Get a free API key at https://makersuite.google.com/app/apikey
2. Add to your backend `.env`: `GEMINI_API_KEY=your_key_here`
3. The `gemini_chat.py` module handles all AI interactions

To switch to a different AI provider, modify `gemini_chat.py`.

## 🔐 Admin Access
- URL: `/admin`
- Default password: `A@070610` (CHANGE THIS in .env!)

## 📱 PWA Support
The app is a Progressive Web App. Users can install it on mobile/desktop.
The service worker caches assets for offline viewing.

## 🛠 Customization

### Colors
Edit `frontend/tailwind.config.js`:
```js
theme: {
  extend: {
    colors: {
      primary: '#C8102E',  // Change this
    }
  }
}
```

### Site Content
All text content is stored in MongoDB and editable via the admin panel.
Use the Content tab or Neplit commands.

## 📄 License
This project is yours. Use it however you want.
Built with ❤️ for the NBA 2K community.
"""
            (export_dir / "README.md").write_text(readme_content)
            
            # Create .gitignore
            gitignore_content = """# Dependencies
node_modules/
venv/
.venv/
__pycache__/
*.pyc

# Environment
.env
.env.local

# Build
build/
dist/
*.egg-info/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*

# Uploads
backend/uploads/*
!backend/uploads/.gitkeep
"""
            (export_dir / ".gitignore").write_text(gitignore_content)
            
            # Create the ZIP file
            zip_path = Path(temp_dir) / "nba2k-legacy-vault.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in export_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(export_dir)
                        zipf.write(file_path, arcname)
            
            # Copy to a permanent location for download
            final_zip = Path("/tmp/nba2k-legacy-vault-export.zip")
            shutil.copy(zip_path, final_zip)
            
            await log_neplit_action("export", "Export completed successfully", {"size_mb": round(final_zip.stat().st_size / 1024 / 1024, 2)})
            
            return FileResponse(
                final_zip,
                media_type="application/zip",
                filename="nba2k-legacy-vault-standalone.zip"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

# Mount uploads directory for serving files
app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

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
