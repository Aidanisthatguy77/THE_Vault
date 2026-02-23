import { useState, useEffect } from "react";
import axios from "axios";
import { Menu, X, Home, Gamepad2, Lock, Users, Share2, Trophy, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SHARE_URL = "https://docs.google.com/document/d/1DEb_W0fxCGWaGN97KcVkVqD1JmZEOUrl5DpCCaayHe0/edit?tab=t.0#heading=h.4a00a8jkgs1z";
const SHARE_TEXT = "This Legacy Vault concept would change NBA 2K forever 🔥";

// Header Component
const Header = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
    setMobileMenuOpen(false);
  };

  return (
    <header className="fixed top-0 w-full z-50 bg-black/90 backdrop-blur-md border-b border-white/10" data-testid="header">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2" data-testid="logo">
            <div className="relative">
              <span className="font-heading text-2xl font-black text-white">2K</span>
              <div className="absolute -top-1 -right-2 w-3 h-3 rounded-full bg-[#C8102E]"></div>
            </div>
            <span className="font-heading text-xl font-bold text-white hover:text-[#C8102E] transition-colors cursor-pointer red-glow">
              Legacy Vault
            </span>
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-8">
            <button onClick={() => scrollTo('hero')} className="text-white hover:text-[#C8102E] transition-colors font-medium" data-testid="nav-home">Home</button>
            <button onClick={() => scrollTo('games')} className="text-white hover:text-[#C8102E] transition-colors font-medium" data-testid="nav-games">The Games</button>
            <button onClick={() => scrollTo('vault')} className="text-white hover:text-[#C8102E] transition-colors font-medium" data-testid="nav-vault">The Vault</button>
            <button onClick={() => scrollTo('community')} className="text-white hover:text-[#C8102E] transition-colors font-medium" data-testid="nav-community">Community</button>
          </nav>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden text-white p-2" 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="mobile-menu-btn"
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-black/95 border-b border-white/10" data-testid="mobile-menu">
          <nav className="flex flex-col p-4 gap-4">
            <button onClick={() => scrollTo('hero')} className="text-white hover:text-[#C8102E] transition-colors font-medium text-left py-2">Home</button>
            <button onClick={() => scrollTo('games')} className="text-white hover:text-[#C8102E] transition-colors font-medium text-left py-2">The Games</button>
            <button onClick={() => scrollTo('vault')} className="text-white hover:text-[#C8102E] transition-colors font-medium text-left py-2">The Vault</button>
            <button onClick={() => scrollTo('community')} className="text-white hover:text-[#C8102E] transition-colors font-medium text-left py-2">Community</button>
          </nav>
        </div>
      )}
    </header>
  );
};

