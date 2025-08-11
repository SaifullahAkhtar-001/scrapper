import { useEffect, useState } from "react";
import {
  Play,
  Search,
  AlertCircle,
  Check,
  RefreshCw,
  ChevronDown,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

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
        // Redirect to data page after a short delay
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
      <div className="bg-white/80 rounded-xl border border-slate-200 p-5 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-800">{title}</h3>
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${
              ok ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
            }`}
          >
            {ok ? "Success" : "Error"}
          </span>
        </div>
        {ok ? (
          <div className="grid grid-cols-2 gap-3 text-sm text-slate-700">
            <div>
              <div className="text-slate-500">Listings Found</div>
              <div className="font-medium">
                {siteResult.total_listings_found ?? "-"}
              </div>
            </div>
            <div>
              <div className="text-slate-500">Saved Listings</div>
              <div className="font-medium">
                {siteResult.saved_listings ?? "-"}
              </div>
            </div>
            <div>
              <div className="text-slate-500">Pages Scraped</div>
              <div className="font-medium">
                {siteResult.pages_scraped ?? "-"}
              </div>
            </div>
            <div>
              <div className="text-slate-500">Errors</div>
              <div className="font-medium">{siteResult.errors ?? 0}</div>
            </div>
          </div>
        ) : (
          <div className="flex items-center text-sm text-red-600">
            <AlertCircle className="w-4 h-4 mr-1" />
            {siteResult.error || "Unknown error"}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Run Scrapers
              </h1>
              <p className="text-slate-600 mt-2">
                Run scrapers for specific websites with a keyword
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex gap-3 items-center">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Enter keyword..."
                  className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                  value={keyword}
                  onChange={(e) => setKeyword(e.target.value)}
                  disabled={loading}
                  onKeyDown={(e) => e.key === "Enter" && handleRun()}
                />
              </div>
              <button
                onClick={handleRun}
                disabled={loading}
                className={`px-6 py-3 rounded-xl text-white font-medium shadow-lg bg-gradient-to-r from-blue-600 to-indigo-600 flex items-center gap-2 ${
                  loading
                    ? "opacity-60 cursor-not-allowed"
                    : "hover:from-blue-700 hover:to-indigo-700"
                }`}
              >
                {loading ? (
                  <RefreshCw className="w-5 h-5 animate-spin" />
                ) : (
                  <Play className="w-5 h-5" />
                )}
                {loading ? "Running..." : "Run Scrapers"}
              </button>
            </div>

            <div className="relative">
              <button
                type="button"
                className="flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 rounded-lg text-slate-700 hover:bg-slate-50 transition-colors w-full justify-between"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              >
                <span>Select Websites</span>
                <ChevronDown
                  className={`w-4 h-4 transition-transform ${
                    isDropdownOpen ? "rotate-180" : ""
                  }`}
                />
              </button>

              {isDropdownOpen && (
                <div className="absolute z-10 mt-1 w-full bg-white rounded-md shadow-lg border border-slate-200">
                  <div className="p-2 space-y-1">
                    {Object.entries(selectedSites).map(([site, isSelected]) => (
                      <label
                        key={site}
                        className="flex items-center p-2 rounded hover:bg-slate-50 cursor-pointer"
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
                          className="h-4 w-4 text-blue-600 rounded border-slate-300 focus:ring-blue-500 mr-2"
                        />
                        <span className="capitalize">{site}</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

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

          {result && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {result.results?.todocoleccion &&
                renderSiteCard("Todocoleccion", result.results.todocoleccion)}
              {result.results?.craigslist &&
                renderSiteCard("Craigslist", result.results.craigslist)}
              {result.results?.ebay &&
                renderSiteCard("eBay", result.results.ebay)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScrapeRunnerPage;
