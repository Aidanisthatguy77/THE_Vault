# NBA 2K Legacy Vault - Product Requirements Document

## Original Problem Statement
Build a premium, fast-loading, fully mobile-responsive single-page PWA website for "NBA 2K Legacy Vault" with tagline "Revive the Classics. Play Online Forever." Strict red-black-white aesthetic (#C8102E, #000000, #FFFFFF). 

## Latest Feature Expansion (March 2026)
Massive feature upgrade to make the site legendary:
- **Vault AI Chatbot** powered by Claude Sonnet - 24/7 AI spokesperson
- **Era Voting Poll** - Real-time community voting
- **Interactive Vault Demo** - Clickable simulation of what the menu would look like
- **Creator Submission System** - Let creators submit content to be featured
- **Community Speaks Wall** - Social proof with tweets, Reddit posts, YouTube comments
- **Live Social Feed** - Real-time ticker of social mentions

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Motor async driver)
- **AI**: Claude Sonnet 4.5 via emergentintegrations
- **PWA**: Service worker + manifest.json

## Admin Panel (11 Tabs)
1. **Games** - CRUD, reorder, toggle visibility
2. **Clips** - Add YouTube/TikTok/Instagram clips per game
3. **Mockups** - Vault concept cards with image/video support
4. **Proof** - Proof of Demand screenshots with drag & drop upload
5. **Community Wall** - Add tweets/Reddit posts/YouTube comments for social proof
6. **Live Feed** - Add items to the real-time social feed ticker
7. **Submissions** - Review and approve/reject creator submissions
8. **Content** - Edit all site text including Google Doc link
9. **Comments** - View, delete, reply as admin with badge
10. **Emails** - View and export subscribers
11. **Petition** - View signatures, add bulk for social proof

## API Endpoints
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
- Last tested: March 2026
- Backend: 95.4% (21/22 - 1 LLM budget limit)
- Frontend: 100%
- Test report: `/app/test_reports/iteration_4.json`

## Admin Credentials
- URL: `/admin`
- Password: `A@070610`

## Known Limitations
- Vault AI chatbot may hit LLM budget limits (user can add balance via Profile → Universal Key → Add Balance)
- Social feed/community wall require manual admin entry (no live API integration to Twitter/Reddit)

## Files of Reference
- `backend/server.py` - All API endpoints
- `frontend/src/pages/AdminPage.jsx` - Admin panel (11 tabs)
- `frontend/src/pages/LandingPage.jsx` - Landing page with all new features
- `frontend/src/index.css` - Animations and styling