// Hero Section
const HeroSection = () => {
  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  const shareOnX = () => {
    window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(SHARE_TEXT)}&url=${encodeURIComponent(SHARE_URL)}`, '_blank');
  };

  const shareOnReddit = () => {
    window.open(`https://reddit.com/submit?url=${encodeURIComponent(SHARE_URL)}&title=${encodeURIComponent(SHARE_TEXT)}`, '_blank');
  };

  const shareOnTikTok = () => {
    navigator.clipboard.writeText(`${SHARE_TEXT} ${SHARE_URL}`);
    toast.success("Link copied! Share it on TikTok");
  };

  return (
    <section id="hero" className="hero-section court-pattern pt-20" data-testid="hero-section">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Vault Door */}
        <div className="vault-door vault-pulse mx-auto mb-8 animate-fade-in-up" data-testid="vault-door">
          <div className="absolute inset-0 flex items-center justify-center">
            <Lock className="w-12 h-12 text-[#C8102E]" />
          </div>
        </div>

        {/* Headline */}
        <h1 className="font-heading text-4xl sm:text-5xl lg:text-7xl font-black text-white uppercase tracking-tight mb-4 animate-fade-in-up animation-delay-100" data-testid="hero-headline">
          <span className="underline-red">The NBA 2K Legacy Vault</span>
        </h1>

        {/* Subheadline */}
        <p className="text-lg sm:text-xl lg:text-2xl text-white/90 mb-2 animate-fade-in-up animation-delay-200 font-heading" data-testid="hero-subheadline">
          <span className="text-[#C8102E]">2K15</span> • <span className="text-[#C8102E]">2K16</span> • <span className="text-[#C8102E]">2K17</span> • <span className="text-[#C8102E]">2K20</span> — All in one place.
        </p>
        <p className="text-base sm:text-lg text-white/80 mb-8 animate-fade-in-up animation-delay-200">
          Persistent online. No resets. <span className="text-[#C8102E] font-bold">Ever.</span>
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8 animate-fade-in-up animation-delay-300">
          <Button 
            onClick={() => scrollTo('games')} 
            className="btn-primary text-base sm:text-lg px-8 py-6"
            data-testid="explore-games-btn"
          >
            Explore the Games
          </Button>
          <Button 
            onClick={() => scrollTo('vault')} 
            variant="outline"
            className="bg-transparent border-2 border-white text-white hover:bg-white hover:text-black text-base sm:text-lg px-8 py-6 uppercase tracking-widest font-bold"
            data-testid="see-vision-btn"
          >
            See the Vision
          </Button>
        </div>

        {/* Share Row */}
        <div className="flex justify-center gap-4 animate-fade-in-up animation-delay-400" data-testid="share-row">
          <button onClick={shareOnX} className="share-btn" data-testid="share-x">
            <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          </button>
          <button onClick={shareOnReddit} className="share-btn" data-testid="share-reddit">
            <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg>
          </button>
          <button onClick={shareOnTikTok} className="share-btn" data-testid="share-tiktok">
            <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/></svg>
          </button>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
          <ChevronDown className="w-8 h-8 text-white/50" />
        </div>
      </div>
    </section>
  );
};

