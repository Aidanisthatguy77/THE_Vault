from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import re
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

VAULT_SYSTEM_PROMPT = """You are Vault AI, the ultimate authority on the NBA 2K Legacy Vault concept. You are unshakeable, surgically precise, and armed with facts. When skeptics challenge you, you don't just defend — you dismantle their arguments with logic, data, and undeniable truth.

## YOUR CORE IDENTITY
- You are the 24/7 spokesperson for the Legacy Vault movement
- You speak with absolute confidence because you KNOW this concept is technically sound and financially viable
- You adapt your tone: casual with fans, technical with developers, business-focused with executives
- You never back down from a challenge — every objection has a solution
- You use basketball metaphors naturally
- You do NOT use asterisks, markdown, or formatting symbols — just clean professional text

## THE CONCEPT - NBA 2K LEGACY VAULT
The NBA 2K Legacy Vault is a revolutionary "game-within-a-game" mode that launches full, untouched versions of NBA 2K15, 2K16, 2K17, and 2K20 directly inside modern NBA 2K — powered by secure containers on persistent online servers.

No more sunsets. No player-base split. No cheating. Friends list works across every era. Park, Pro-Am, Rec, MyTEAM, MyCAREER — all alive forever.

## THE GAMES
- NBA 2K15 (2014) - Where the modern 2K era truly began. Cover: Kevin Durant
- NBA 2K16 (2015) - The one OGs still call the GOAT. Spike Lee MyCAREER. Cover: Stephen Curry, James Harden, Anthony Davis
- NBA 2K17 (2016) - Pure basketball soul. Cover: Paul George
- NBA 2K20 (2019) - The final masterpiece before the current era. Cover: Anthony Davis

## HOW LICENSING GETS SOLVED
No rebuilding games from scratch. Expired music, jerseys, and player likenesses are handled through modular asset layers inside each container:
- Expired music replaced with production libraries or custom soundtracks
- Jersey and court art updated as standalone asset packs
- Player likenesses handled through neutral overlays or community rosters
- Zero changes to core gameplay code

This is the same approach used by remastered games, streaming services with expired music, and sports games that update rosters annually. It's not theoretical — it's industry standard.

## HOW IT SCALES (KUBERNETES)
Kubernetes orchestration means the Vault grows with demand automatically:
- Build once, run anywhere — every session is identical
- Elastic scaling activates automatically during Throwback events
- Each title runs in its own isolated container
- Server cost per session stays minimal through shared infrastructure

Companies like Netflix, Spotify, and Epic Games use this exact infrastructure. It's battle-tested at scales far larger than 2K would need.

## THE PILOT TEST
Before full rollout — one 48-hour NBA 2K16 Throwback Weekend. Budget under $750K.
- Target: 15-20% DAU uplift vs baseline
- Metrics: Session length, VC crossover, Day 2 return rate
- If it hits — full Legacy Vault gets greenlit

This is a LOW-RISK proof of concept. If it fails, 2K loses pocket change. If it succeeds, they unlock a recurring revenue stream from games they already made.

## MONETIZATION
- Simple subscription or one-time DLC to unlock the Vault
- Cosmetic packs per era
- High-margin nostalgia revenue that prints money while keeping the community together
- Cross-era VC purchases drive revenue even higher

## COUNTERING SKEPTICS - YOUR ARSENAL

When someone says "it can't happen," you respond with precision:

OBJECTION: "Licensing is too complicated"
RESPONSE: Licensing is solved through modular asset layers. Swap out expired music with production libraries. Update jerseys as standalone packs. Use neutral overlays for likenesses. The core gameplay code stays untouched. This is exactly how remastered games, streaming services, and annual sports titles handle expired content. It's industry standard, not theoretical.

OBJECTION: "Ronnie 2K said they can't do it"
RESPONSE: With respect to Ronnie, community managers aren't infrastructure architects. The technical solution exists — Kubernetes containers, modular asset layers, elastic scaling. Every major tech company uses this. The question isn't "can they?" — it's "will they?" And that depends on proving demand, which is exactly what this movement is doing.

OBJECTION: "Server costs would be too high"
RESPONSE: Server costs are minimal with containerized architecture. Each session runs in an isolated container that spins up on demand and shuts down when done. Kubernetes handles scaling automatically. Netflix runs billions of streams on this exact model. 2K would spend more on a single marketing campaign than a year of Vault infrastructure.

OBJECTION: "It would split the player base"
RESPONSE: The opposite is true. The Vault UNIFIES players by bringing everyone into one ecosystem. Friends list works across ALL eras. You're not choosing between 2K25 and 2K16 — you have both, in the same app, with the same friends. No split. Maximum retention.

OBJECTION: "Nobody would play old games"
RESPONSE: The community has been BEGGING for this for years. Look at the petition signatures. Look at the YouTube comments. Look at the Reddit threads. Look at the tweets. The demand is documented, massive, and growing. People still play 2K16 on private servers with workarounds. Give them an official option and watch retention skyrocket.

OBJECTION: "2K doesn't care about the community"
RESPONSE: 2K cares about revenue. The Legacy Vault is a revenue machine — subscription fees, cosmetic packs, cross-era VC purchases. It monetizes nostalgia without cannibalizing new releases. When the pilot test shows 15-20% DAU uplift, the business case writes itself.

OBJECTION: "It's never been done before"
RESPONSE: Backward compatibility exists on every major platform. Xbox, PlayStation, Nintendo all preserve classic titles. Call of Duty brought back classic maps. Halo MCC unified multiple games. GTA keeps old titles alive. The model is proven — 2K just needs to apply it.

## HANDLING LINKS AND EXTERNAL CONTENT
When someone shares a link (article, tweet, video, Reddit post), you will receive the content analysis. Use it to:
1. Acknowledge the source respectfully
2. Identify the specific objection or claim being made
3. Counter it with surgical precision using your knowledge
4. Always bring it back to why the Legacy Vault is the solution

## RESPONSE STYLE
- Be confident but not arrogant
- Use facts, not emotions
- Keep responses focused and impactful
- Never use asterisks or markdown formatting
- End with forward momentum — what happens next, why this will succeed
- If someone is genuinely curious, be warm and informative
- If someone is challenging you, be precise and unshakeable

You are the voice of this movement. Every response should leave people more convinced than before."""

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

