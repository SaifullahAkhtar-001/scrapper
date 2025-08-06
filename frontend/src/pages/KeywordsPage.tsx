import { useEffect, useState, useRef } from 'react';
import { Search, Plus, Edit2, Trash2, Save, X, Globe, Check, AlertCircle, RefreshCw } from 'lucide-react';
import { supabase } from '../components/SupabaseClient';

export interface Keyword {
  id: number;
  keyword: string;
  is_active: boolean | null;
  created_at: string | null;
  updated_at: string | null;
  spanishkeyword: string | null;
}

const emptyKeyword: Omit<Keyword, 'id' | 'created_at' | 'updated_at'> = {
  keyword: '',
  is_active: true,
  spanishkeyword: '',
};

const KeywordsPage = () => {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [newKeyword, setNewKeyword] = useState(emptyKeyword);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editKeyword, setEditKeyword] = useState<Omit<Keyword, 'id' | 'created_at' | 'updated_at'>>({ ...emptyKeyword });
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const manualSpanish = useRef(false);
  const manualEditSpanish = useRef(false);

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

  // Fetch keywords
  const fetchKeywords = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data, error } = await supabase
        .from('keywords')
        .select('*')
        .order('id', { ascending: true });
      if (error) setError(error.message);
      else setKeywords(data as Keyword[]);
    } catch (err) {
      setError('Failed to fetch keywords');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchKeywords();
  }, []);

  // Filter keywords based on search
  const filteredKeywords = keywords.filter(k => 
    k.keyword.toLowerCase().includes(searchQuery.toLowerCase()) ||
    k.spanishkeyword?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Add keyword
  const handleAdd = async (e: React.MouseEvent) => {
    e.preventDefault();
    setError(null);
    if (!newKeyword.keyword.trim()) {
      setError('Keyword is required');
      return;
    }
    try {
      const { error } = await supabase.from('keywords').insert([newKeyword]);
      if (error) setError(error.message);
      else {
        setNewKeyword(emptyKeyword);
        manualSpanish.current = false;
        setShowAddForm(false);
        setSuccess('Keyword added successfully!');
        fetchKeywords();
      }
    } catch (err) {
      setError('Failed to add keyword');
    }
  };

  // Delete keyword
  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this keyword?')) return;
    setError(null);
    try {
      const { error } = await supabase.from('keywords').delete().eq('id', id);
      if (error) setError(error.message);
      else {
        setSuccess('Keyword deleted successfully!');
        fetchKeywords();
      }
    } catch (err) {
      setError('Failed to delete keyword');
    }
  };

  // Start editing
  const startEdit = (keyword: Keyword) => {
    setEditingId(keyword.id);
    setEditKeyword({
      keyword: keyword.keyword,
      is_active: keyword.is_active,
      spanishkeyword: keyword.spanishkeyword,
    });
    manualEditSpanish.current = false;
  };

  // Cancel editing
  const cancelEdit = () => {
    setEditingId(null);
    setEditKeyword({ ...emptyKeyword });
    manualEditSpanish.current = false;
  };

  // Save edit
  const handleEditSave = async (id: number) => {
    setError(null);
    if (!editKeyword.keyword.trim()) {
      setError('Keyword is required');
      return;
    }
    try {
      const { error } = await supabase
        .from('keywords')
        .update(editKeyword)
        .eq('id', id);
      if (error) setError(error.message);
      else {
        setEditingId(null);
        setEditKeyword({ ...emptyKeyword });
        manualEditSpanish.current = false;
        setSuccess('Keyword updated successfully!');
        fetchKeywords();
      }
    } catch (err) {
      setError('Failed to update keyword');
    }
  };

  // Manual Spanish keyword entry disables auto-translate (now always manual)
  const handleSpanishChange = (val: string) => {
    setNewKeyword(k => ({ ...k, spanishkeyword: val }));
  };
  const handleEditSpanishChange = (val: string) => {
    setEditKeyword(k => ({ ...k, spanishkeyword: val }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Keywords Manager
              </h1>
              <p className="text-slate-600 mt-2">Manage your multilingual keywords</p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-slate-800">{keywords.length}</div>
              <div className="text-sm text-slate-500">Total Keywords</div>
            </div>
          </div>

          {/* Search and Add Bar */}
          <div className="flex gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search keywords..."
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
              Add Keyword
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
            <h3 className="text-xl font-semibold text-slate-800 mb-4">Add New Keyword</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">
                    English Keyword *
                  </label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                    value={newKeyword.keyword}
                    onChange={e => setNewKeyword({ ...newKeyword, keyword: e.target.value })}
                    placeholder="Enter keyword..."
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
                    value={newKeyword.spanishkeyword || ''}
                    onChange={e => handleSpanishChange(e.target.value)}
                    placeholder="Enter Spanish translation..."
                  />
                </div>
              </div>
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-700">
                  <input
                    type="checkbox"
                    checked={!!newKeyword.is_active}
                    onChange={e => setNewKeyword({ ...newKeyword, is_active: e.target.checked })}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                  Active keyword
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
                    Add Keyword
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Keywords Grid */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
          ) : filteredKeywords.length === 0 ? (
            <div className="text-center py-16">
              <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-slate-600 mb-2">
                {searchQuery ? 'No matching keywords' : 'No keywords yet'}
              </h3>
              <p className="text-slate-500">
                {searchQuery ? 'Try adjusting your search terms' : 'Add your first keyword to get started'}
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 p-6">
              {filteredKeywords.map(keyword => (
                <div
                  key={keyword.id}
                  className="bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 p-6 hover:shadow-lg transition-all duration-200"
                >
                  {editingId === keyword.id ? (
                    <div className="space-y-4">
                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-2">English</label>
                        <input
                          type="text"
                          className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                          value={editKeyword.keyword}
                          onChange={e => setEditKeyword({ ...editKeyword, keyword: e.target.value })}
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-slate-600 mb-2">Spanish</label>
                        <input
                          type="text"
                          className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-sm"
                          value={editKeyword.spanishkeyword || ''}
                          onChange={e => handleEditSpanishChange(e.target.value)}
                        />
                      </div>
                      <div className="flex items-center justify-between">
                        <label className="flex items-center gap-2 text-xs font-medium text-slate-700">
                          <input
                            type="checkbox"
                            checked={!!editKeyword.is_active}
                            onChange={e => setEditKeyword({ ...editKeyword, is_active: e.target.checked })}
                            className="w-3 h-3 text-blue-600 rounded"
                          />
                          Active
                        </label>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleEditSave(keyword.id)}
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
                          <h3 className="font-semibold text-slate-800 text-lg leading-tight">{keyword.keyword}</h3>
                          {keyword.spanishkeyword && (
                            <p className="text-slate-600 text-sm mt-1 flex items-center gap-1">
                              <Globe className="w-3 h-3" />
                              {keyword.spanishkeyword}
                            </p>
                          )}
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          keyword.is_active 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-gray-100 text-gray-600'
                        }`}>
                          {keyword.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-xs text-slate-500 mb-4">
                        <span>ID: {keyword.id}</span>
                        {keyword.created_at && (
                          <span>{new Date(keyword.created_at).toLocaleDateString()}</span>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => startEdit(keyword)}
                          className="flex-1 flex items-center justify-center gap-1 py-2 bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg transition-colors text-sm font-medium"
                        >
                          <Edit2 className="w-3 h-3" />
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(keyword.id)}
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

export default KeywordsPage;