// Game Card Component
const GameCard = ({ game, onClick }) => {
  return (
    <div 
      className="game-card bg-[#09090B] rounded-md overflow-hidden cursor-pointer group"
      onClick={onClick}
      data-testid={`game-card-${game.year}`}
    >
      <div className="aspect-[3/4] overflow-hidden">
        <img 
          src={game.cover_image} 
          alt={game.title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
          loading="lazy"
        />
      </div>
      <div className="p-4">
        <h3 className="font-heading text-xl font-bold text-white uppercase">{game.title}</h3>
        <p className="text-white/60 text-sm mb-2">{game.year}</p>
        <p className="text-[#C8102E] text-sm font-medium">{game.hook_text}</p>
      </div>
    </div>
  );
};

// Games Section
const GamesSection = ({ games }) => {
  const [selectedGame, setSelectedGame] = useState(null);

  return (
    <section id="games" className="py-20 court-pattern" data-testid="games-section">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="font-heading text-3xl sm:text-4xl lg:text-5xl font-black text-white uppercase text-center mb-4">
          <span className="underline-red">The Games</span>
        </h2>
        <p className="text-white/70 text-center mb-12 max-w-2xl mx-auto">
          Four legendary eras of NBA 2K basketball. Each one a masterpiece. All preserved forever.
        </p>

        {/* Games Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {games.map((game) => (
            <GameCard key={game.id} game={game} onClick={() => setSelectedGame(game)} />
          ))}
        </div>
      </div>

      {/* Game Detail Modal */}
      <Dialog open={!!selectedGame} onOpenChange={() => setSelectedGame(null)}>
        <DialogContent className="bg-[#09090B] border-white/10 max-w-4xl max-h-[90vh] overflow-y-auto" data-testid="game-modal">
          {selectedGame && (
            <>
              <DialogHeader>
                <DialogTitle className="font-heading text-3xl font-black text-white uppercase">
                  {selectedGame.title} <span className="text-[#C8102E]">({selectedGame.year})</span>
                </DialogTitle>
              </DialogHeader>
              
              <div className="grid md:grid-cols-2 gap-6 mt-4">
                <div>
                  <img 
                    src={selectedGame.cover_image} 
                    alt={selectedGame.title}
                    className="w-full rounded-md"
                  />
                </div>
                <div>
                  <h4 className="text-[#C8102E] font-heading text-lg font-bold uppercase mb-2">Cover</h4>
                  <p className="text-white/80 mb-4">{selectedGame.cover_athletes}</p>
                  
                  <h4 className="text-[#C8102E] font-heading text-lg font-bold uppercase mb-2">The Legacy</h4>
                  <p className="text-white/80 leading-relaxed">{selectedGame.description}</p>
                </div>
              </div>

              {selectedGame.youtube_embed && (
                <div className="mt-6">
                  <h4 className="text-[#C8102E] font-heading text-lg font-bold uppercase mb-4">Gameplay Highlights</h4>
                  <div className="aspect-video">
                    <iframe
                      src={selectedGame.youtube_embed}
                      title={`${selectedGame.title} Gameplay`}
                      className="w-full h-full rounded-md"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    ></iframe>
                  </div>
                </div>
              )}
            </>
          )}
        </DialogContent>
      </Dialog>
    </section>
  );
};

// Vault Section
const VaultSection = () => {
  return (
    <section id="vault" className="py-20 bg-[#09090B]" data-testid="vault-section">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="font-heading text-3xl sm:text-4xl lg:text-5xl font-black text-white uppercase text-center mb-4">
          <span className="underline-red">One Vault. Four Eras. Infinite Play.</span>
        </h2>
        <p className="text-white/70 text-center mb-12 max-w-2xl mx-auto">
          The revolutionary concept that changes everything.
        </p>

        {/* Concept Description */}
        <div className="max-w-4xl mx-auto mb-12">
          <div className="bg-black p-6 sm:p-8 rounded-md border border-white/10">
            <p className="text-white/90 text-base sm:text-lg leading-relaxed mb-6">
              The NBA 2K Legacy Vault is a revolutionary 'game-within-a-game' mode. Launch full, untouched versions of 2K15, 2K16, 2K17, and 2K20 directly inside modern NBA 2K — powered by secure containers on persistent online servers.
            </p>
            <p className="text-white/90 text-base sm:text-lg leading-relaxed mb-6">
              <span className="text-[#C8102E] font-bold">No more sunsets.</span> No player-base split. No cheating.
            </p>
            <p className="text-white/90 text-base sm:text-lg leading-relaxed">
              Friends list works across every era. Park, Pro-Am, Rec, MyTEAM, MyCAREER — all alive forever.
              <br /><br />
              <span className="text-[#C8102E]">Monetization?</span> Simple subscription or one-time DLC to unlock the Vault. Cosmetic packs per era. High-margin nostalgia revenue that prints money while keeping the community together.
            </p>
          </div>
        </div>

        {/* Mockup Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="bg-black p-6 rounded-md border border-white/10 text-center" data-testid="mockup-1">
            <div className="w-full aspect-video bg-[#09090B] rounded-md flex items-center justify-center mb-4 border border-[#C8102E]/30">
              <div className="text-center">
                <Trophy className="w-12 h-12 text-[#C8102E] mx-auto mb-2" />
                <p className="font-heading text-white uppercase text-sm">Vault Menu</p>
                <div className="flex justify-center gap-2 mt-2">
                  {['15', '16', '17', '20'].map(year => (
                    <div key={year} className="w-10 h-10 border border-white/30 rounded flex items-center justify-center text-white text-xs font-bold">
                      {year}
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <p className="text-white/70 text-sm">Vault menu showing all four game icons in modern 2K</p>
          </div>

          <div className="bg-black p-6 rounded-md border border-white/10 text-center" data-testid="mockup-2">
            <div className="w-full aspect-video bg-[#09090B] rounded-md flex items-center justify-center mb-4 border border-[#C8102E]/30">
              <div className="text-center">
                <div className="spinner mx-auto mb-3"></div>
                <p className="font-heading text-white uppercase">Entering <span className="text-[#C8102E]">2K16</span>...</p>
              </div>
            </div>
            <p className="text-white/70 text-sm">Loading screen transitioning into classic era</p>
          </div>

          <div className="bg-black p-6 rounded-md border border-white/10 text-center" data-testid="mockup-3">
            <div className="w-full aspect-video bg-[#09090B] rounded-md flex items-center justify-center mb-4 border border-[#C8102E]/30">
              <div className="grid grid-cols-2 gap-2 p-4 w-full">
                <div className="bg-black/50 p-2 rounded border border-white/20">
                  <p className="text-[#C8102E] text-xs font-heading uppercase">2K15 Park</p>
                  <div className="flex gap-1 mt-1">
                    <div className="w-4 h-4 rounded-full bg-white/30"></div>
                    <div className="w-4 h-4 rounded-full bg-white/30"></div>
                  </div>
                </div>
                <div className="bg-black/50 p-2 rounded border border-white/20">
                  <p className="text-white text-xs font-heading uppercase">Friends</p>
                  <div className="flex gap-1 mt-1">
                    <div className="w-4 h-4 rounded-full bg-[#C8102E]/50"></div>
                    <div className="w-4 h-4 rounded-full bg-[#C8102E]/50"></div>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-white/70 text-sm">Unified friends list across all eras</p>
          </div>
        </div>

        {/* Features List */}
        <div className="max-w-2xl mx-auto mb-12">
          <ul className="space-y-3">
            {[
              "Eternal online for every classic",
              "Unified progression & friends",
              "Cheat-proof containers",
              "Recurring revenue stream for 2K",
              "OG retention + new players discovering history"
            ].map((feature, index) => (
              <li key={index} className="flex items-center gap-3 text-white/90">
                <span className="w-2 h-2 rounded-full bg-[#C8102E] flex-shrink-0"></span>
                {feature}
              </li>
            ))}
          </ul>
        </div>

        {/* CTA */}
        <div className="text-center">
          <Button 
            onClick={() => {
              navigator.clipboard.writeText(`${SHARE_TEXT} ${SHARE_URL}`);
              toast.success("Link copied! Share it everywhere!");
            }}
            className="btn-primary text-lg px-10 py-6"
            data-testid="share-cta-btn"
          >
            <Share2 className="w-5 h-5 mr-2" />
            This is the future. Share it with 2K.
          </Button>
        </div>
      </div>
    </section>
  );
};

// Comments Component
const CommentsSection = () => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState({ author_name: '', content: '' });
  const [replyTo, setReplyTo] = useState(null);
  const [replyContent, setReplyContent] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchComments = async () => {
    try {
      const response = await axios.get(`${API}/comments`);
      setComments(response.data);
    } catch (error) {
      console.error('Error fetching comments:', error);
    }
  };

  useEffect(() => {
    fetchComments();
  }, []);

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!newComment.author_name.trim() || !newComment.content.trim()) {
      toast.error("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/comments`, newComment);
      setNewComment({ author_name: '', content: '' });
      fetchComments();
      toast.success("Comment posted!");
    } catch (error) {
      toast.error("Failed to post comment");
    }
    setLoading(false);
  };

  const handleSubmitReply = async (parentId) => {
    if (!replyContent.trim()) {
      toast.error("Please enter a reply");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/comments`, {
        author_name: newComment.author_name || "Anonymous",
        content: replyContent,
        parent_id: parentId
      });
      setReplyTo(null);
      setReplyContent('');
      fetchComments();
      toast.success("Reply posted!");
    } catch (error) {
      toast.error("Failed to post reply");
    }
    setLoading(false);
  };

  return (
    <div className="max-w-3xl mx-auto" data-testid="comments-section">
      <h3 className="font-heading text-2xl font-bold text-white uppercase mb-6">Join the Discussion</h3>
      
      {/* Comment Form */}
      <form onSubmit={handleSubmitComment} className="mb-8 bg-black p-4 rounded-md border border-white/10">
        <Input
          type="text"
          placeholder="Your name"
          value={newComment.author_name}
          onChange={(e) => setNewComment({ ...newComment, author_name: e.target.value })}
          className="bg-black border-white/20 text-white mb-3"
          data-testid="comment-name-input"
        />
        <Textarea
          placeholder="Share your thoughts on the Legacy Vault concept..."
          value={newComment.content}
          onChange={(e) => setNewComment({ ...newComment, content: e.target.value })}
          className="bg-black border-white/20 text-white mb-3 min-h-[100px]"
          data-testid="comment-content-input"
        />
        <Button 
          type="submit" 
          disabled={loading}
          className="btn-primary"
          data-testid="submit-comment-btn"
        >
          {loading ? 'Posting...' : 'Post Comment'}
        </Button>
      </form>

      {/* Comments List */}
      <div className="space-y-4">
        {comments.length === 0 ? (
          <p className="text-white/50 text-center py-8">Be the first to comment!</p>
        ) : (
          comments.map((comment) => (
            <div key={comment.id} className="comment-item rounded-md" data-testid={`comment-${comment.id}`}>
              <div className="flex justify-between items-start mb-2">
                <span className="font-bold text-white">{comment.author_name}</span>
                <span className="text-white/40 text-sm">{new Date(comment.created_at).toLocaleDateString()}</span>
              </div>
              <p className="text-white/80 mb-3">{comment.content}</p>
              <button 
                onClick={() => setReplyTo(replyTo === comment.id ? null : comment.id)}
                className="text-[#C8102E] text-sm hover:underline"
                data-testid={`reply-btn-${comment.id}`}
              >
                Reply
              </button>

              {/* Reply Form */}
              {replyTo === comment.id && (
                <div className="mt-3 pl-4 border-l-2 border-[#C8102E]">
                  <Textarea
                    placeholder="Write a reply..."
                    value={replyContent}
                    onChange={(e) => setReplyContent(e.target.value)}
                    className="bg-black border-white/20 text-white mb-2 min-h-[80px]"
                    data-testid="reply-input"
                  />
                  <Button 
                    onClick={() => handleSubmitReply(comment.id)}
                    disabled={loading}
                    className="btn-primary text-sm py-2"
                    data-testid="submit-reply-btn"
                  >
                    {loading ? 'Posting...' : 'Post Reply'}
                  </Button>
                </div>
              )}

              {/* Replies */}
              {comment.replies && comment.replies.length > 0 && (
                <div className="mt-4 space-y-3">
                  {comment.replies.map((reply) => (
                    <div key={reply.id} className="reply-item" data-testid={`reply-${reply.id}`}>
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-bold text-white text-sm">{reply.author_name}</span>
                        <span className="text-white/40 text-xs">{new Date(reply.created_at).toLocaleDateString()}</span>
                      </div>
                      <p className="text-white/70 text-sm">{reply.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

// Email Signup Component
const EmailSignup = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      toast.error("Please enter your email");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/subscribe`, { email });
      setEmail('');
      toast.success("You're in! We'll notify you when this goes to 2K.");
    } catch (error) {
      if (error.response?.data?.detail === "Email already subscribed") {
        toast.error("This email is already subscribed!");
      } else {
        toast.error("Failed to subscribe. Please try again.");
      }
    }
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto text-center" data-testid="email-signup">
      <h3 className="font-heading text-2xl font-bold text-white uppercase mb-4">Join the Movement</h3>
      <p className="text-white/70 mb-6">Get notified when we push this to 2K</p>
      
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <Input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="bg-black border-white/20 text-white flex-1"
          data-testid="email-input"
        />
        <Button 
          type="submit"
          disabled={loading}
          className="btn-primary whitespace-nowrap"
          data-testid="subscribe-btn"
        >
          {loading ? 'Subscribing...' : 'Notify Me'}
        </Button>
      </form>
    </div>
  );
};

