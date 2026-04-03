# NBA 2K Legacy Vault - Product Requirements Document

## Original Problem Statement
Build a premium, fast-loading, fully mobile-responsive single-page PWA website for "NBA 2K Legacy Vault" with tagline "Revive the Classics. Play Online Forever." Strict red-black-white aesthetic (#C8102E, #000000, #FFFFFF). 

## Latest Feature: Neplit System (April 2026)
Comprehensive site control and export system:
- **Neplit Tab** - Owner-only admin control room for high-level site changes
- **AI Command Analyzer** - Natural language commands to modify site content
- **The Doc** - Stability and health monitoring with automatic fix suggestions
- **Standalone Export** - Generate portable ZIP with Gemini AI wiring
- **Connectivity Indicator** - LIVE SYNC / VAULT mode display
- **Action Logging** - Full audit trail of all Neplit actions

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **AI**: Claude Sonnet 4.5 via emergentintegrations (Vault AI chatbot)
- **AI for Export**: Gemini 2.5 Flash (standalone version)
- **PWA**: Enhanced service worker with cache-first strategy

## Admin Panel (12 Tabs)
1. **Neplit** - Site control, AI commands, standalone export
2. **Games** - CRUD, reorder, toggle visibility
3. **Clips** - Add YouTube/TikTok/Instagram clips per game
4. **Mockups** - Vault concept cards with image/video support
5. **Proof** - Proof of Demand screenshots with drag & drop upload
6. **Community Wall** - Add tweets/Reddit posts/YouTube comments for social proof
7. **Live Feed** - Add items to the real-time social feed ticker
8. **Submissions** - Review and approve/reject creator submissions
9. **Content** - Edit all site text including Google Doc link
10. **Comments** - View, delete, reply as admin with badge
11. **Emails** - View and export subscribers
12. **Petition** - View signatures, add bulk for social proof

## Neplit Features
### AI Command Analyzer
- Natural language text input for site modifications
- "Analyze & Plan" button - AI generates structured change plan
- "Execute Directly" button - Immediate execution of common commands
- Supported commands:
  - Change hero/vault/games/community/petition headlines
  - Update taglines and descriptions
  - Set petition goal
  - Change CTA buttons
  - Set vault doc URL

### Quick Commands
- Pre-built command templates with one-click execution
- Change Hero Headline, Update Tagline, Set Petition Goal, Change CTA Button, Update Vault Headline

### The Doc - Stability System
- "Run Check" button performs comprehensive health audit
- Checks for: missing content, orphaned clips, petition anomalies
- One-click fixes for detected issues
- Risk-level indicators (low/medium/high)

### Standalone Export
- "Download ZIP" generates fully portable project
- Includes: React frontend, FastAPI backend, Gemini AI integration
- Creates .env.example files (no secrets)
- Includes comprehensive README with deployment guide
- Deployment-ready for Vercel, Railway, Render

### Connectivity Intelligence
- Real-time LIVE SYNC / VAULT indicator
- Shows in both admin panel and landing page header
- Green badge when connected, yellow when offline

### Action Logging
- All Neplit actions recorded with timestamps
- Viewable in collapsible Action Log section
- Includes: content changes, exports, doc fixes, AI plans

## API Endpoints
### Neplit Endpoints
- `GET /api/health` - Health check for connectivity
- `POST /api/neplit/analyze` - AI-powered command analysis
- `POST /api/neplit/execute` - Execute text commands
- `POST /api/neplit/apply-plan` - Apply confirmed AI plan
- `POST /api/neplit/doc/check` - Run stability check
- `POST /api/neplit/doc/fix` - Apply specific fix
- `GET /api/neplit/logs` - Get action logs
- `GET /api/neplit/export` - Download standalone ZIP

### Other Endpoints
- `/api/chat` - Vault AI chatbot (Claude Sonnet)
- `/api/votes` - Era voting poll
- `/api/creator-submissions` - Creator content submissions
- `/api/community-posts` - Community speaks wall posts
- `/api/social-feed` - Live feed items
- `/api/games` - Game management
- `/api/clips` - Video clips management
- `/api/mockups` - Vault mockup cards
- `/api/proof` - Proof of demand images
- `/api/upload` - File upload (multipart + base64)
- `/api/content` - Site content management
- `/api/comments` - Comments with likes and replies
- `/api/subscribers` - Email subscriptions
- `/api/petition-signatures` - Petition signatures
- `/api/admin/login` - Admin authentication

## Testing Status
- Last tested: April 2026
- Backend: 100% (14/14 Neplit tests passed)
- Frontend: 100%
- Test report: `/app/test_reports/iteration_5.json`

## Admin Credentials
- URL: `/admin`
- Password: `A@070610`

## Files of Reference
- `backend/server.py` - All API endpoints (~2100 lines)
- `frontend/src/components/admin/NeplitControl.jsx` - Full Neplit UI component
- `frontend/src/pages/AdminPage.jsx` - Admin panel (12 tabs)
- `frontend/src/pages/LandingPage.jsx` - Landing page with connectivity indicator
- `frontend/public/service-worker.js` - Enhanced PWA service worker
- `frontend/src/hooks/useConnectivity.js` - Connectivity status hook

## Known Limitations
- Vault AI chatbot may hit LLM budget limits (user can add balance via Profile → Universal Key → Add Balance)
- Social feed/community wall require manual admin entry (no live API integration to Twitter/Reddit)
- Standalone export uses Gemini API - requires user's own API key after export

## Completed: April 3, 2026
✅ Neplit Tab with AI Command Analyzer
✅ The Doc stability monitoring system
✅ Standalone ZIP export with Gemini AI wiring
✅ LIVE SYNC / VAULT connectivity indicator
✅ Action logging to MongoDB
✅ Enhanced PWA service worker
✅ Quick Commands panel
✅ 100% test coverage for Neplit features