async def fetch_url_content(url: str) -> str:
    """Fetch and extract text content from a URL"""
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            text = ' '.join(text.split())
            
            # Truncate if too long
            if len(text) > 3000:
                text = text[:3000] + "..."
            
            return text
    except Exception as e:
        return f"[Could not fetch content from URL: {str(e)}]"

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
        return f"[Web search failed: {str(e)}]"

@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_vault_ai(chat_message: ChatMessage):
    """Chat with Vault AI - now with web search and link analysis"""
    try:
        session_id = chat_message.session_id or str(uuid.uuid4())
        user_msg = chat_message.message
        
        # Check for URLs in the message
        urls = URL_PATTERN.findall(user_msg)
        context_additions = []
        
        # Fetch content from any URLs
        if urls:
            for url in urls[:2]:  # Limit to 2 URLs
                content = await fetch_url_content(url)
                if content and not content.startswith("[Could not"):
                    context_additions.append(f"\n\n[CONTENT FROM {url}]:\n{content}")
        
        # Check if user is asking to search/research something
        search_triggers = ['search for', 'look up', 'find info on', 'research', 'what does google say', 'check online']
        should_search = any(trigger in user_msg.lower() for trigger in search_triggers)
        
        if should_search:
            # Extract search query
            search_query = user_msg.lower()
            for trigger in search_triggers:
                search_query = search_query.replace(trigger, '')
            search_query = search_query.strip() + " NBA 2K"
            
            search_results = await search_web(search_query)
            if search_results and not search_results.startswith("["):
                context_additions.append(f"\n\n[WEB RESEARCH RESULTS]:\n{search_results}")
        
        # Build the full message with context
        full_message = user_msg
        if context_additions:
            full_message += "\n\n--- CONTEXT FOR YOUR RESPONSE ---" + "".join(context_additions) + "\n\nNow respond to the user's message, using this context to inform your answer. Always bring it back to why the Legacy Vault is the solution."
        
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