// Petition Counter Component
const PetitionCounter = () => {
  const [count, setCount] = useState(0);
  const [showSign, setShowSign] = useState(false);
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [recentSigners, setRecentSigners] = useState([]);

  const fetchCount = async () => {
    try {
      const response = await axios.get(`${API}/petition/count`);
      setCount(response.data.count);
    } catch (error) {
      console.error('Error fetching count:', error);
    }
  };

  const fetchRecentSigners = async () => {
    try {
      const response = await axios.get(`${API}/petition/signatures`);
      setRecentSigners(response.data.slice(0, 5));
    } catch (error) {
      console.error('Error fetching signers:', error);
    }
  };

  useEffect(() => {
    fetchCount();
    fetchRecentSigners();
  }, []);

  const handleSign = async (e) => {
    e.preventDefault();
    if (!name.trim()) {
      toast.error("Please enter your name");
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API}/petition/sign`, { name, location: location || null });
      setName('');
      setLocation('');
      setShowSign(false);
      fetchCount();
      fetchRecentSigners();
      toast.success("Your signature has been added! Thank you for your support!");
    } catch (error) {
      toast.error("Failed to sign petition");
    }
    setLoading(false);
  };

  return (
    <div className="bg-black p-6 sm:p-8 rounded-md border border-[#C8102E] text-center" data-testid="petition-counter">
      <div className="mb-4">
        <Trophy className="w-12 h-12 text-[#C8102E] mx-auto mb-2" />
        <h3 className="font-heading text-2xl sm:text-3xl font-black text-white uppercase">Community Support</h3>
      </div>
      
      <div className="mb-6">
        <div className="font-heading text-5xl sm:text-6xl font-black text-[#C8102E] mb-2" data-testid="petition-count">
          {count.toLocaleString()}+
        </div>
        <p className="text-white/70">fans want the Legacy Vault</p>
      </div>

      {!showSign ? (
        <Button 
          onClick={() => setShowSign(true)}
          className="btn-primary text-lg px-8 py-4"
          data-testid="sign-petition-btn"
        >
          Add Your Name
        </Button>
      ) : (
        <form onSubmit={handleSign} className="space-y-3 max-w-sm mx-auto">
          <Input
            type="text"
            placeholder="Your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="bg-black border-white/20 text-white"
            data-testid="petition-name-input"
          />
          <Input
            type="text"
            placeholder="City/Country (optional)"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            className="bg-black border-white/20 text-white"
            data-testid="petition-location-input"
          />
          <div className="flex gap-2">
            <Button 
              type="button"
              variant="outline"
              onClick={() => setShowSign(false)}
              className="flex-1 border-white/20 text-white hover:bg-white/10"
            >
              Cancel
            </Button>
            <Button 
              type="submit"
              disabled={loading}
              className="flex-1 btn-primary"
              data-testid="submit-signature-btn"
            >
              {loading ? 'Signing...' : 'Sign Now'}
            </Button>
          </div>
        </form>
      )}

      {recentSigners.length > 0 && (
        <div className="mt-6 pt-4 border-t border-white/10">
          <p className="text-white/50 text-sm mb-2">Recent supporters:</p>
          <div className="flex flex-wrap justify-center gap-2">
            {recentSigners.map((signer) => (
              <span key={signer.id} className="text-white/70 text-sm">
                {signer.name}{signer.location ? ` (${signer.location})` : ''} •
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Community Section
const CommunitySection = () => {
  return (
    <section id="community" className="py-20 court-pattern" data-testid="community-section">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="font-heading text-3xl sm:text-4xl lg:text-5xl font-black text-white uppercase text-center mb-4">
          <span className="underline-red">Community</span>
        </h2>
        <p className="text-white/70 text-center mb-12 max-w-2xl mx-auto">
          Join the conversation. Help make this vision a reality.
        </p>

        <div className="grid lg:grid-cols-2 gap-12">
          <CommentsSection />
          <div>
            <EmailSignup />
            
            {/* Share CTA */}
            <div className="mt-12 p-6 bg-black rounded-md border border-[#C8102E]/30 text-center">
              <Share2 className="w-10 h-10 text-[#C8102E] mx-auto mb-4" />
              <h4 className="font-heading text-xl font-bold text-white uppercase mb-3">Share the Concept</h4>
              <p className="text-white/70 mb-4 text-sm">Help us get this in front of 2K. Every share counts.</p>
              <div className="flex justify-center gap-4">
                <button 
                  onClick={() => window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(SHARE_TEXT)}&url=${encodeURIComponent(SHARE_URL)}`, '_blank')}
                  className="share-btn"
                  data-testid="community-share-x"
                >
                  <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                </button>
                <button 
                  onClick={() => window.open(`https://reddit.com/submit?url=${encodeURIComponent(SHARE_URL)}&title=${encodeURIComponent(SHARE_TEXT)}`, '_blank')}
                  className="share-btn"
                  data-testid="community-share-reddit"
                >
                  <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current"><path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/></svg>
                </button>
                <button 
                  onClick={() => window.open('https://discord.com', '_blank')}
                  className="share-btn"
                  data-testid="community-share-discord"
                >
                  <svg viewBox="0 0 24 24" className="w-5 h-5 fill-current"><path d="M20.317 4.3698a19.7913 19.7913 0 00-4.8851-1.5152.0741.0741 0 00-.0785.0371c-.211.3753-.4447.8648-.6083 1.2495-1.8447-.2762-3.68-.2762-5.4868 0-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077 0 00-.0785-.037 19.7363 19.7363 0 00-4.8852 1.515.0699.0699 0 00-.0321.0277C.5334 9.0458-.319 13.5799.0992 18.0578a.0824.0824 0 00.0312.0561c2.0528 1.5076 4.0413 2.4228 5.9929 3.0294a.0777.0777 0 00.0842-.0276c.4616-.6304.8731-1.2952 1.226-1.9942a.076.076 0 00-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077 0 01-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743 0 01.0776-.0105c3.9278 1.7933 8.18 1.7933 12.0614 0a.0739.0739 0 01.0785.0095c.1202.099.246.1981.3728.2924a.077.077 0 01-.0066.1276 12.2986 12.2986 0 01-1.873.8914.0766.0766 0 00-.0407.1067c.3604.698.7719 1.3628 1.225 1.9932a.076.076 0 00.0842.0286c1.961-.6067 3.9495-1.5219 6.0023-3.0294a.077.077 0 00.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061 0 00-.0312-.0286zM8.02 15.3312c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9555-2.4189 2.157-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.9555 2.4189-2.1569 2.4189zm7.9748 0c-1.1825 0-2.1569-1.0857-2.1569-2.419 0-1.3332.9554-2.4189 2.1569-2.4189 1.2108 0 2.1757 1.0952 2.1568 2.419 0 1.3332-.946 2.4189-2.1568 2.4189Z"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

