import { useEffect, useState } from 'react';
import { Copy, Check, RefreshCw } from 'lucide-react';
import { supabase } from '../components/SupabaseClient';
import { PageLayout } from '../components/ui/PageLayout';
import { PageHeader } from '../components/ui/PageHeader';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import { LoadingState } from '../components/ui/LoadingState';

interface AppSetting {
  key: string;
  value: boolean | string | null;
  is_public: boolean;
  description: string | null;
  updated_at: string;
}

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string;

const SettingsPage = () => {
  const [settings, setSettings] = useState<AppSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const fetchUrl =
    `${supabaseUrl}/rest/v1/app_settings?key=eq.is_scraper_running&select=key,value,updated_at`;

  const fetchSettings = async () => {
    setLoading(true);
    setError(null);
    try {
      const { data, error: fetchError } = await supabase
        .from('app_settings')
        .select('key, value, is_public, description, updated_at')
        .order('key');

      if (fetchError) throw fetchError;
      setSettings((data as AppSetting[]) ?? []);
    } catch (e) {
      setError('Failed to load settings. Make sure you ran the SQL migration in Supabase.');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  useEffect(() => {
    if (error || success) {
      const t = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 3000);
      return () => clearTimeout(t);
    }
  }, [error, success]);

  const updateSetting = async (key: string, value: boolean) => {
    setSaving(key);
    setError(null);
    try {
      const { error: updateError } = await supabase
        .from('app_settings')
        .update({ value })
        .eq('key', key);

      if (updateError) throw updateError;

      setSettings((prev) =>
        prev.map((s) => (s.key === key ? { ...s, value } : s))
      );
      setSuccess(`Updated ${key}`);
    } catch (e) {
      setError(`Failed to update ${key}`);
    }
    setSaving(null);
  };

  const copyFetchUrl = async () => {
    await navigator.clipboard.writeText(fetchUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const scraperRunning = settings.find((s) => s.key === 'is_scraper_running');

  return (
    <PageLayout>
      <PageHeader
        title="Settings"
        description="Manage application configuration and scraper status"
        actions={
          <Button variant="secondary" size="sm" onClick={fetchSettings}>
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        }
      />

      {error && <div className="mb-4"><Alert variant="error">{error}</Alert></div>}
      {success && <div className="mb-4"><Alert variant="success">{success}</Alert></div>}

      {loading ? (
        <LoadingState />
      ) : (
        <div className="space-y-6">
          <Card>
            <h2 className="text-sm font-semibold text-zinc-900 mb-1">Scraper Status</h2>
            <p className="text-sm text-zinc-500 mb-4">
              Control whether the scraper process should be running. External scripts can read this via the API URL below.
            </p>

            <div className="flex items-center justify-between py-3 border-t border-zinc-100">
              <div>
                <div className="text-sm font-medium text-zinc-900">is_scraper_running</div>
                <div className="text-xs text-zinc-500 mt-0.5">
                  {scraperRunning?.description ?? 'Scraper active flag'}
                </div>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={scraperRunning?.value === true}
                disabled={saving === 'is_scraper_running'}
                onClick={() =>
                  updateSetting('is_scraper_running', scraperRunning?.value !== true)
                }
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-zinc-900 disabled:opacity-50 ${
                  scraperRunning?.value === true ? 'bg-zinc-900' : 'bg-zinc-200'
                }`}
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition-transform ${
                    scraperRunning?.value === true ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
            </div>

            <div className="mt-2 text-xs text-zinc-400">
              Current value:{' '}
              <code className="bg-zinc-100 px-1.5 py-0.5 rounded text-zinc-700">
                {JSON.stringify(scraperRunning?.value ?? false)}
              </code>
            </div>
          </Card>

          {/* <Card>
            <h2 className="text-sm font-semibold text-zinc-900 mb-1">Public API URL</h2>
            <p className="text-sm text-zinc-500 mb-4">
              Fetch <code className="text-xs bg-zinc-100 px-1 rounded">is_scraper_running</code> from any script or service using your Supabase anon key.
            </p>

            <div className="bg-zinc-50 border border-zinc-200 rounded-md p-3">
              <code className="text-xs text-zinc-700 break-all leading-relaxed block">
                GET {fetchUrl}
              </code>
            </div>

            <div className="mt-3 flex gap-2">
              <Button variant="secondary" size="sm" onClick={copyFetchUrl}>
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied' : 'Copy URL'}
              </Button>
            </div>

            <div className="mt-4 pt-4 border-t border-zinc-100">
              <p className="text-xs font-medium text-zinc-700 mb-2">Required headers</p>
              <pre className="text-xs bg-zinc-900 text-zinc-100 rounded-md p-3 overflow-x-auto">
{`apikey: ${supabaseAnonKey}
Authorization: Bearer ${supabaseAnonKey}`}
              </pre>
            </div>

            <div className="mt-4 pt-4 border-t border-zinc-100">
              <p className="text-xs font-medium text-zinc-700 mb-2">Example (curl)</p>
              <pre className="text-xs bg-zinc-900 text-zinc-100 rounded-md p-3 overflow-x-auto whitespace-pre-wrap">
{`curl "${fetchUrl}" \\
  -H "apikey: ${supabaseAnonKey}" \\
  -H "Authorization: Bearer ${supabaseAnonKey}"`}
              </pre>
            </div>

            <div className="mt-4 pt-4 border-t border-zinc-100">
              <p className="text-xs font-medium text-zinc-700 mb-2">Example response</p>
              <pre className="text-xs bg-zinc-50 border border-zinc-200 rounded-md p-3 overflow-x-auto">
{`[
  {
    "key": "is_scraper_running",
    "value": false,
    "updated_at": "2026-06-11T12:00:00+00:00"
  }
]`}
              </pre>
            </div>
          </Card> */}

          {/* {settings.length > 1 && (
            <Card>
              <h2 className="text-sm font-semibold text-zinc-900 mb-4">All Settings</h2>
              <div className="divide-y divide-zinc-100">
                {settings.map((setting) => (
                  <div key={setting.key} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                    <div>
                      <div className="text-sm font-medium text-zinc-900">{setting.key}</div>
                      {setting.description && (
                        <div className="text-xs text-zinc-500">{setting.description}</div>
                      )}
                    </div>
                    <code className="text-xs bg-zinc-100 px-2 py-1 rounded text-zinc-700">
                      {JSON.stringify(setting.value)}
                    </code>
                  </div>
                ))}
              </div>
            </Card>
          )} */}
        </div>
      )}
    </PageLayout>
  );
};

export default SettingsPage;
