import { useEffect, useState } from 'react';
import { Search, Plus, Edit2, Trash2, Save, X, Check, AlertCircle, RefreshCw, UploadCloud, Globe } from 'lucide-react';
import { supabase } from '../components/SupabaseClient';

export interface Stopword {
  id: number;
  stopword: string;
  is_active: boolean | null;
  created_at: string | null;
  updated_at: string | null;
  spanishkeyword: string | null;
}

const emptyStopword: Omit<Stopword, 'id' | 'created_at' | 'updated_at'> = {
  stopword: '',
  is_active: true,
  spanishkeyword: '',
};

const StopwordsPage = () => {
  const [stopwords, setStopwords] = useState<Stopword[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [newStopword, setNewStopword] = useState(emptyStopword);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editStopword, setEditStopword] = useState<Omit<Stopword, 'id' | 'created_at' | 'updated_at'>>({ ...emptyStopword });
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [syncLoading, setSyncLoading] = useState(false);

  // Clear messages after 3 seconds
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  // Fetch stopwords
  const fetchStopwords = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data, error } = await supabase
        .from('stopwords')
        .select('*')
        .order('id', { ascending: true });
      if (error) setError(error.message);
      else setStopwords(data as Stopword[]);
    } catch (err) {
      setError('Failed to fetch stopwords');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStopwords();
  }, []);