// Footer
const Footer = () => {
  return (
    <footer className="py-8 bg-black border-t border-white/10" data-testid="footer">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p className="text-white/40 text-sm">
          Fan-Made Concept • Not Affiliated with 2K Sports or Take-Two Interactive
        </p>
        <a href="/admin" className="text-white/20 text-xs hover:text-[#C8102E] mt-2 inline-block" data-testid="admin-link">
          Admin
        </a>
      </div>
    </footer>
  );
};

// Mobile Bottom Nav
const MobileBottomNav = () => {
  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <nav className="mobile-nav md:hidden py-2 px-4" data-testid="mobile-bottom-nav">
      <div className="flex justify-around items-center">
        <button onClick={() => scrollTo('hero')} className="flex flex-col items-center gap-1 p-2 text-white/70 hover:text-[#C8102E]" data-testid="mobile-nav-home">
          <Home size={20} />
          <span className="text-xs">Home</span>
        </button>
        <button onClick={() => scrollTo('games')} className="flex flex-col items-center gap-1 p-2 text-white/70 hover:text-[#C8102E]" data-testid="mobile-nav-games">
          <Gamepad2 size={20} />
          <span className="text-xs">Games</span>
        </button>
        <button onClick={() => scrollTo('vault')} className="flex flex-col items-center gap-1 p-2 text-white/70 hover:text-[#C8102E]" data-testid="mobile-nav-vault">
          <Lock size={20} />
          <span className="text-xs">Vault</span>
        </button>
        <button onClick={() => scrollTo('community')} className="flex flex-col items-center gap-1 p-2 text-white/70 hover:text-[#C8102E]" data-testid="mobile-nav-community">
          <Users size={20} />
          <span className="text-xs">Community</span>
        </button>
      </div>
    </nav>
  );
};

// Main Landing Page
const LandingPage = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const response = await axios.get(`${API}/games`);
        setGames(response.data);
      } catch (error) {
        console.error('Error fetching games:', error);
      }
      setLoading(false);
    };
    fetchGames();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black pb-16 md:pb-0">
      <Header />
      <HeroSection />
      <GamesSection games={games} />
      <VaultSection />
      <CommunitySection />
      <Footer />
      <MobileBottomNav />
    </div>
  );
};

export default LandingPage;
