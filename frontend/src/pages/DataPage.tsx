import { useEffect, useState } from "react";
import {
  ExternalLink,
  RefreshCw,
  Search,
  Calendar,
  DollarSign,
  Eye,
  Image as ImageIcon,
  Copy,
  Check,
  Save as SaveIcon,
  Trash2,
  ListFilter,
} from "lucide-react";
import { supabase } from "../components/SupabaseClient";
import { PageLayout } from "../components/ui/PageLayout";
import { PageHeader } from "../components/ui/PageHeader";
import { Card } from "../components/ui/Card";
import { Input } from "../components/ui/Input";
import { Select } from "../components/ui/Select";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import { Alert } from "../components/ui/Alert";
import { EmptyState } from "../components/ui/EmptyState";
import { LoadingState } from "../components/ui/LoadingState";
import { Pagination } from "../components/ui/Pagination";

type ViewMode = "pending" | "unqualified";

export interface ScrapedListing {
  id: number;
  title: string;
  url: string;
  price: number | null;
  image_url: string | null;
  description: string | null;
  site: string;
  keyword: string;
  created_at: string | null;
  updated_at: string | null;
  ai_status: boolean | null;
  saved: boolean | null;
}

export interface Keyword {
  id: number;
  keyword: string;
  is_active: boolean | null;
  created_at: string | null;
  updated_at: string | null;
  spanishkeyword: string | null;
}

