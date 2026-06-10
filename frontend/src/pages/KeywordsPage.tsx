import { useEffect, useState, useRef } from 'react';
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

  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

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

  const filteredKeywords = keywords.filter(k =>
    k.keyword.toLowerCase().includes(searchQuery.toLowerCase()) ||
    k.spanishkeyword?.toLowerCase().includes(searchQuery.toLowerCase())
  );

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

  const startEdit = (keyword: Keyword) => {
    setEditingId(keyword.id);
    setEditKeyword({
      keyword: keyword.keyword,
      is_active: keyword.is_active,
      spanishkeyword: keyword.spanishkeyword,
    });
    manualEditSpanish.current = false;
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditKeyword({ ...emptyKeyword });
    manualEditSpanish.current = false;
  };

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

  const handleSpanishChange = (val: string) => {
    setNewKeyword(k => ({ ...k, spanishkeyword: val }));
  };
  const handleEditSpanishChange = (val: string) => {
    setEditKeyword(k => ({ ...k, spanishkeyword: val }));
  };

  return (
    <PageLayout>
      <PageHeader
        title="Keywords"
        description="Manage multilingual search keywords"
        stat={{ value: keywords.length, label: 'Total' }}
      />

      <div className="flex gap-3 mb-6">
        <div className="flex-1">
          <Input
            icon={<Search className="w-4 h-4" />}
            type="text"
            placeholder="Search keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button onClick={() => setShowAddForm(!showAddForm)}>
          <Plus className="w-4 h-4" />
          Add Keyword
        </Button>
      </div>

      {error && <div className="mb-4"><Alert variant="error">{error}</Alert></div>}
      {success && <div className="mb-4"><Alert variant="success">{success}</Alert></div>}

      {showAddForm && (
        <Card className="mb-6">
          <h3 className="text-sm font-semibold text-zinc-900 mb-4">Add New Keyword</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-zinc-700 mb-1.5">
                  English Keyword <span className="text-red-500">*</span>
                </label>
                <Input
                  type="text"
                  value={newKeyword.keyword}
                  onChange={e => setNewKeyword({ ...newKeyword, keyword: e.target.value })}
                  placeholder="Enter keyword..."
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-700 mb-1.5">
                  Spanish Translation
                </label>
                <Input
                  type="text"
                  value={newKeyword.spanishkeyword || ''}
                  onChange={e => handleSpanishChange(e.target.value)}
                  placeholder="Enter Spanish translation..."
                />
              </div>
            </div>
            <div className="flex items-center justify-between pt-2 border-t border-zinc-100">
              <label className="flex items-center gap-2 text-sm text-zinc-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={!!newKeyword.is_active}
                  onChange={e => setNewKeyword({ ...newKeyword, is_active: e.target.checked })}
                  className="w-4 h-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900"
                />
                Active keyword
              </label>
              <div className="flex gap-2">
                <Button variant="ghost" type="button" onClick={() => setShowAddForm(false)}>
                  Cancel
                </Button>
                <Button onClick={(e) => { e.preventDefault(); handleAdd(e); }}>
                  Add Keyword
                </Button>
              </div>
            </div>
          </div>
        </Card>
      )}

      <Card padding={false}>
        {loading ? (
          <LoadingState />
        ) : filteredKeywords.length === 0 ? (
          <EmptyState
            icon={Search}
            title={searchQuery ? 'No matching keywords' : 'No keywords yet'}
            description={searchQuery ? 'Try adjusting your search terms' : 'Add your first keyword to get started'}
          />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-px bg-zinc-200">
            {filteredKeywords.map(keyword => (
              <div key={keyword.id} className="bg-white p-5">
                {editingId === keyword.id ? (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-xs font-medium text-zinc-500 mb-1">English</label>
                      <Input
                        type="text"
                        value={editKeyword.keyword}
                        onChange={e => setEditKeyword({ ...editKeyword, keyword: e.target.value })}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-500 mb-1">Spanish</label>
                      <Input
                        type="text"
                        value={editKeyword.spanishkeyword || ''}
                        onChange={e => handleEditSpanishChange(e.target.value)}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="flex items-center gap-2 text-xs text-zinc-700 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={!!editKeyword.is_active}
                          onChange={e => setEditKeyword({ ...editKeyword, is_active: e.target.checked })}
                          className="w-3.5 h-3.5 rounded border-zinc-300"
                        />
                        Active
                      </label>
                      <div className="flex gap-1">
                        <Button size="sm" onClick={() => handleEditSave(keyword.id)}>
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
                        <h3 className="font-medium text-zinc-900 truncate">{keyword.keyword}</h3>
                        {keyword.spanishkeyword && (
                          <p className="text-sm text-zinc-500 mt-0.5 flex items-center gap-1">
                            <Globe className="w-3 h-3 shrink-0" />
                            <span className="truncate">{keyword.spanishkeyword}</span>
                          </p>
                        )}
                      </div>
                      <Badge variant={keyword.is_active ? 'success' : 'default'}>
                        {keyword.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between text-xs text-zinc-400 mb-4">
                      <span>ID {keyword.id}</span>
                      {keyword.created_at && (
                        <span>{new Date(keyword.created_at).toLocaleDateString()}</span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <Button variant="secondary" size="sm" className="flex-1" onClick={() => startEdit(keyword)}>
                        <Edit2 className="w-3.5 h-3.5" />
                        Edit
                      </Button>
                      <Button variant="danger" size="sm" className="flex-1" onClick={() => handleDelete(keyword.id)}>
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

export default KeywordsPage;
