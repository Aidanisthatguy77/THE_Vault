import { useState, useEffect } from "react";
import axios from "axios";
import { Lock, LogOut, Plus, Pencil, Trash2, Eye, EyeOff, ArrowLeft, Users, Mail, Gamepad2, MessageSquare, Trophy, RefreshCw, UserPlus, Video, Youtube, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Admin Login
const AdminLogin = ({ onLogin }) => {
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API}/admin/login`, { password });
      onLogin();
      toast.success("Login successful!");
    } catch (error) {
      toast.error("Invalid password");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4" data-testid="admin-login">
      <div className="w-full max-w-md bg-[#09090B] p-8 rounded-md border border-white/10">
        <div className="text-center mb-8">
          <Lock className="w-12 h-12 text-[#C8102E] mx-auto mb-4" />
          <h1 className="font-heading text-2xl font-bold text-white uppercase">Admin Access</h1>
          <p className="text-white/60 mt-2">Enter admin password to continue</p>
        </div>
        
        <form onSubmit={handleSubmit}>
          <Input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="bg-black border-white/20 text-white mb-4"
            data-testid="admin-password-input"
          />
          <Button 
            type="submit" 
            disabled={loading}
            className="w-full btn-primary"
            data-testid="admin-login-btn"
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <a href="/" className="text-white/40 text-sm hover:text-[#C8102E] mt-6 block text-center">
          ← Back to site
        </a>
      </div>
    </div>
  );
};

// Game Form Modal
const GameFormModal = ({ game, open, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: '',
    year: '',
    cover_image: '',
    hook_text: '',
    cover_athletes: '',
    description: '',
    youtube_embed: '',
    order: 0,
    is_active: true
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (game) {
      setFormData({
        title: game.title || '',
        year: game.year || '',
        cover_image: game.cover_image || '',
        hook_text: game.hook_text || '',
        cover_athletes: game.cover_athletes || '',
        description: game.description || '',
        youtube_embed: game.youtube_embed || '',
        order: game.order || 0,
        is_active: game.is_active !== false
      });
    } else {
      setFormData({
        title: '',
        year: '',
        cover_image: '',
        hook_text: '',
        cover_athletes: '',
        description: '',
        youtube_embed: '',
        order: 0,
        is_active: true
      });
    }
  }, [game, open]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || !formData.year) {
      toast.error("Title and year are required");
      return;
    }

    setLoading(true);
    try {
      if (game) {
        await axios.put(`${API}/games/${game.id}`, formData);
        toast.success("Game updated!");
      } else {
        await axios.post(`${API}/games`, formData);
        toast.success("Game created!");
      }
      onSave();
      onClose();
    } catch (error) {
      toast.error("Failed to save game");
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-[#09090B] border-white/10 max-w-2xl max-h-[90vh] overflow-y-auto" data-testid="game-form-modal">
        <DialogHeader>
          <DialogTitle className="font-heading text-2xl font-bold text-white uppercase">
            {game ? 'Edit Game' : 'Add New Game'}
          </DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 mt-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="text-white/70 text-sm mb-1 block">Title *</label>
              <Input
                placeholder="NBA 2K27"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="bg-black border-white/20 text-white"
              />
            </div>
            <div>
              <label className="text-white/70 text-sm mb-1 block">Year *</label>
              <Input
                placeholder="2026"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                className="bg-black border-white/20 text-white"
              />
            </div>
          </div>

          <div>
            <label className="text-white/70 text-sm mb-1 block">Cover Image URL</label>
            <Input
              placeholder="https://example.com/cover.jpg"
              value={formData.cover_image}
              onChange={(e) => setFormData({ ...formData, cover_image: e.target.value })}
              className="bg-black border-white/20 text-white"
            />
            {formData.cover_image && (
              <img src={formData.cover_image} alt="Preview" className="mt-2 w-32 h-auto rounded" />
            )}
          </div>

          <div>
            <label className="text-white/70 text-sm mb-1 block">Hook Text (short tagline)</label>
            <Input
              placeholder="The newest era continues"
              value={formData.hook_text}
              onChange={(e) => setFormData({ ...formData, hook_text: e.target.value })}
              className="bg-black border-white/20 text-white"
            />
          </div>

          <div>
            <label className="text-white/70 text-sm mb-1 block">Cover Athletes</label>
            <Input
              placeholder="Player Name + Special Edition"
              value={formData.cover_athletes}
              onChange={(e) => setFormData({ ...formData, cover_athletes: e.target.value })}
              className="bg-black border-white/20 text-white"
            />
          </div>

          <div>
            <label className="text-white/70 text-sm mb-1 block">Description</label>
            <Textarea
              placeholder="Full description of the game and its features..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="bg-black border-white/20 text-white min-h-[120px]"
            />
          </div>

          <div>
            <label className="text-white/70 text-sm mb-1 block">Main YouTube Embed URL (optional)</label>
            <Input
              placeholder="https://www.youtube.com/embed/..."
              value={formData.youtube_embed}
              onChange={(e) => setFormData({ ...formData, youtube_embed: e.target.value })}
              className="bg-black border-white/20 text-white"
            />
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="text-white/70 text-sm mb-1 block">Display Order</label>
              <Input
                type="number"
                value={formData.order}
                onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 0 })}
                className="bg-black border-white/20 text-white"
              />
            </div>
            <div className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 accent-[#C8102E]"
              />
              <label className="text-white/70">Active (visible on site)</label>
            </div>
          </div>

          <DialogFooter className="pt-4">
            <Button type="button" variant="outline" onClick={onClose} className="border-white/20 text-white hover:bg-white/10">
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Saving...' : (game ? 'Update Game' : 'Create Game')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

// Games Management
const GamesManagement = () => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editGame, setEditGame] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const fetchGames = async () => {
    try {
      const response = await axios.get(`${API}/games/all`);
      setGames(response.data);
    } catch (error) {
      toast.error("Failed to fetch games");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchGames();
  }, []);

  const handleDelete = async (gameId) => {
    try {
      await axios.delete(`${API}/games/${gameId}`);
      toast.success("Game deleted!");
      fetchGames();
    } catch (error) {
      toast.error("Failed to delete game");
    }
    setDeleteConfirm(null);
  };

  const toggleActive = async (game) => {
    try {
      await axios.put(`${API}/games/${game.id}`, { is_active: !game.is_active });
      toast.success(game.is_active ? "Game hidden" : "Game activated");
      fetchGames();
    } catch (error) {
      toast.error("Failed to update game");
    }
  };

  if (loading) {
    return <div className="spinner mx-auto mt-8"></div>;
  }

  return (
    <div data-testid="games-management">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-heading text-2xl font-bold text-white uppercase">Manage Games ({games.length})</h2>
        <Button onClick={() => { setEditGame(null); setShowForm(true); }} className="btn-primary">
          <Plus size={18} className="mr-2" /> Add Game
        </Button>
      </div>

      <div className="space-y-4">
        {games.length === 0 ? (
          <p className="text-white/50 text-center py-8">No games yet. Add your first game!</p>
        ) : (
          games.map((game) => (
            <div key={game.id} className={`bg-black p-4 rounded-md border ${game.is_active ? 'border-white/10' : 'border-white/5 opacity-60'} flex items-center gap-4`}>
              <img src={game.cover_image} alt={game.title} className="w-16 h-20 object-cover rounded" />
              <div className="flex-1 min-w-0">
                <h3 className="font-heading text-lg font-bold text-white">{game.title}</h3>
                <p className="text-white/60 text-sm">{game.year} • Order: {game.order}</p>
                <p className="text-[#C8102E] text-sm truncate">{game.hook_text}</p>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={() => toggleActive(game)} className="text-white/60 hover:text-white">
                  {game.is_active ? <Eye size={18} /> : <EyeOff size={18} />}
                </Button>
                <Button variant="ghost" size="icon" onClick={() => { setEditGame(game); setShowForm(true); }} className="text-white/60 hover:text-white">
                  <Pencil size={18} />
                </Button>
                <Button variant="ghost" size="icon" onClick={() => setDeleteConfirm(game)} className="text-white/60 hover:text-[#C8102E]">
                  <Trash2 size={18} />
                </Button>
              </div>
            </div>
          ))
        )}
      </div>

      <GameFormModal
        game={editGame}
        open={showForm}
        onClose={() => { setShowForm(false); setEditGame(null); }}
        onSave={fetchGames}
      />

      <Dialog open={!!deleteConfirm} onOpenChange={() => setDeleteConfirm(null)}>
        <DialogContent className="bg-[#09090B] border-white/10">
          <DialogHeader>
            <DialogTitle className="text-white">Delete Game?</DialogTitle>
          </DialogHeader>
          <p className="text-white/70">Are you sure you want to delete "{deleteConfirm?.title}"? This action cannot be undone.</p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirm(null)} className="border-white/20 text-white hover:bg-white/10">
              Cancel
            </Button>
            <Button onClick={() => handleDelete(deleteConfirm?.id)} className="bg-[#C8102E] hover:bg-red-700">
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Clips Management - NEW!
const ClipsManagement = () => {
  const [games, setGames] = useState([]);
  const [clips, setClips] = useState([]);
  const [selectedGame, setSelectedGame] = useState('all');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editClip, setEditClip] = useState(null);
  const [formData, setFormData] = useState({
    game_id: '',
    title: '',
    platform: 'youtube',
    embed_url: '',
    description: '',
    order: 0
  });

  const fetchData = async () => {
    try {
      const [gamesRes, clipsRes] = await Promise.all([
        axios.get(`${API}/games/all`),
        axios.get(`${API}/clips`)
      ]);
      setGames(gamesRes.data);
      setClips(clipsRes.data);
    } catch (error) {
      toast.error("Failed to fetch data");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredClips = selectedGame === 'all' 
    ? clips 
    : clips.filter(c => c.game_id === selectedGame);

  const getGameTitle = (gameId) => {
    const game = games.find(g => g.id === gameId);
    return game ? game.title : 'Unknown Game';
  };

  const getPlatformIcon = (platform) => {
    switch(platform) {
      case 'youtube': return <Youtube size={16} className="text-red-500" />;
      case 'tiktok': return <Play size={16} className="text-pink-500" />;
      default: return <Video size={16} className="text-white/60" />;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.game_id || !formData.title || !formData.embed_url) {
      toast.error("Game, title, and embed URL are required");
      return;
    }

    try {
      if (editClip) {
        await axios.put(`${API}/clips/${editClip.id}`, formData);
        toast.success("Clip updated!");
      } else {
        await axios.post(`${API}/clips`, formData);
        toast.success("Clip added!");
      }
      setShowForm(false);
      setEditClip(null);
      setFormData({ game_id: '', title: '', platform: 'youtube', embed_url: '', description: '', order: 0 });
      fetchData();
    } catch (error) {
      toast.error("Failed to save clip");
    }
  };

  const handleEdit = (clip) => {
    setEditClip(clip);
    setFormData({
      game_id: clip.game_id,
      title: clip.title,
      platform: clip.platform,
      embed_url: clip.embed_url,
      description: clip.description || '',
      order: clip.order || 0
    });
    setShowForm(true);
  };

  const handleDelete = async (clipId) => {
    if (!window.confirm("Delete this clip?")) return;
    try {
      await axios.delete(`${API}/clips/${clipId}`);
      toast.success("Clip deleted!");
      fetchData();
    } catch (error) {
      toast.error("Failed to delete clip");
    }
  };

  const openAddForm = () => {
    setEditClip(null);
    setFormData({ 
      game_id: selectedGame !== 'all' ? selectedGame : '', 
      title: '', 
      platform: 'youtube', 
      embed_url: '', 
      description: '', 
      order: 0 
    });
    setShowForm(true);
  };

  if (loading) {
    return <div className="spinner mx-auto mt-8"></div>;
  }

  return (
    <div data-testid="clips-management">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 className="font-heading text-2xl font-bold text-white uppercase">Media & Clips ({clips.length})</h2>
          <p className="text-white/60 text-sm">Add YouTube, TikTok, Instagram clips for each game</p>
        </div>
        <Button onClick={openAddForm} className="btn-primary">
          <Plus size={18} className="mr-2" /> Add Clip
        </Button>
      </div>

      {/* Filter by Game */}
      <div className="mb-6 flex items-center gap-3">
        <span className="text-white/70">Filter by game:</span>
        <Select value={selectedGame} onValueChange={setSelectedGame}>
          <SelectTrigger className="w-[200px] bg-black border-white/20 text-white">
            <SelectValue placeholder="All Games" />
          </SelectTrigger>
          <SelectContent className="bg-[#09090B] border-white/10">
            <SelectItem value="all" className="text-white hover:bg-white/10">All Games</SelectItem>
            {games.map(game => (
              <SelectItem key={game.id} value={game.id} className="text-white hover:bg-white/10">
                {game.title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* How to get embed URLs */}
      <div className="bg-[#09090B] p-4 rounded-md border border-white/10 mb-6">
        <h3 className="font-heading text-lg font-bold text-white uppercase mb-2">How to Add Clips</h3>
        <div className="text-white/70 text-sm space-y-2">
          <p><strong className="text-[#C8102E]">YouTube:</strong> Go to video → Share → Embed → Copy the URL from src="..."</p>
          <p className="text-white/50 text-xs">Example: https://www.youtube.com/embed/VIDEO_ID</p>
          <p><strong className="text-[#C8102E]">TikTok:</strong> Go to video → Share → Embed → Copy the video URL</p>
          <p className="text-white/50 text-xs">Example: https://www.tiktok.com/embed/v2/VIDEO_ID</p>
          <p><strong className="text-[#C8102E]">Instagram:</strong> Go to post → ⋯ → Embed → Copy URL</p>
          <p><strong className="text-[#C8102E]">Twitter/X:</strong> Use the tweet URL directly</p>
        </div>
      </div>

      {/* Clips List */}
      {filteredClips.length === 0 ? (
        <p className="text-white/50 text-center py-8">No clips yet. Add your first clip!</p>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredClips.map(clip => (
            <div key={clip.id} className="bg-black p-4 rounded-md border border-white/10">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {getPlatformIcon(clip.platform)}
                  <span className="text-white/60 text-xs uppercase">{clip.platform}</span>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" onClick={() => handleEdit(clip)} className="h-6 w-6 text-white/60 hover:text-white">
                    <Pencil size={14} />
                  </Button>
                  <Button variant="ghost" size="icon" onClick={() => handleDelete(clip.id)} className="h-6 w-6 text-white/60 hover:text-[#C8102E]">
                    <Trash2 size={14} />
                  </Button>
                </div>
              </div>
              <h4 className="font-bold text-white mb-1">{clip.title}</h4>
              <p className="text-[#C8102E] text-xs mb-2">{getGameTitle(clip.game_id)}</p>
              {clip.description && (
                <p className="text-white/60 text-sm mb-2 line-clamp-2">{clip.description}</p>
              )}
              <div className="aspect-video bg-[#09090B] rounded overflow-hidden">
                <iframe
                  src={clip.embed_url}
                  title={clip.title}
                  className="w-full h-full"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                ></iframe>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Clip Modal */}
      <Dialog open={showForm} onOpenChange={() => { setShowForm(false); setEditClip(null); }}>
        <DialogContent className="bg-[#09090B] border-white/10 max-w-lg">
          <DialogHeader>
            <DialogTitle className="font-heading text-2xl font-bold text-white uppercase">
              {editClip ? 'Edit Clip' : 'Add New Clip'}
            </DialogTitle>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-4 mt-4">
            <div>
              <label className="text-white/70 text-sm mb-1 block">Game *</label>
              <Select value={formData.game_id} onValueChange={(v) => setFormData({...formData, game_id: v})}>
                <SelectTrigger className="bg-black border-white/20 text-white">
                  <SelectValue placeholder="Select a game" />
                </SelectTrigger>
                <SelectContent className="bg-[#09090B] border-white/10">
                  {games.map(game => (
                    <SelectItem key={game.id} value={game.id} className="text-white hover:bg-white/10">
                      {game.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-white/70 text-sm mb-1 block">Platform *</label>
              <Select value={formData.platform} onValueChange={(v) => setFormData({...formData, platform: v})}>
                <SelectTrigger className="bg-black border-white/20 text-white">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#09090B] border-white/10">
                  <SelectItem value="youtube" className="text-white hover:bg-white/10">YouTube</SelectItem>
                  <SelectItem value="tiktok" className="text-white hover:bg-white/10">TikTok</SelectItem>
                  <SelectItem value="instagram" className="text-white hover:bg-white/10">Instagram</SelectItem>
                  <SelectItem value="twitter" className="text-white hover:bg-white/10">Twitter/X</SelectItem>
                  <SelectItem value="other" className="text-white hover:bg-white/10">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <label className="text-white/70 text-sm mb-1 block">Title *</label>
              <Input
                placeholder="Epic dunk compilation"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                className="bg-black border-white/20 text-white"
              />
            </div>

            <div>
              <label className="text-white/70 text-sm mb-1 block">Embed URL *</label>
              <Input
                placeholder="https://www.youtube.com/embed/..."
                value={formData.embed_url}
                onChange={(e) => setFormData({...formData, embed_url: e.target.value})}
                className="bg-black border-white/20 text-white"
              />
            </div>

            <div>
              <label className="text-white/70 text-sm mb-1 block">Description (optional)</label>
              <Textarea
                placeholder="What's in this clip..."
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="bg-black border-white/20 text-white min-h-[80px]"
              />
            </div>

            <div>
              <label className="text-white/70 text-sm mb-1 block">Display Order</label>
              <Input
                type="number"
                value={formData.order}
                onChange={(e) => setFormData({...formData, order: parseInt(e.target.value) || 0})}
                className="bg-black border-white/20 text-white w-24"
              />
            </div>

            <DialogFooter className="pt-4">
              <Button type="button" variant="outline" onClick={() => setShowForm(false)} className="border-white/20 text-white hover:bg-white/10">
                Cancel
              </Button>
              <Button type="submit" className="btn-primary">
                {editClip ? 'Update Clip' : 'Add Clip'}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Comments Management
const CommentsManagement = () => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchComments = async () => {
    try {
      const response = await axios.get(`${API}/comments`);
      setComments(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchComments();
  }, []);

  const handleDelete = async (commentId) => {
    if (!window.confirm("Delete this comment and all its replies?")) return;
    try {
      await axios.delete(`${API}/comments/${commentId}`);
      toast.success("Comment deleted!");
      fetchComments();
    } catch (error) {
      toast.error("Failed to delete comment");
    }
  };

  if (loading) {
    return <div className="spinner mx-auto mt-8"></div>;
  }

  const totalComments = comments.reduce((acc, c) => acc + 1 + (c.replies?.length || 0), 0);

  return (
    <div data-testid="comments-management">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-heading text-2xl font-bold text-white uppercase">Manage Comments ({totalComments})</h2>
        <Button onClick={fetchComments} variant="outline" className="border-white/20 text-white hover:bg-white/10">
          <RefreshCw size={18} className="mr-2" /> Refresh
        </Button>
      </div>

      {comments.length === 0 ? (
        <p className="text-white/50 text-center py-8">No comments yet.</p>
      ) : (
        <div className="space-y-4">
          {comments.map((comment) => (
            <div key={comment.id} className="bg-black p-4 rounded-md border border-white/10">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-white">{comment.author_name}</span>
                    <span className="text-white/40 text-sm">{new Date(comment.created_at).toLocaleString()}</span>
                  </div>
                  <p className="text-white/80">{comment.content}</p>
                </div>
                <Button variant="ghost" size="icon" onClick={() => handleDelete(comment.id)} className="text-white/60 hover:text-[#C8102E]">
                  <Trash2 size={18} />
                </Button>
              </div>

              {comment.replies && comment.replies.length > 0 && (
                <div className="mt-3 ml-6 space-y-2 border-l-2 border-[#C8102E]/30 pl-4">
                  {comment.replies.map((reply) => (
                    <div key={reply.id} className="flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-sm">{reply.author_name}</span>
                          <span className="text-white/40 text-xs">{new Date(reply.created_at).toLocaleString()}</span>
                        </div>
                        <p className="text-white/70 text-sm">{reply.content}</p>
                      </div>
                      <Button variant="ghost" size="icon" onClick={() => handleDelete(reply.id)} className="text-white/60 hover:text-[#C8102E] h-6 w-6">
                        <Trash2 size={14} />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Subscriptions Management
const SubscriptionsManagement = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSubs = async () => {
    try {
      const response = await axios.get(`${API}/subscriptions`);
      setSubscriptions(response.data);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchSubs();
  }, []);

  const handleDelete = async (subId) => {
    if (!window.confirm("Delete this subscription?")) return;
    try {
      await axios.delete(`${API}/subscriptions/${subId}`);
      toast.success("Subscription deleted!");
      fetchSubs();
    } catch (error) {
      toast.error("Failed to delete subscription");
    }
  };

  const exportEmails = () => {
    const emails = subscriptions.map(s => s.email).join('\n');
    const blob = new Blob([emails], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'legacy-vault-subscribers.txt';
    a.click();
    toast.success("Emails exported!");
  };

  if (loading) {
    return <div className="spinner mx-auto mt-8"></div>;
  }

  return (
    <div data-testid="subscriptions-management">
      <div className="flex justify-between items-center mb-6">
        <h2 className="font-heading text-2xl font-bold text-white uppercase">Email Subscribers ({subscriptions.length})</h2>
        <Button onClick={exportEmails} className="btn-primary" disabled={subscriptions.length === 0}>
          Export Emails
        </Button>
      </div>
      
      {subscriptions.length === 0 ? (
        <p className="text-white/50 text-center py-8">No subscribers yet.</p>
      ) : (
        <div className="bg-black rounded-md border border-white/10 overflow-hidden">
          <table className="w-full">
            <thead className="bg-[#09090B]">
              <tr>
                <th className="text-left text-white/70 font-medium p-3">Email</th>
                <th className="text-left text-white/70 font-medium p-3">Date</th>
                <th className="text-right text-white/70 font-medium p-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {subscriptions.map((sub) => (
                <tr key={sub.id} className="border-t border-white/5">
                  <td className="text-white p-3">{sub.email}</td>
                  <td className="text-white/60 p-3">{new Date(sub.subscribed_at).toLocaleDateString()}</td>
                  <td className="text-right p-3">
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(sub.id)} className="text-white/60 hover:text-[#C8102E]">
                      <Trash2 size={16} />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Petition Management
const PetitionManagement = () => {
  const [signatures, setSignatures] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [bulkCount, setBulkCount] = useState(100);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newSig, setNewSig] = useState({ name: '', location: '' });

  const fetchData = async () => {
    try {
      const [sigsRes, countRes] = await Promise.all([
        axios.get(`${API}/petition/signatures`),
        axios.get(`${API}/petition/count`)
      ]);
      setSignatures(sigsRes.data);
      setCount(countRes.data.count);
    } catch (error) {
      console.error('Error:', error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDelete = async (sigId) => {
    if (!window.confirm("Delete this signature?")) return;
    try {
      await axios.delete(`${API}/petition/${sigId}`);
      toast.success("Signature deleted!");
      fetchData();
    } catch (error) {
      toast.error("Failed to delete signature");
    }
  };

  const handleAddBulk = async () => {
    try {
      await axios.post(`${API}/petition/add-bulk?count=${bulkCount}`);
      toast.success(`Added ${bulkCount} signatures!`);
      fetchData();
    } catch (error) {
      toast.error("Failed to add signatures");
    }
  };

  const handleAddSingle = async (e) => {
    e.preventDefault();
    if (!newSig.name.trim()) {
      toast.error("Name is required");
      return;
    }
    try {
      await axios.post(`${API}/petition/sign`, { name: newSig.name, location: newSig.location || null });
      toast.success("Signature added!");
      setNewSig({ name: '', location: '' });
      setShowAddForm(false);
      fetchData();
    } catch (error) {
      toast.error("Failed to add signature");
    }
  };

  if (loading) {
    return <div className="spinner mx-auto mt-8"></div>;
  }

  return (
    <div data-testid="petition-management">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="font-heading text-2xl font-bold text-white uppercase">Petition Signatures</h2>
          <p className="text-[#C8102E] font-heading text-3xl font-black">{count.toLocaleString()}+ supporters</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setShowAddForm(true)} variant="outline" className="border-white/20 text-white hover:bg-white/10">
            <UserPlus size={18} className="mr-2" /> Add Single
          </Button>
        </div>
      </div>

      <div className="bg-[#09090B] p-4 rounded-md border border-[#C8102E]/30 mb-6">
        <h3 className="font-heading text-lg font-bold text-white uppercase mb-3">Boost Social Proof</h3>
        <p className="text-white/60 text-sm mb-4">Add signatures to boost the counter</p>
        <div className="flex gap-3 items-center">
          <Input
            type="number"
            value={bulkCount}
            onChange={(e) => setBulkCount(parseInt(e.target.value) || 0)}
            className="bg-black border-white/20 text-white w-32"
            min={1}
            max={10000}
          />
          <Button onClick={handleAddBulk} className="btn-primary">
            Add {bulkCount} Signatures
          </Button>
        </div>
      </div>

      <h3 className="font-heading text-lg font-bold text-white uppercase mb-3">Recent Signatures (showing last 50)</h3>
      {signatures.length === 0 ? (
        <p className="text-white/50 text-center py-8">No signatures yet.</p>
      ) : (
        <div className="bg-black rounded-md border border-white/10 overflow-hidden max-h-96 overflow-y-auto">
          <table className="w-full">
            <thead className="bg-[#09090B] sticky top-0">
              <tr>
                <th className="text-left text-white/70 font-medium p-3">Name</th>
                <th className="text-left text-white/70 font-medium p-3">Location</th>
                <th className="text-left text-white/70 font-medium p-3">Date</th>
                <th className="text-right text-white/70 font-medium p-3">Action</th>
              </tr>
            </thead>
            <tbody>
              {signatures.slice(0, 50).map((sig) => (
                <tr key={sig.id} className="border-t border-white/5">
                  <td className="text-white p-3">{sig.name}</td>
                  <td className="text-white/60 p-3">{sig.location || '-'}</td>
                  <td className="text-white/60 p-3">{new Date(sig.signed_at).toLocaleDateString()}</td>
                  <td className="text-right p-3">
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(sig.id)} className="text-white/60 hover:text-[#C8102E]">
                      <Trash2 size={16} />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Dialog open={showAddForm} onOpenChange={setShowAddForm}>
        <DialogContent className="bg-[#09090B] border-white/10">
          <DialogHeader>
            <DialogTitle className="text-white">Add Signature</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleAddSingle} className="space-y-4 mt-4">
            <div>
              <label className="text-white/70 text-sm mb-1 block">Name *</label>
              <Input
                placeholder="John Doe"
                value={newSig.name}
                onChange={(e) => setNewSig({ ...newSig, name: e.target.value })}
                className="bg-black border-white/20 text-white"
              />
            </div>
            <div>
              <label className="text-white/70 text-sm mb-1 block">Location (optional)</label>
              <Input
                placeholder="New York"
                value={newSig.location}
                onChange={(e) => setNewSig({ ...newSig, location: e.target.value })}
                className="bg-black border-white/20 text-white"
              />
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setShowAddForm(false)} className="border-white/20 text-white hover:bg-white/10">
                Cancel
              </Button>
              <Button type="submit" className="btn-primary">
                Add Signature
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Main Admin Page
const AdminPage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('games');

  useEffect(() => {
    const loggedIn = sessionStorage.getItem('adminLoggedIn');
    if (loggedIn === 'true') {
      setIsLoggedIn(true);
    }
  }, []);

  const handleLogin = () => {
    sessionStorage.setItem('adminLoggedIn', 'true');
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('adminLoggedIn');
    setIsLoggedIn(false);
  };

  if (!isLoggedIn) {
    return <AdminLogin onLogin={handleLogin} />;
  }

  const tabs = [
    { id: 'games', label: 'Games', icon: Gamepad2 },
    { id: 'clips', label: 'Clips', icon: Video },
    { id: 'comments', label: 'Comments', icon: MessageSquare },
    { id: 'subscribers', label: 'Subscribers', icon: Mail },
    { id: 'petition', label: 'Petition', icon: Trophy },
  ];

  return (
    <div className="min-h-screen bg-black" data-testid="admin-dashboard">
      <header className="bg-[#09090B] border-b border-white/10 py-4 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a href="/" className="text-white/60 hover:text-white flex items-center gap-2">
              <ArrowLeft size={18} />
              <span className="hidden sm:inline">Back to Site</span>
            </a>
            <div className="w-px h-6 bg-white/10"></div>
            <h1 className="font-heading text-xl font-bold text-white uppercase">Full Admin Control</h1>
          </div>
          <Button variant="ghost" onClick={handleLogout} className="text-white/60 hover:text-white">
            <LogOut size={18} className="mr-2" /> Logout
          </Button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        <div className="flex flex-wrap gap-2 mb-8 border-b border-white/10 pb-4">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-sm font-medium transition-colors ${activeTab === tab.id ? 'bg-[#C8102E] text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
            >
              <tab.icon size={18} /> {tab.label}
            </button>
          ))}
        </div>

        {activeTab === 'games' && <GamesManagement />}
        {activeTab === 'clips' && <ClipsManagement />}
        {activeTab === 'comments' && <CommentsManagement />}
        {activeTab === 'subscribers' && <SubscriptionsManagement />}
        {activeTab === 'petition' && <PetitionManagement />}
      </div>
    </div>
  );
};

export default AdminPage;
