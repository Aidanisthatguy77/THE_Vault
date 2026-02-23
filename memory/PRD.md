# NBA 2K Legacy Vault - Product Requirements Document

## Original Problem Statement
Build a premium, fast-loading, fully mobile-responsive single-page PWA website for "NBA 2K Legacy Vault" with tagline "Revive the Classics. Play Online Forever." Strict red-black-white aesthetic (#C8102E, #000000, #FFFFFF). Features include hero section with vault door, games grid with modals, vault concept section, community with comments/email signup, and admin panel for game management.

## User Personas
1. **Nostalgic 2K Gamers**: Long-time NBA 2K fans who miss classic versions (2K15-2K20)
2. **Content Creators**: People who want to share the concept to get 2K's attention
3. **Admin/Owner**: Can manage games, view subscribers, and update content

## Core Requirements (Static)
- Single-page landing with sections: Hero, Games, Vault, Community
- Strict black (#000)/red (#C8102E)/white (#FFF) color palette only
- PWA installable with service worker
- Mobile-first responsive design with bottom nav
- Admin panel for CRUD game management
- MongoDB-backed comments and email subscriptions
- Social share functionality (X, Reddit, TikTok)

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **Styling**: Custom CSS with Barlow Condensed + Manrope fonts
- **PWA**: Service worker + manifest.json

## What's Been Implemented (Feb 23, 2026)

### Backend APIs
- `GET /api/games` - Get active games
- `GET /api/games/all` - Get all games (admin)
- `GET /api/games/:id` - Get single game
- `POST /api/games` - Create game
- `PUT /api/games/:id` - Update game
- `DELETE /api/games/:id` - Delete game
- `GET /api/comments` - Get threaded comments
- `POST /api/comments` - Create comment/reply
- `DELETE /api/comments/:id` - Delete comment
- `POST /api/subscribe` - Email subscription
- `GET /api/subscriptions` - Get all subscribers
- `POST /api/admin/login` - Admin authentication
- `POST /api/seed` - Seed initial games

### Frontend Features
- Hero section with animated vault door
- Games grid (4-col desktop, stacked mobile)
- Game detail modals with YouTube embeds
- Vault concept section with 3 mockup cards
- Comments section with replies
- Email signup form
- Social share buttons
- Admin panel with tabs (Games, Subscribers)
- Admin CRUD for games (add/edit/delete/toggle)
- Mobile bottom navigation
- PWA manifest + service worker

### Admin Credentials
- Password: `legacyvault2k`
- Route: `/admin`

## Prioritized Backlog

### P0 (Critical) - DONE
- [x] Landing page with all sections
- [x] Games CRUD via admin
- [x] Comments system
- [x] Email subscriptions
- [x] PWA support
- [x] Mobile responsive

### P1 (High Priority)
- [ ] Add actual NBA 2K cover art images (requires licensing or user upload)
- [ ] Add more YouTube gameplay clips
- [ ] Admin comment moderation
- [ ] Email notification system

### P2 (Medium Priority)
- [ ] Dark mode toggle
- [ ] Comment upvoting/reactions
- [ ] Social login (optional)
- [ ] Analytics dashboard

## Next Tasks
1. Replace placeholder basketball images with actual game covers (user can update via admin)
2. Add more games as they release
3. Connect email signup to notification service (SendGrid/Resend)
4. Add social proof section (tweet embeds)