const DataPage = () => {
  const [viewMode, setViewMode] = useState<ViewMode>("pending");
  const [listings, setListings] = useState<ScrapedListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSite, setSelectedSite] = useState("all");
  const [selectedKeyword, setSelectedKeyword] = useState("all");
  const [priceRange] = useState({ min: "", max: "" });
  const [sortBy, setSortBy] = useState("newest");
  const [copiedId, setCopiedId] = useState<number | null>(null);
  const [availableKeywords, setAvailableKeywords] = useState<Keyword[]>([]);
  const [savingId, setSavingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [bulkDeleting, setBulkDeleting] = useState(false);

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(48);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const fetchKeywords = async () => {
    try {
      const { data, error } = await supabase
        .from("keywords")
        .select("*")
        .eq("is_active", true)
        .order("keyword", { ascending: true });

      if (error) {
        console.error("Error fetching keywords:", error);
      } else {
        setAvailableKeywords(data as Keyword[]);
      }
    } catch (err) {
      console.error("Failed to fetch keywords:", err);
    }
  };

  useEffect(() => {
    fetchSavedIds();
  }, []);
  const fetchSavedIds = async () => {
    try {
      const { data, error } = await supabase
        .from("scraped_listings")
        .select("id")
        .eq("saved", true);

      if (error) {
        console.error("Error fetching saved IDs:", error);
      } else {
        const savedIdsSet = new Set(data?.map(item => item.id) || []);
        setSavedIds(savedIdsSet);
      }
    } catch (err) {
      console.error("Failed to fetch saved IDs:", err);
    }
  };

  const fetchListings = async () => {
    console.log("Starting to fetch listings...");
    setLoading(true);
    setError(null);

    try {
      let query = supabase
        .from("scraped_listings")
        .select("*", { count: "exact" });

      if (searchQuery) {
        query = query.ilike("title", `%${searchQuery}%`);
      }
      if (selectedSite !== "all") {
        query = query.eq("site", selectedSite);
      }
      if (selectedKeyword !== "all") {
        try {
          const parsed = JSON.parse(selectedKeyword as string) as {
            en?: string | null;
            es?: string | null;
          };
          const orFilters: string[] = [];
          if (parsed?.en) {
            orFilters.push(`title.ilike.%${parsed.en}%`);
          }
          if (parsed?.es) {
            orFilters.push(`title.ilike.%${parsed.es}%`);
          }
          if (orFilters.length > 0) {
            query = query.or(orFilters.join(","));
          }
        } catch {
          query = query.ilike("title", `%${selectedKeyword}%`);
        }
      }
      if (priceRange.min) {
        query = query.gte("price", parseFloat(priceRange.min));
      }
      if (priceRange.max) {
        query = query.lte("price", parseFloat(priceRange.max));
      }

      if (viewMode === "pending") {
        query = query.is("ai_status", null);
      } else {
        // AI processed but rejected: ai_status=true means classified, saved=false means not qualified
        query = query.eq("ai_status", true).eq("saved", false);
      }

      if (sortBy === "oldest") {
        query = query.order("id", { ascending: true });
      } else if (sortBy === "price-high") {
        query = query.order("price", { ascending: false });
      } else if (sortBy === "price-low") {
        query = query.order("price", { ascending: true });
      } else {
        query = query.order("id", { ascending: false });
      }

      const from = (currentPage - 1) * pageSize;
      const to = from + pageSize - 1;
      query = query.range(from, to);

      console.log("Executing Supabase query...");
      const { data, error, count } = await query;
      console.log(
        "Supabase query completed. Data:",
        data,
        "Error:",
        error,
        "Count:",
        count
      );

      if (error) {
        console.error("Error from Supabase:", error);
        setError(error.message);
      } else {
        setListings(data as ScrapedListing[]);
        setTotalCount(count || 0);
        setTotalPages(Math.ceil((count || 0) / pageSize));
      }
    } catch (err) {
      console.error("Failed to fetch listings:", err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchKeywords();
  }, []);

  useEffect(() => {
    fetchListings();
  }, [
    currentPage,
    pageSize,
    searchQuery,
    selectedSite,
    selectedKeyword,
    priceRange,
    sortBy,
    viewMode,
  ]);

  useEffect(() => {
    setCurrentPage(1);
    setSelectedIds(new Set());
  }, [searchQuery, selectedSite, selectedKeyword, priceRange, sortBy, viewMode]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1);
  };

  const highlightKeywordInTitle = (title: string, keyword: string) => {
    if (!keyword) return title;
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(${escaped})`, "ig");
    const parts = title.split(regex);
    return parts.map((part, idx) =>
      part.toLowerCase() === keyword.toLowerCase() ? (
        <mark key={idx} className="bg-amber-100 text-amber-900 rounded px-0.5">
          {part}
        </mark>
      ) : (
        <span key={idx}>{part}</span>
      )
    );
  };

  const handleSaveListing = async (listing: ScrapedListing) => {
    try {
      setSavingId(listing.id);

      const { error: update_error } = await supabase
        .from("scraped_listings")
        .update({
          saved: true,
          updated_at: new Date().toISOString()
        })
        .eq("id", listing.id);

      const { error } = await supabase.from("cigar_listings").insert([
        {
          title: listing.title,
          url: listing.url,
          price: listing.price,
          image_url: listing.image_url,
          description: listing.description,
          site: listing.site,
          keyword: listing.keyword,
          created_at: new Date().toISOString(),
          parent_id: listing.id,
        },
      ]);

      if (error || update_error) {
        if ((error as any).code !== "23505") {
          throw error || update_error;
        }
      }

      setListings(prevListings =>
        prevListings.map(item =>
          item.id === listing.id
            ? { ...item, saved: true, updated_at: new Date().toISOString() }
            : item
        )
      );

      setSavedIds(prev => new Set([...prev, listing.id]));
      setError(null);
    } catch (e) {
      console.error("Failed to save listing:", e);
      setError("Failed to save listing");
    } finally {
      setSavingId(null);
    }
  };

  const handleDeleteListing = async (id: number) => {
    try {
      setDeletingId(id);
      const { error } = await supabase
        .from("scraped_listings")
        .delete()
        .eq("id", id);
      if (error) throw error;
      setListings((prev) => prev.filter((l) => l.id !== id));
      setTotalCount((prev) => Math.max(0, prev - 1));
      setSelectedIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    } catch (e) {
      console.error("Failed to delete listing:", e);
      setError("Failed to delete listing");
    } finally {
      setDeletingId(null);
    }
  };

  const toggleViewMode = () => {
    setViewMode((mode) => (mode === "pending" ? "unqualified" : "pending"));
  };

  const toggleSelectId = (id: number) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const allOnPageSelected =
    listings.length > 0 && listings.every((l) => selectedIds.has(l.id));

  const toggleSelectAllOnPage = () => {
    if (allOnPageSelected) {
      setSelectedIds((prev) => {
        const next = new Set(prev);
        listings.forEach((l) => next.delete(l.id));
        return next;
      });
    } else {
      setSelectedIds((prev) => {
        const next = new Set(prev);
        listings.forEach((l) => next.add(l.id));
        return next;
      });
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`Delete ${selectedIds.size} unqualified listing(s)? This cannot be undone.`)) return;

    setBulkDeleting(true);
    setError(null);
    try {
      const ids = Array.from(selectedIds);
      const { error } = await supabase
        .from("scraped_listings")
        .delete()
        .in("id", ids);
      if (error) throw error;

      setListings((prev) => prev.filter((l) => !selectedIds.has(l.id)));
      setTotalCount((prev) => Math.max(0, prev - selectedIds.size));
      setSelectedIds(new Set());
    } catch (e) {
      console.error("Failed to bulk delete listings:", e);
      setError("Failed to delete selected listings");
    } finally {
      setBulkDeleting(false);
    }
  };

  const isUnqualifiedView = viewMode === "unqualified";

  return (
    <PageLayout wide>
      <PageHeader
        title="Scraped Listings"
        description={
          isUnqualifiedView
            ? "AI processed but not saved (ai_status=true, saved=false)"
            : "Listings awaiting AI classification (ai_status is null)"
        }
        stat={{ value: totalCount, label: isUnqualifiedView ? "Unqualified" : "Pending" }}
        actions={
          <Button
            variant={isUnqualifiedView ? "primary" : "secondary"}
            onClick={toggleViewMode}
          >
            <ListFilter className="w-4 h-4" />
            {isUnqualifiedView ? "Show Pending Data" : "Show Unqualified Data"}
          </Button>
        }
      />

      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          <Input
            icon={<Search className="w-4 h-4" />}
            type="text"
            placeholder="Search listings..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <Select
            value={selectedSite}
            onChange={(e) => setSelectedSite(e.target.value)}
          >
            <option value="all">All Sites</option>
            <option value="ebay">eBay</option>
            <option value="craigslist">Craigslist</option>
            <option value="todocoleccion">TodoColeccion</option>
          </Select>
          <Select
            value={selectedKeyword}
            onChange={(e) => setSelectedKeyword(e.target.value)}
          >
            <option value="all">All Keywords</option>
            {availableKeywords.map((keyword) => (
              <option
                key={keyword.id}
                value={JSON.stringify({ en: keyword.keyword, es: keyword.spanishkeyword })}
              >
                {(keyword.keyword && keyword.spanishkeyword)
                  ? `${keyword.keyword} / ${keyword.spanishkeyword}`
                  : (keyword.spanishkeyword || keyword.keyword || "")}
              </option>
            ))}
          </Select>
          <Select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="price-high">Price: High to Low</option>
            <option value="price-low">Price: Low to High</option>
          </Select>
        </div>
      </Card>

      {error && <div className="mb-4"><Alert variant="error">{error}</Alert></div>}

      <Card padding={false}>
        {loading ? (
          <LoadingState />
        ) : listings.length === 0 ? (
          <EmptyState
            icon={Search}
            title={searchQuery ? "No matching listings" : isUnqualifiedView ? "No unqualified listings" : "No pending listings"}
            description={
              searchQuery
                ? "Try adjusting your search terms"
                : isUnqualifiedView
                  ? "All unqualified listings have been removed"
                  : "New scraped listings will appear here before AI classification"
            }
          />
        ) : (
          <>
            {isUnqualifiedView && (
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-4 py-3 border-b border-zinc-200 bg-zinc-50">
                <label className="flex items-center gap-2.5 text-sm text-zinc-700 cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={allOnPageSelected}
                    onChange={toggleSelectAllOnPage}
                    className="w-4 h-4 rounded border-zinc-300 text-zinc-900 focus:ring-zinc-900"
                  />
                  Select all on page ({listings.length})
                  {selectedIds.size > 0 && (
                    <span className="text-zinc-500">
                      · {selectedIds.size} selected
                    </span>
                  )}
                </label>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleBulkDelete}
                  disabled={selectedIds.size === 0 || bulkDeleting}
                >
                  {bulkDeleting ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Trash2 className="w-4 h-4" />
                  )}
                  Delete selected ({selectedIds.size})
                </Button>
              </div>
            )}

            <div className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {listings.map((listing) => (
                  <div
                    key={listing.id}
                    className={`border rounded-lg overflow-hidden bg-white transition-colors group ${
                      isUnqualifiedView && selectedIds.has(listing.id)
                        ? "border-zinc-900 ring-1 ring-zinc-900"
                        : "border-zinc-200 hover:border-zinc-300"
                    }`}
                  >
                    <div className="relative h-44 bg-zinc-100">
                      {isUnqualifiedView && (
                        <div className="absolute top-2 right-2 z-10">
                          <input
                            type="checkbox"
                            checked={selectedIds.has(listing.id)}
                            onChange={() => toggleSelectId(listing.id)}
                            className="w-4 h-4 rounded border-zinc-300 bg-white text-zinc-900 focus:ring-zinc-900 shadow-sm"
                            aria-label={`Select listing ${listing.id}`}
                          />
                        </div>
                      )}
                      {listing.image_url ? (
                        <img
                          src={listing.image_url}
                          alt={listing.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          <ImageIcon className="w-8 h-8 text-zinc-300" />
                        </div>
                      )}
                      <div className="absolute top-2 left-2 flex gap-1.5">
                        <Badge variant="info">{listing.site}</Badge>
                        {listing.created_at &&
                          new Date(listing.created_at) > new Date(Date.now() - 24 * 60 * 60 * 1000) && (
                            <Badge variant="success">New</Badge>
                          )}
                      </div>
                    </div>

                    <div className="p-3.5">
                      <h3 className="text-sm font-medium text-zinc-900 leading-snug mb-2 line-clamp-2">
                        {highlightKeywordInTitle(listing.title, listing.keyword)}
                      </h3>
                      <div className="mb-2">
                        <Badge>{listing.keyword}</Badge>
                      </div>
                      {listing.description && (
                        <p className="text-xs text-zinc-500 mb-3 line-clamp-2">
                          {listing.description}
                        </p>
                      )}

                      <div className="flex items-center justify-between text-xs text-zinc-400 mb-2">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {listing.created_at
                            ? new Date(listing.created_at).toLocaleDateString()
                            : "N/A"}
                        </div>
                        <span>#{listing.id}</span>
                      </div>
                      {listing.price !== null && (
                        <div className="flex items-center gap-1 text-sm mb-3">
                          <DollarSign className="w-3.5 h-3.5 text-zinc-400" />
                          <span className="font-medium text-zinc-900">
                            ${listing.price.toFixed(2)}
                          </span>
                        </div>
                      )}

                      <div className="flex items-center gap-1.5 pt-3 border-t border-zinc-100">
                        <a
                          href={listing.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-1 inline-flex items-center justify-center gap-1.5 py-1.5 text-xs font-medium text-white bg-zinc-900 hover:bg-zinc-800 rounded-md transition-colors"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          View
                          <ExternalLink className="w-3 h-3" />
                        </a>
                        <button
                          className={`p-1.5 rounded-md border transition-colors ${
                            savedIds.has(listing.id)
                              ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                              : "border-zinc-200 text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900"
                          }`}
                          onClick={() => handleSaveListing(listing)}
                          disabled={savingId === listing.id || savedIds.has(listing.id)}
                          type="button"
                          aria-label="Save listing"
                          title={savedIds.has(listing.id) ? "Saved" : "Save"}
                        >
                          {savingId === listing.id ? (
                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          ) : savedIds.has(listing.id) ? (
                            <Check className="w-3.5 h-3.5" />
                          ) : (
                            <SaveIcon className="w-3.5 h-3.5" />
                          )}
                        </button>
                        <button
                          className="p-1.5 rounded-md border border-zinc-200 text-zinc-500 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
                          onClick={() => handleDeleteListing(listing.id)}
                          disabled={deletingId === listing.id}
                          type="button"
                          aria-label="Delete listing"
                          title="Delete"
                        >
                          {deletingId === listing.id ? (
                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Trash2 className="w-3.5 h-3.5" />
                          )}
                        </button>
                        <button
                          className="p-1.5 rounded-md border border-zinc-200 text-zinc-500 hover:bg-zinc-50 hover:text-zinc-900 transition-colors"
                          onClick={async () => {
                            await navigator.clipboard.writeText(listing.url);
                            setCopiedId(listing.id);
                            setTimeout(() => setCopiedId(null), 1200);
                          }}
                          aria-label="Copy URL"
                          title="Copy URL"
                          type="button"
                        >
                          {copiedId === listing.id ? (
                            <Check className="w-3.5 h-3.5 text-emerald-600" />
                          ) : (
                            <Copy className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              totalCount={totalCount}
              pageSize={pageSize}
              onPageChange={handlePageChange}
              onPageSizeChange={handlePageSizeChange}
            />
          </>
        )}
      </Card>
    </PageLayout>
  );
};

export default DataPage;
