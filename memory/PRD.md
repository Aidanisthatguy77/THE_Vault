# NBA 2K Legacy Vault - Product Requirements Document

## Original Problem Statement
Build a premium, fast-loading, fully mobile-responsive single-page PWA website for "NBA 2K Legacy Vault".

## Latest Feature: Unified Vault Engine (Dual AI System)
Complete standalone AI system with auto-routing:

### Dual Engine Architecture
| Engine | Model | Use Case |
|--------|-------|----------|
| **Media Engine** | Claude 3.5 Sonnet | YouTube, X/Twitter, Facebook, TikTok, Instagram, Reddit analysis |
| **Logic Engine** | Gemini 2.0 Flash | General commands, site management, quick responses |

### Auto-Routing Logic
1. User sends message → System checks for media URLs
2. Media URLs detected → Routes to **Claude Media Engine**
3. Claude analyzes → Returns structured analysis (title, sentiment, key points)
4. No media URLs → Routes to **Gemini Logic Engine**
5. Response stored with model metadata for chat history

### Multi-Modal Memory
- Each chat message stores:
  - `model_used`: "claude" or "gemini"
  - `model_version`: Full version string
  - `media_metadata`: Analysis results from Claude
  - `has_media_analysis`: Boolean flag
  - `timestamp`: ISO timestamp

### Standalone Export
The "Download ZIP" exports a complete package with:
- `dual_engine_ai.py` - Full dual-engine system
- `.env.example` with ANTHROPIC_API_KEY + GEMINI_API_KEY
- Updated README with dual-engine documentation
- All frontend and backend code

## Key API Endpoints

### Chat (Dual Engine)
- `POST /api/chat` - Auto-routes between Claude/Gemini
  - Returns: `response`, `session_id`, `model_used`, `model_version`, `media_analyses`

### Chat History
- `GET /api/chat/history/{session_id}` - Get messages with model info
- `GET /api/chat/sessions` - List all sessions with model summary

### System Health
- `GET /api/health` - Full diagnostics (DB, AI status)
- `GET /api/health/pulse` - Quick pulse for UI indicator

### Secrets Vault
- `GET/POST/DELETE /api/admin/secrets` - Deployment credentials

## Testing Status
- Dual Engine Routing: ✅ Verified (Gemini for text, Claude for media links)
- Export Contains: ✅ dual_engine_ai.py, .env.example, README.md
- Chat History Tracking: ✅ model_used stored with each message

## Admin Credentials
- URL: `/admin`
- Password: `A@070610`

## Files Modified
- `backend/server.py` - Added dual-engine chat, model tracking, chat history endpoints
- `backend/server.py` - Updated export to include dual_engine_ai.py

## Completed: April 7, 2026
✅ Unified Vault Engine (Claude + Gemini)
✅ Auto-Routing Logic (media links → Claude, else → Gemini)
✅ Multi-Modal Memory (model tracking in chat history)
✅ Standalone Export with dual_engine_ai.py
✅ Chat history endpoints with model metadata
