# NBA 2K Legacy Vault - Product Requirements Document

## Original Problem Statement
Build a premium, fast-loading, fully mobile-responsive single-page PWA website for "NBA 2K Legacy Vault" with tagline "Revive the Classics. Play Online Forever." Strict red-black-white aesthetic (#C8102E, #000000, #FFFFFF). Features include hero section with vault door, games grid with modals, vault concept section, community with comments/email signup, and admin panel for full content management.

## User Personas
1. **Nostalgic 2K Gamers**: Long-time NBA 2K fans who miss classic versions (2K15-2K20)
2. **Content Creators**: People who want to share the concept to get 2K's attention
3. **Admin/Owner**: Full control to manage games, clips, content, comments, subscribers, proofs, and petition

## Core Requirements (Static)
- Single-page landing with sections: Hero, Games, Vault (with Proof of Demand), Community
- Strict black (#000)/red (#C8102E)/white (#FFF) color palette only
- PWA installable with service worker
- Mobile-first responsive design with bottom nav
- Comprehensive admin panel for all content management
- MongoDB-backed data persistence
- Social share functionality (X, Reddit, TikTok)

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **Styling**: Custom CSS with Barlow Condensed + Manrope fonts
- **PWA**: Service worker + manifest.json
- **File Storage**: Local uploads served via FastAPI StaticFiles

## What's Been Implemented

### Backend APIs (Feb 23, 2026)
**Games**
- `GET /api/games` - Get active games
- `GET /api/games/all` - Get all games (admin)
- `POST /api/games` - Create game
- `PUT /api/games/:id` - Update game
- `DELETE /api/games/:id` - Delete game

**Clips**
- `GET /api/clips` - Get all clips
- `GET /api/clips/game/:id` - Get clips for a game
- `POST /api/clips` - Create clip
- `PUT /api/clips/:id` - Update clip
- `DELETE /api/clips/:id` - Delete clip

**Proof of Demand**
- `GET /api/proof` - Get all proofs
- `POST /api/proof` - Create proof
- `PUT /api/proof/:id` - Update proof
- `DELETE /api/proof/:id` - Delete proof

**Vault Mockups (NEW)**
- `GET /api/mockups` - Get all mockups
- `POST /api/mockups` - Create mockup (image or video)
- `PUT /api/mockups/:id` - Update mockup
- `DELETE /api/mockups/:id` - Delete mockup
- `POST /api/mockups/seed` - Seed default mockups

**File Upload**
- `POST /api/upload` - Upload image file (multipart/form-data)
- `POST /api/upload/base64` - Upload clipboard paste (base64)
- `GET /api/uploads/:filename` - Serve uploaded files

**Site Content**
- `GET /api/content` - Get all site content
- `GET /api/content/:key` - Get specific content
- `POST /api/content` - Update content
- `POST /api/content/seed` - Seed default content

**Comments**
- `GET /api/comments` - Get threaded comments
- `POST /api/comments` - Create comment/reply
- `POST /api/comments/:id/like` - Like a comment
- `DELETE /api/comments/:id` - Delete comment

**Email Subscriptions**
- `POST /api/subscribe` - Subscribe email
- `GET /api/subscriptions` - Get all subscribers
- `DELETE /api/subscriptions/:id` - Remove subscriber

**Petition**
- `POST /api/petition/sign` - Sign petition
- `GET /api/petition/count` - Get signature count
- `GET /api/petition/signatures` - Get all signatures
- `POST /api/petition/add-bulk` - Add bulk signatures
- `DELETE /api/petition/:id` - Delete signature

**Admin**
- `POST /api/admin/login` - Admin authentication
- `POST /api/seed` - Seed initial games

### Frontend Features
- Hero section with animated vault door
- Games grid with modal details and embedded clips
- Vault concept section with multi-cover banner
- **Google Doc link button** with customizable text
- **Proof of Demand gallery** showing screenshots
- **Vault Mockup Cards** - fully customizable with images OR video embeds
- Comments section with likes and admin replies
- Email signup form
- Petition counter with sign-up
- Social share buttons
- **Comprehensive Admin Panel with 8 tabs:**
  - Games: CRUD, reorder, toggle visibility
  - Clips: Add YouTube/TikTok/Instagram clips per game
  - **Mockups: Add/edit/delete vault concept cards with image upload OR video embeds**
  - Proof: **Direct file upload + clipboard paste (Ctrl+V)**
  - Content: Edit all site text including Google Doc link
  - Comments: View, delete, reply as admin with badge
  - Emails: View and export subscribers
  - Petition: View signatures, add bulk for social proof
- Mobile bottom navigation
- PWA manifest + service worker

### Admin Credentials
- Password: `A@070610`
- Route: `/admin`

## Prioritized Backlog

### P0 (Critical) - COMPLETED
- [x] Landing page with all sections
- [x] Games CRUD via admin
- [x] Clips management per game
- [x] Comments system with likes and replies
- [x] Email subscriptions
- [x] Petition counter with signatures
- [x] PWA support
- [x] Mobile responsive
- [x] **Proof of Demand with direct file upload and clipboard paste**
- [x] **Google Doc link integration**
- [x] **Vault Mockups management with image upload AND video embed support**

### P1 (High Priority)
- [ ] Email notification system (SendGrid/Resend integration)
- [ ] Admin comment notifications
- [ ] Add more YouTube gameplay clips

### P2 (Medium Priority)
- [ ] Social login (optional)
- [ ] Analytics dashboard
- [ ] Tweet embeds in proof section

## Testing Status
- Last tested: Feb 23, 2026
- Backend: 100% (23/23 tests passed)
- Frontend: 100%
- Test report: `/app/test_reports/iteration_2.json`

## Files of Reference
- `backend/server.py` - All API endpoints
- `frontend/src/pages/AdminPage.jsx` - Admin panel with all 7 tabs
- `frontend/src/pages/LandingPage.jsx` - Main landing page
- `frontend/src/App.js` - App routing and PWA setup
