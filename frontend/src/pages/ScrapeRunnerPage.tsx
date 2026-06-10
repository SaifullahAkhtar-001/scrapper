import { useEffect, useState } from "react";
import {
  Play,
  Search,
  RefreshCw,
  ChevronDown,
  AlertCircle,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { PageLayout } from "../components/ui/PageLayout";
import { PageHeader } from "../components/ui/PageHeader";
import { Card } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Alert } from "../components/ui/Alert";

type ScrapeSiteResult = {
  success: boolean;
  site?: string;
  total_listings_found?: number;
  saved_listings?: number;
  pages_scraped?: number;
  errors?: number;
  error?: string;
};

type ScrapeResponse = {
  success: boolean;
  keyword: string;
  results: {
    todocoleccion?: ScrapeSiteResult;
    craigslist?: ScrapeSiteResult;
    [key: string]: ScrapeSiteResult | undefined;
  };
};

const ScrapeRunnerPage = () => {
  const navigate = useNavigate();
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [result, setResult] = useState<ScrapeResponse | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [selectedSites, setSelectedSites] = useState<Record<string, boolean>>({
    todocoleccion: true,
    craigslist: true,
    ebay: true,
  });

  useEffect(() => {
    if (error || success) {
      const t = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 3000);
      return () => clearTimeout(t);
    }
  }, [error, success]);

  const handleRun = async () => {
    setError(null);
    setSuccess(null);
    setResult(null);

    const trimmed = keyword.trim();
    if (!trimmed) {
      setError("Keyword is required");
      return;
    }
    if (trimmed.length < 2) {
      setError("Keyword must be at least 2 characters");
      return;
    }

    const sites = Object.entries(selectedSites)
      .filter(([_, isSelected]) => isSelected)
      .map(([site]) => site);

    if (sites.length === 0) {
      setError("Please select at least one website");
      return;
    }

    setLoading(true);
    try {
      const resp = await fetch("http://127.0.0.1:5001/api/scrape", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          keyword: trimmed,
          sites: sites,
        }),
      });
      const data: ScrapeResponse = await resp.json();
      setResult(data);
      if (resp.ok && data.success) {
        setSuccess("Scrape finished successfully");
        setTimeout(() => {
          navigate("/data");
        }, 1500);
      } else {
        setError("Scrape finished with errors");
      }
    } catch (e) {
      setError("Failed to run scrapers");
      console.error("Scraper error:", e);
    }
    setLoading(false);
  };

  const renderSiteCard = (title: string, siteResult?: ScrapeSiteResult) => {
    if (!siteResult) return null;
    const ok = !!siteResult.success;
    return (
      <Card key={title}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-zinc-900">{title}</h3>
          <Badge variant={ok ? "success" : "error"}>
            {ok ? "Success" : "Error"}
          </Badge>
        </div>
        {ok ? (
          <div className="grid grid-cols-2 gap-4">
            {[
              { label: "Listings Found", value: siteResult.total_listings_found ?? "-" },
              { label: "Saved Listings", value: siteResult.saved_listings ?? "-" },
              { label: "Pages Scraped", value: siteResult.pages_scraped ?? "-" },
              { label: "Errors", value: siteResult.errors ?? 0 },
            ].map(({ label, value }) => (
              <div key={label}>
                <div className="text-xs text-zinc-500 mb-0.5">{label}</div>
                <div className="text-sm font-medium text-zinc-900">{value}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-red-600">
            <AlertCircle className="w-4 h-4 shrink-0" />
            {siteResult.error || "Unknown error"}
          </div>
        )}
      </Card>
    );
  };

  return (
    <PageLayout>
      <PageHeader
        title="Run Scrapers"
        description="Run scrapers for specific websites with a keyword"
      />

      <Card className="mb-6">
        <div className="space-y-4">
          <div className="flex gap-3">
            <div className="flex-1">
              <Input
                icon={<Search className="w-4 h-4" />}
                type="text"
                placeholder="Enter keyword..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                disabled={loading}
                onKeyDown={(e) => e.key === "Enter" && handleRun()}
              />
            </div>
            <Button onClick={handleRun} disabled={loading} size="lg">
              {loading ? (
                <RefreshCw className="w-4 h-4 animate-spin" />
              ) : (
                <Play className="w-4 h-4" />
              )}
              {loading ? "Running..." : "Run Scrapers"}
            </Button>
          </div>

          <div className="relative">
            <button
              type="button"
              className="flex items-center justify-between w-full px-3 py-2 text-sm bg-white border border-zinc-300 rounded-md text-zinc-700 hover:bg-zinc-50 transition-colors"
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            >
              <span>Select Websites</span>
              <ChevronDown
                className={`w-4 h-4 text-zinc-400 transition-transform ${
                  isDropdownOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {isDropdownOpen && (
              <div className="absolute z-10 mt-1 w-full bg-white rounded-md shadow-lg border border-zinc-200">
                <div className="p-1">
                  {Object.entries(selectedSites).map(([site, isSelected]) => (
                    <label
                      key={site}
                      className="flex items-center px-3 py-2 rounded hover:bg-zinc-50 cursor-pointer text-sm"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => {
                          setSelectedSites((prev) => ({
                            ...prev,
                            [site]: !prev[site],
                          }));
                        }}
                        className="h-4 w-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900 mr-2.5"
                      />
                      <span className="capitalize text-zinc-700">{site}</span>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </Card>

      {error && <div className="mb-4"><Alert variant="error">{error}</Alert></div>}
      {success && <div className="mb-4"><Alert variant="success">{success}</Alert></div>}

      {result && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {result.results?.todocoleccion &&
            renderSiteCard("Todocoleccion", result.results.todocoleccion)}
          {result.results?.craigslist &&
            renderSiteCard("Craigslist", result.results.craigslist)}
          {result.results?.ebay &&
            renderSiteCard("eBay", result.results.ebay)}
        </div>
      )}
    </PageLayout>
  );
};

export default ScrapeRunnerPage;
