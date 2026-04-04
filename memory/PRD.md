# NBA 2K Legacy Vault - Product Requirements Document

## Original Problem Statement
Build a premium, fast-loading, fully mobile-responsive single-page PWA website for "NBA 2K Legacy Vault" with tagline "Revive the Classics. Play Online Forever." Strict red-black-white aesthetic (#C8102E, #000000, #FFFFFF).

## Latest Feature: Total Site Sync (April 2026)
Comprehensive system integration for deployment readiness:
- **System Pulse** - Real-time health monitoring with glowing indicator
- **Enhanced Health API** - Full system diagnostics
- **Secrets Vault** - Secure storage for deployment keys
- **Global State** - React Context for instant UI sync
- **vercel.json** - Deployment routing configuration

### System Pulse
- Green glowing dot when system is healthy
- Shows API and Database status icons
- Expandable panel with full diagnostics
- Auto-pings every 30 seconds

### Enhanced Health Endpoints
- `GET /api/health` - Full system diagnostics (DB latency, collections, AI status)
- `GET /api/health/pulse` - Lightweight pulse check for UI

### Secrets Vault
- Secure storage for deployment credentials
- Pre-configured templates for VERCEL_TOKEN, MONGODB_URI, GEMINI_API_KEY, SUPABASE
- Values masked in UI (only last 4 chars visible)
- Endpoints: GET/POST/DELETE `/api/admin/secrets`

### Global State (React Context)
- `GlobalProvider` wraps entire app
- `useGlobalState()` hook for site content, games, health
- Real-time updates via custom events
- Auto-refresh on content changes

## Nep - Conversational Dev Partner
- Chill senior dev personality ("yo", "bet", "let's cook")
- Follow-up questions before changes
- Proposal cards with confirm/reject buttons
- Persistent conversation history
- URL analysis for design inspiration

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI + Global Context
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **AI**: Gemini 2.5 Flash via EMERGENT_LLM_KEY
- **PWA**: Enhanced service worker
- **Deployment**: vercel.json configured

## File Structure
```
/app/
├── vercel.json                    # Deployment routing
├── frontend/
│   ├── src/
│   │   ├── context/
│   │   │   └── GlobalContext.js   # Global state provider
│   │   ├── components/admin/
│   │   │   └── NeplitControl.jsx  # Nep chat + System Pulse + Secrets
│   │   └── pages/
│   │       ├── LandingPage.jsx
│   │       └── AdminPage.jsx
│   └── App.js                     # Wrapped with GlobalProvider
└── backend/
    └── server.py                  # All API endpoints (~2500 lines)
```

## Key API Endpoints
- `/api/health` - Full system health check
- `/api/health/pulse` - Quick pulse for UI indicator
- `/api/admin/secrets` - Secrets vault CRUD
- `/api/nep/*` - Conversational AI endpoints
- `/api/neplit/*` - Export and stability endpoints

## Testing Status
- System Pulse: ✅ Verified (pulse: alive, backend: true, database: true)
- Secrets Vault: ✅ Verified (save, get masked, delete)
- Global Context: ✅ Integrated
- vercel.json: ✅ Created

## Admin Credentials
- URL: `/admin`
- Password: `A@070610`

## Deployment Instructions
1. Click "Save to Github" in Emergent platform
2. Connect your GitHub repo (https://github.com/Aidanisthatguy77/THE_Vault)
3. Deploy to Vercel:
   - Connect GitHub repo to Vercel
   - Set environment variables (use Secrets Vault as reference)
   - Vercel will use vercel.json for routing

## Completed: April 4, 2026
✅ System Pulse indicator with health monitoring
✅ Enhanced /api/health with full diagnostics
✅ Secrets Vault with masked values
✅ Global State with React Context
✅ vercel.json deployment configuration
✅ Nep conversational dev partner
✅ ZIP export with Gemini AI wiring
