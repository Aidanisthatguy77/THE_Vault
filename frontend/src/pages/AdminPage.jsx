import { useState, useEffect } from "react";
import axios from "axios";
import { Lock, LogOut, Plus, Pencil, Trash2, Eye, EyeOff, ArrowLeft, Users, Mail, Gamepad2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
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
                data-testid="game-title-input"
              />
            </div>
            <div>
              <label className="text-white/70 text-sm mb-1 block">Year *</label>
              <Input
                placeholder="2026"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: e.target.value })}
                className="bg-black border-white/20 text-white"
                data-testid="game-year-input"
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
              data-testid="game-image-input"
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
              data-testid="game-hook-input"
            />
          </div>

          <div>
            <label className="text-white/70 text-sm mb-1 block">Cover Athletes</label>
            <Input
              placeholder="Player Name + Special Edition"
              value={formData.cover_athletes}
              onChange={(e) => setFormData({ ...formData, cover_athletes: e.target.value })}
              className="bg-black border-white/20 text-white"
              data-testid="game-athletes-input"
            />
          </div>

          <div>
            <label className="text-white/70 text-sm mb-1 block">Description</label>
            <Textarea
              placeholder="Full description of the game and its features..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="bg-black border-white/20 text-white min-h-[120px]"
              data-testid="game-description-input"
            />
          </div>

          <div>
            <label className="text-white/70 text-sm mb-1 block">YouTube Embed URL</label>
            <Input
              placeholder="https://www.youtube.com/embed/..."
              value={formData.youtube_embed}
              onChange={(e) => setFormData({ ...formData, youtube_embed: e.target.value })}
              className="bg-black border-white/20 text-white"
              data-testid="game-youtube-input"
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
                data-testid="game-order-input"
              />
            </div>
            <div className="flex items-center gap-2 pt-6">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 accent-[#C8102E]"
                data-testid="game-active-checkbox"
              />
              <label className="text-white/70">Active (visible on site)</label>
            </div>
          </div>

          <DialogFooter className="pt-4">
            <Button type="button" variant="outline" onClick={onClose} className="border-white/20 text-white hover:bg-white/10">
              Cancel
            </Button>
            <Button type="submit" disabled={loading} className="btn-primary" data-testid="save-game-btn">
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
        <h2 className="font-heading text-2xl font-bold text-white uppercase">Manage Games</h2>
        <Button onClick={() => { setEditGame(null); setShowForm(true); }} className="btn-primary" data-testid="add-game-btn">
          <Plus size={18} className="mr-2" /> Add Game
        </Button>
      </div>

      <div className="space-y-4">
        {games.length === 0 ? (
          <p className="text-white/50 text-center py-8">No games yet. Add your first game!</p>
        ) : (
          games.map((game) => (
            <div key={game.id} className={`bg-black p-4 rounded-md border ${game.is_active ? 'border-white/10' : 'border-white/5 opacity-60'} flex items-center gap-4`} data-testid={`admin-game-${game.id}`}>
              <img src={game.cover_image} alt={game.title} className="w-16 h-20 object-cover rounded" />
              <div className="flex-1 min-w-0">
                <h3 className="font-heading text-lg font-bold text-white">{game.title}</h3>
                <p className="text-white/60 text-sm">{game.year} • Order: {game.order}</p>
                <p className="text-[#C8102E] text-sm truncate">{game.hook_text}</p>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon" onClick={() => toggleActive(game)} className="text-white/60 hover:text-white" data-testid={`toggle-active-${game.id}`}>
                  {game.is_active ? <Eye size={18} /> : <EyeOff size={18} />}
                </Button>
                <Button variant="ghost" size="icon" onClick={() => { setEditGame(game); setShowForm(true); }} className="text-white/60 hover:text-white" data-testid={`edit-game-${game.id}`}>
                  <Pencil size={18} />
                </Button>
                <Button variant="ghost" size="icon" onClick={() => setDeleteConfirm(game)} className="text-white/60 hover:text-[#C8102E]" data-testid={`delete-game-${game.id}`}>
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

      {/* Delete Confirmation */}
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
            <Button onClick={() => handleDelete(deleteConfirm?.id)} className="bg-[#C8102E] hover:bg-red-700" data-testid="confirm-delete-btn">
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Subscriptions List
const SubscriptionsList = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSubs = async () => {
      try {
        const response = await axios.get(`${API}/subscriptions`);
        setSubscriptions(response.data);
      } catch (error) {
        console.error('Error:', error);
      }
      setLoading(false);
    };
    fetchSubs();
  }, []);

  if (loading) {
    return <div className="spinner mx-auto mt-8"></div>;
  }

  return (
    <div data-testid="subscriptions-list">
      <h2 className="font-heading text-2xl font-bold text-white uppercase mb-6">Email Subscribers</h2>
      <p className="text-white/60 mb-4">Total: {subscriptions.length} subscribers</p>
      
      {subscriptions.length === 0 ? (
        <p className="text-white/50 text-center py-8">No subscribers yet.</p>
      ) : (
        <div className="bg-black rounded-md border border-white/10 overflow-hidden">
          <table className="w-full">
            <thead className="bg-[#09090B]">
              <tr>
                <th className="text-left text-white/70 font-medium p-3">Email</th>
                <th className="text-left text-white/70 font-medium p-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {subscriptions.map((sub) => (
                <tr key={sub.id} className="border-t border-white/5">
                  <td className="text-white p-3">{sub.email}</td>
                  <td className="text-white/60 p-3">{new Date(sub.subscribed_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// Main Admin Page
const AdminPage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('games');

  // Check if already logged in (session storage)
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

  return (
    <div className="min-h-screen bg-black" data-testid="admin-dashboard">
      {/* Header */}
      <header className="bg-[#09090B] border-b border-white/10 py-4 px-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a href="/" className="text-white/60 hover:text-white flex items-center gap-2" data-testid="back-to-site">
              <ArrowLeft size={18} />
              <span className="hidden sm:inline">Back to Site</span>
            </a>
            <div className="w-px h-6 bg-white/10"></div>
            <h1 className="font-heading text-xl font-bold text-white uppercase">Admin Panel</h1>
          </div>
          <Button variant="ghost" onClick={handleLogout} className="text-white/60 hover:text-white" data-testid="logout-btn">
            <LogOut size={18} className="mr-2" /> Logout
          </Button>
        </div>
      </header>

      {/* Content */}
      <div className="max-w-7xl mx-auto p-6">
        {/* Tabs */}
        <div className="flex gap-4 mb-8 border-b border-white/10 pb-4">
          <button
            onClick={() => setActiveTab('games')}
            className={`flex items-center gap-2 px-4 py-2 rounded-sm font-medium transition-colors ${activeTab === 'games' ? 'bg-[#C8102E] text-white' : 'text-white/60 hover:text-white'}`}
            data-testid="tab-games"
          >
            <Gamepad2 size={18} /> Games
          </button>
          <button
            onClick={() => setActiveTab('subscribers')}
            className={`flex items-center gap-2 px-4 py-2 rounded-sm font-medium transition-colors ${activeTab === 'subscribers' ? 'bg-[#C8102E] text-white' : 'text-white/60 hover:text-white'}`}
            data-testid="tab-subscribers"
          >
            <Mail size={18} /> Subscribers
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === 'games' && <GamesManagement />}
        {activeTab === 'subscribers' && <SubscriptionsList />}
      </div>
    </div>
  );
};

export default AdminPage;