// Filter stopwords based on search
const filteredStopwords = stopwords.filter(s => 
  s.stopword.toLowerCase().includes(searchQuery.toLowerCase()) ||
  (s.spanishkeyword || '').toLowerCase().includes(searchQuery.toLowerCase())
);

  // Add stopword
  const handleAdd = async (e: React.MouseEvent) => {
    e.preventDefault();
    setError(null);
    if (!newStopword.stopword.trim()) {
      setError('Stopword is required');
      return;
    }
    try {
      const { error } = await supabase.from('stopwords').insert([newStopword]);
      if (error) setError(error.message);
      else {
        setNewStopword(emptyStopword);
        setShowAddForm(false);
        setSuccess('Stopword added successfully!');
        fetchStopwords();
      }
    } catch (err) {
      setError('Failed to add stopword');
    }
  };

  // Delete stopword
  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this stopword?')) return;
    setError(null);
    try {
      const { error } = await supabase.from('stopwords').delete().eq('id', id);
      if (error) setError(error.message);
      else {
        setSuccess('Stopword deleted successfully!');
        fetchStopwords();
      }
    } catch (err) {
      setError('Failed to delete stopword');
    }
  };

  // Start editing
  const startEdit = (stopword: Stopword) => {
    setEditingId(stopword.id);
    setEditStopword({
      stopword: stopword.stopword,
      is_active: stopword.is_active,
      spanishkeyword: stopword.spanishkeyword,
    });
  };

  // Cancel editing
  const cancelEdit = () => {
    setEditingId(null);
    setEditStopword({ ...emptyStopword });
  };

  // Save edit
  const handleEditSave = async (id: number) => {
    setError(null);
    if (!editStopword.stopword.trim()) {
      setError('Stopword is required');
      return;
    }
    try {
      const { error } = await supabase
        .from('stopwords')
        .update(editStopword)
        .eq('id', id);
      if (error) setError(error.message);
      else {
        setEditingId(null);
        setEditStopword({ ...emptyStopword });
        setSuccess('Stopword updated successfully!');
        fetchStopwords();
      }
    } catch (err) {
      setError('Failed to update stopword');
    }
  };

  // Trigger push-cigar-listings API
  const handleSyncCigarListings = async () => {
    setSyncLoading(true);
    setError(null);
    setSuccess(null);
    try {
      const resp = await fetch('http://127.0.0.1:5000/api/push-cigar-listings', { method: 'POST' });
      const data = await resp.json();
      if (resp.ok && data.success) {
        setSuccess('Cigar listings synced successfully!');
      } else {
        setError(data.error || 'Failed to sync cigar listings');
      }
    } catch (err) {
      setError('Failed to sync cigar listings');
    }
    setSyncLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Stopwords Manager
              </h1>
              <p className="text-slate-600 mt-2">Manage your stopwords for filtering listings</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-slate-800">{stopwords.length}</div>
              <div className="text-sm text-slate-500">Total Stopwords</div>
            </div>
          </div>

          {/* Search, Add, and Sync Bar */}
          <div className="flex gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search stopwords..."
                className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 flex items-center gap-2 font-medium shadow-lg hover:shadow-xl"
            >
              <Plus className="w-5 h-5" />
              Add Stopword
            </button>
            <button
              onClick={handleSyncCigarListings}
              disabled={syncLoading}
              className={`bg-gradient-to-r from-green-600 to-blue-600 text-white px-6 py-3 rounded-xl flex items-center gap-2 font-medium shadow-lg hover:shadow-xl transition-all duration-200 ${syncLoading ? 'opacity-60 cursor-not-allowed' : 'hover:from-green-700 hover:to-blue-700'}`}
            >
              <UploadCloud className="w-5 h-5" />
              {syncLoading ? 'Syncing...' : 'Sync Cigar Listings'}
            </button>
          </div>
        </div>

        {/* Messages */}
        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded-r-xl">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-red-400 mr-2" />
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}
        {success && (
          <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6 rounded-r-xl">
            <div className="flex items-center">
              <Check className="w-5 h-5 text-green-400 mr-2" />
              <p className="text-green-700">{success}</p>
            </div>
          </div>
        )}

        {/* Add Form */}
        {showAddForm && (
          <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-6 mb-8">
            <h3 className="text-xl font-semibold text-slate-800 mb-4">Add New Stopword</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      English Stopword *
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      value={newStopword.stopword}
                      onChange={e => setNewStopword({ ...newStopword, stopword: e.target.value })}
                      placeholder="Enter stopword..."
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Spanish Translation
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                      value={newStopword.spanishkeyword || ''}
                      onChange={e => setNewStopword({ ...newStopword, spanishkeyword: e.target.value })}
                      placeholder="Enter Spanish translation..."
                    />
                  </div>
                </div>
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={!!newStopword.is_active}
                    onChange={e => setNewStopword({ ...newStopword, is_active: e.target.checked })}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  Active stopword
                </label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="px-4 py-2 text-slate-600 hover:text-slate-800 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      handleAdd(e);
                    }}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 font-medium"
                  >
                    Add Stopword
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Stopwords Grid */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
          ) : filteredStopwords.length === 0 ? (
            <div className="text-center py-16">
              <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-slate-600 mb-2">
                {searchQuery ? 'No matching stopwords' : 'No stopwords yet'}
              </h3>
              <p className="text-slate-500">
                {searchQuery ? 'Try adjusting your search terms' : 'Add your first stopword to get started'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 p-6">
              {filteredStopwords.map(stopword => (
                <div
                  key={stopword.id}
                  className="bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 p-6 hover:shadow-lg transition-all duration-200"
                >
                  {editingId === stopword.id ? (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-2">English</label>
                        <input
                          type="text"
                          className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                          value={editStopword.stopword}
                          onChange={e => setEditStopword({ ...editStopword, stopword: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-2">Spanish</label>
                        <input
                          type="text"
                          className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                          value={editStopword.spanishkeyword || ''}
                          onChange={e => setEditStopword({ ...editStopword, spanishkeyword: e.target.value })}
                        />
                      </div>
                  <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2 text-xs font-medium text-slate-700">
                          <input
                            type="checkbox"
                            checked={!!editStopword.is_active}
                            onChange={e => setEditStopword({ ...editStopword, is_active: e.target.checked })}
                            className="w-3 h-3 text-blue-600 rounded"
                          />
                          Active
                        </label>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEditSave(stopword.id)}
                            className="p-1.5 bg-green-100 text-green-600 hover:bg-green-200 rounded-lg transition-colors"
                          >
                            <Save className="w-3 h-3" />
                          </button>
                          <button
                            onClick={cancelEdit}
                            className="p-1.5 bg-gray-100 text-gray-600 hover:bg-gray-200 rounded-lg transition-colors"
                          >
                            <X className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                      <h3 className="font-semibold text-slate-800 text-lg leading-tight">{stopword.stopword}</h3>
                      {stopword.spanishkeyword && (
                        <p className="text-slate-600 text-sm mt-1 flex items-center gap-1">
                          <Globe className="w-3 h-3" />
                          {stopword.spanishkeyword}
                        </p>
                      )}
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          stopword.is_active 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {stopword.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                        <span>ID: {stopword.id}</span>
                        {stopword.created_at && (
                          <span>{new Date(stopword.created_at).toLocaleDateString()}</span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => startEdit(stopword)}
                          className="flex-1 flex items-center justify-center gap-1 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors text-sm font-medium"
                        >
                          <Edit2 className="w-3 h-3" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(stopword.id)}
                          className="flex-1 flex items-center justify-center gap-1 py-2 bg-red-50 text-red-600 hover:bg-red-100 rounded-lg transition-colors text-sm font-medium"
                        >
                          <Trash2 className="w-3 h-3" />
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StopwordsPage;