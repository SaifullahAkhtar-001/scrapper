import { useEffect, useState } from 'react';
import { Search, Plus, Edit2, Trash2, Save, X, Globe } from 'lucide-react';
import { supabase } from '../components/SupabaseClient';
import { PageLayout } from '../components/ui/PageLayout';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Alert } from '../components/ui/Alert';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingState } from '../components/ui/LoadingState';

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

  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

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

  const filteredStopwords = stopwords.filter(s =>
    s.stopword.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (s.spanishkeyword || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

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

  const startEdit = (stopword: Stopword) => {
    setEditingId(stopword.id);
    setEditStopword({
      stopword: stopword.stopword,
      is_active: stopword.is_active,
      spanishkeyword: stopword.spanishkeyword,
    });
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditStopword({ ...emptyStopword });
  };

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

  return (
    <PageLayout>
      <PageHeader
        title="Stopwords"
        description="Manage stopwords for filtering listings"
        stat={{ value: stopwords.length, label: 'Total' }}
      />

      <div className="flex gap-3 mb-6">
        <div className="flex-1">
          <Input
            icon={<Search className="w-4 h-4" />}
            type="text"
            placeholder="Search stopwords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button onClick={() => setShowAddForm(!showAddForm)}>
          <Plus className="w-4 h-4" />
          Add Stopword
        </Button>
      </div>

      {error && <div className="mb-4"><Alert variant="error">{error}</Alert></div>}
      {success && <div className="mb-4"><Alert variant="success">{success}</Alert></div>}

      {showAddForm && (
        <Card className="mb-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-4">Add New Stopword</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-zinc-700 mb-1.5">
                  English Stopword <span className="text-red-500">*</span>
                </label>
                <Input
                  type="text"
                  value={newStopword.stopword}
                  onChange={e => setNewStopword({ ...newStopword, stopword: e.target.value })}
                  placeholder="Enter stopword..."
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-700 mb-1.5">
                  Spanish Translation
                </label>
                <Input
                  type="text"
                  value={newStopword.spanishkeyword || ''}
                  onChange={e => setNewStopword({ ...newStopword, spanishkeyword: e.target.value })}
                  placeholder="Enter Spanish translation..."
                />
              </div>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-zinc-100">
              <label className="flex items-center gap-2 text-sm text-zinc-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={!!newStopword.is_active}
                  onChange={e => setNewStopword({ ...newStopword, is_active: e.target.checked })}
                  className="w-4 h-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900"
                />
                Active stopword
              </label>
              <div className="flex gap-2">
                <Button variant="ghost" type="button" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
                <Button onClick={(e) => { e.preventDefault(); handleAdd(e); }}>
                  Add Stopword
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}

      <Card padding={false}>
        {loading ? (
          <LoadingState />
        ) : filteredStopwords.length === 0 ? (
          <EmptyState
            icon={Search}
            title={searchQuery ? 'No matching stopwords' : 'No stopwords yet'}
            description={searchQuery ? 'Try adjusting your search terms' : 'Add your first stopword to get started'}
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-px bg-zinc-200">
            {filteredStopwords.map(stopword => (
              <div key={stopword.id} className="bg-white p-5">
                {editingId === stopword.id ? (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-zinc-500 mb-1">English</label>
                      <Input
                        type="text"
                        value={editStopword.stopword}
                        onChange={e => setEditStopword({ ...editStopword, stopword: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-500 mb-1">Spanish</label>
                      <Input
                        type="text"
                        value={editStopword.spanishkeyword || ''}
                        onChange={e => setEditStopword({ ...editStopword, spanishkeyword: e.target.value })}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="flex items-center gap-2 text-xs text-zinc-700 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={!!editStopword.is_active}
                          onChange={e => setEditStopword({ ...editStopword, is_active: e.target.checked })}
                          className="w-3.5 h-3.5 rounded border-zinc-300"
                        />
                        Active
                      </label>
                      <div className="flex gap-1">
                        <Button size="sm" onClick={() => handleEditSave(stopword.id)}>
                          <Save className="w-3.5 h-3.5" />
                        </Button>
                        <Button size="sm" variant="ghost" onClick={cancelEdit}>
                          <X className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div className="min-w-0">
                        <h3 className="font-medium text-zinc-900 truncate">{stopword.stopword}</h3>
                        {stopword.spanishkeyword && (
                          <p className="text-sm text-zinc-500 mt-0.5 flex items-center gap-1">
                            <Globe className="w-3 h-3 shrink-0" />
                            <span className="truncate">{stopword.spanishkeyword}</span>
                          </p>
                        )}
                      </div>
                      <Badge variant={stopword.is_active ? 'success' : 'default'}>
                        {stopword.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-xs text-zinc-400 mb-4">
                      <span>ID {stopword.id}</span>
                      {stopword.created_at && (
                        <span>{new Date(stopword.created_at).toLocaleDateString()}</span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button variant="secondary" size="sm" className="flex-1" onClick={() => startEdit(stopword)}>
                        <Edit2 className="w-3.5 h-3.5" />
                        Edit
                      </Button>
                      <Button variant="danger" size="sm" className="flex-1" onClick={() => handleDelete(stopword.id)}>
                        <Trash2 className="w-3.5 h-3.5" />
                        Delete
                      </Button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>
    </PageLayout>
  );
};

export default StopwordsPage;
