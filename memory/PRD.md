# NBA 2K Legacy Vault - Product Requirements Document

## Original Problem Statement
Build a premium, fast-loading, fully mobile-responsive single-page PWA website for "NBA 2K Legacy Vault" with tagline "Revive the Classics. Play Online Forever." Strict red-black-white aesthetic (#C8102E, #000000, #FFFFFF).

## Latest Feature: Nep - Conversational Dev Partner (April 2026)
Transformed the AI Command Analyzer into "Nep" - a chill senior dev partner that:
- Talks naturally with phrases like "yo", "bet", "let's cook", "lowkey"
- Asks follow-up questions before making changes
- Explains reasoning before proposing changes
- Shows proposals with confirm/reject buttons
- Has persistent conversation history with sidebar
- Can analyze URLs for design inspiration
- Research capability via web content analysis

### Nep System Architecture
- **Backend**: FastAPI endpoints at `/api/nep/*`
- **AI**: Gemini 2.5 Flash via EMERGENT_LLM_KEY
- **Storage**: MongoDB `nep_sessions` collection
- **Frontend**: Full chat UI in NeplitControl.jsx

### Nep API Endpoints
- `GET /api/nep/sessions` - List all conversation sessions
- `GET /api/nep/sessions/{id}` - Get specific session with messages
- `DELETE /api/nep/sessions/{id}` - Delete a conversation
- `POST /api/nep/chat` - Send message to Nep (body: {session_id?, message, urls?})
- `POST /api/nep/confirm` - Confirm or reject a proposal (body: {session_id, message_index, approved})

### Nep Personality System Prompt
Nep uses a custom system prompt that:
- Establishes chill senior dev personality
- Lists all editable content keys
- Defines proposal JSON format
- Encourages asking questions and pushing back

## Neplit System (Export & Control)
- **Standalone Export**: ZIP download with React + FastAPI + Gemini AI wiring
- **The Doc**: Stability monitoring with auto-fix
- **Connectivity Indicator**: LIVE SYNC / VAULT mode
- **Action Logging**: Full audit trail

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **AI**: Claude Sonnet 4.5 (Vault AI chatbot) + Gemini 2.5 Flash (Nep)
- **PWA**: Enhanced service worker with cache-first strategy

## Admin Panel (12 Tabs)
1. **Neplit/Nep** - Conversational dev partner, site control, standalone export
2. **Games** - CRUD, reorder, toggle visibility
3. **Clips** - Add YouTube/TikTok/Instagram clips per game
4. **Mockups** - Vault concept cards with image/video support
5. **Proof** - Proof of Demand screenshots with drag & drop upload
6. **Community Wall** - Add tweets/Reddit posts/YouTube comments
7. **Live Feed** - Add items to the real-time social feed ticker
8. **Submissions** - Review and approve/reject creator submissions
9. **Content** - Edit all site text including Google Doc link
10. **Comments** - View, delete, reply as admin with badge
11. **Emails** - View and export subscribers
12. **Petition** - View signatures, add bulk for social proof

## Testing Status
- Last tested: April 2026
- Nep Backend: 100% (15/15 tests passed)
- Frontend: 100%
- Test report: `/app/test_reports/iteration_6.json`

## Admin Credentials
- URL: `/admin`
- Password: `A@070610`

## Key Files
- `backend/server.py` - All API endpoints (~2400 lines)
- `frontend/src/components/admin/NeplitControl.jsx` - Nep chat + export UI
- `frontend/src/pages/AdminPage.jsx` - Admin panel (12 tabs)
- `frontend/src/pages/LandingPage.jsx` - Landing page with connectivity indicator
- `frontend/public/service-worker.js` - Enhanced PWA service worker

## Completed: April 4, 2026
✅ Nep - Conversational Dev Partner
✅ Chill senior dev personality ("yo", "bet", "let's cook")
✅ Follow-up questions before changes
✅ Proposal cards with confirm/reject buttons
✅ Persistent conversation history with sidebar
✅ URL analysis for design inspiration
✅ 100% test coverage for Nep features

## Previous Features
- Neplit Tab with export functionality
- The Doc stability monitoring
- Standalone ZIP export with Gemini AI
- LIVE SYNC / VAULT connectivity indicator
- Action logging to MongoDB
- Enhanced PWA service worker
- Quick Commands panel
- Vault AI chatbot with web scraping
- Era voting, creator submissions, community features
