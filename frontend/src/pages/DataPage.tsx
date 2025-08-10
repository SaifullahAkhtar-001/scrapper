import { useEffect, useState } from "react";
import {
  ExternalLink,
  RefreshCw,
  AlertCircle,
  Search,
  Calendar,
  DollarSign,
  Eye,
  Image as ImageIcon,
  Copy,
  Check,
  ChevronLeft,
  ChevronRight,
  Save as SaveIcon,
  Trash2,
} from "lucide-react";
import { supabase } from "../components/SupabaseClient";

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

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(48);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  // Fetch available keywords
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

  const fetchListings = async () => {
    console.log("Starting to fetch listings...");
    setLoading(true);
    setError(null);

    try {
      // Build query
      let query = supabase
        .from("scraped_listings")
        .select("*", { count: "exact" });

      // Apply filters
      if (searchQuery) {
        query = query.ilike("title", `%${searchQuery}%`);
      }
      if (selectedSite !== "all") {
        query = query.eq("site", selectedSite);
      }
      if (selectedKeyword !== "all") {
        query = query.ilike("title", `%${selectedKeyword}%`);
      }
      if (priceRange.min) {
        query = query.gte("price", parseFloat(priceRange.min));
      }
      if (priceRange.max) {
        query = query.lte("price", parseFloat(priceRange.max));
      }

      // Apply sorting - default to highest ID first (newest)
      if (sortBy === "oldest") {
        query = query.order("id", { ascending: true });
      } else if (sortBy === "price-high") {
        query = query.order("price", { ascending: false });
      } else if (sortBy === "price-low") {
        query = query.order("price", { ascending: true });
      } else {
        // Default sort: highest ID first (newest)
        query = query.order("id", { ascending: false });
      }

      // Apply pagination
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
    console.log("useEffect triggered with dependencies:", {
      currentPage,
      pageSize,
      searchQuery,
      selectedSite,
      selectedKeyword,
      priceRange,
      sortBy,
    });
    fetchListings();
  }, [
    currentPage,
    pageSize,
    searchQuery,
    selectedSite,
    selectedKeyword,
    priceRange,
    sortBy,
  ]);

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedSite, selectedKeyword, priceRange, sortBy]);

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
        <mark key={idx} className="bg-yellow-200 rounded px-1">
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
      
      // Update the listing in the database
      const { error: update_error } = await supabase
        .from("scraped_listings")
        .update({
          saved: true,
          updated_at: new Date().toISOString()
        })
        .eq("id", listing.id);

      // Add to cigar_listings
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
        // Treat unique violation (already saved) as success for UX
        if ((error as any).code !== "23505") {
          throw error || update_error;
        }
      }

      // Update local state
      setListings(prevListings => 
        prevListings.map(item => 
          item.id === listing.id 
            ? { ...item, saved: true, updated_at: new Date().toISOString() } 
            : item
        )
      );
      
      // Update saved IDs
      setSavedIds(prev => new Set([...prev, listing.id]));
      
      // Show success message
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
    } catch (e) {
      console.error("Failed to delete listing:", e);
      setError("Failed to delete listing");
    } finally {
      setDeletingId(null);
    }
  };

  // Generate page numbers for pagination
  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;

    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) {
          pages.push(i);
        }
        pages.push("...");
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push("...");
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        pages.push("...");
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i);
        }
        pages.push("...");
        pages.push(totalPages);
      }
    }

    return pages;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 p-8 mb-8">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Scraped Listings
              </h1>
              <p className="text-slate-600 mt-2">
                Browse and manage your scraped data
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-slate-800">
                {totalCount}
              </div>
              <div className="text-sm text-slate-500">Total Listings</div>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search listings..."
                className="w-full pl-10 pr-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <select
              value={selectedSite}
              onChange={(e) => setSelectedSite(e.target.value)}
              className="px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            >
              <option value="all">All Sites</option>
              <option value="ebay">eBay</option>
              <option value="craigslist">Craigslist</option>
              <option value="todocoleccion">TodoColeccion</option>
            </select>
            <select
              value={selectedKeyword}
              onChange={(e) => setSelectedKeyword(e.target.value)}
              className="px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            >
              <option value="all">All Keywords</option>
              {availableKeywords.map((keyword) => (
                <option
                  key={keyword.id}
                  value={
                    keyword.spanishkeyword ? `${keyword.spanishkeyword}` : ""
                  }
                >
                  {keyword.spanishkeyword ? `${keyword.spanishkeyword}` : ""}
                </option>
              ))}
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="price-high">Price: High to Low</option>
              <option value="price-low">Price: Low to High</option>
            </select>
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

        {/* Listings Grid */}
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl shadow-xl border border-white/20 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
          ) : listings.length === 0 ? (
            <div className="text-center py-16">
              <Search className="w-16 h-16 text-slate-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-slate-600 mb-2">
                {searchQuery ? "No matching listings" : "No listings found"}
              </h3>
              <p className="text-slate-500">
                {searchQuery
                  ? "Try adjusting your search terms"
                  : "Start scraping to see data here"}
              </p>
            </div>
          ) : (
            <>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {listings.map((listing) => (
                    <div
                      key={listing.id}
                      className="bg-white/70 backdrop-blur-sm rounded-xl border border-slate-200/50 overflow-hidden hover:shadow-xl transition-all duration-300 group"
                    >
                      {/* Image */}
                      <div className="relative h-48 bg-gradient-to-br from-slate-100 to-slate-200">
                        {listing.image_url ? (
                          <img
                            src={listing.image_url}
                            alt={listing.title}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="flex items-center justify-center h-full">
                            <ImageIcon className="w-12 h-12 text-slate-400" />
                          </div>
                        )}
                        <div className="absolute top-2 left-2">
                          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded-full font-medium">
                            {listing.site}
                          </span>
                        </div>
                      </div>

                      {/* Content */}
                      <div className="p-4">
                        <h3 className="font-semibold text-slate-800 text-lg leading-tight mb-2">
                          {highlightKeywordInTitle(
                            listing.title,
                            listing.keyword
                          )}
                        </h3>
                        <div className="mb-3">
                          <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full font-medium">
                            {listing.keyword}
                          </span>
                        </div>
                        {listing.description && (
                          <p className="text-slate-600 text-sm mb-3 line-clamp-2">
                            {listing.description}
                          </p>
                        )}

                        {/* Meta Info */}
                        <div className="space-y-2 mb-4">
                          <div className="flex items-center justify-between text-xs text-slate-500">
                            <div className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {listing.created_at
                                ? new Date(
                                    listing.created_at
                                  ).toLocaleDateString()
                                : "N/A"}
                            </div>
                            <span>ID: {listing.id}</span>
                          </div>
                          {listing.price !== null && (
                            <div className="flex items-center gap-1 text-sm">
                              <DollarSign className="w-4 h-4 text-green-600" />
                              <span className="font-semibold text-green-700">
                                ${listing.price.toFixed(2)}
                              </span>
                            </div>
                          )}
                        </div>

                        {/* Action Buttons */}
                        <div className="flex items-center gap-2 mt-2">
                          <a
                            href={listing.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 flex items-center justify-center gap-2 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 rounded-lg transition-all duration-200 font-medium text-sm"
                          >
                            <Eye className="w-4 h-4" />
                            View Listing
                            <ExternalLink className="w-3 h-3" />
                          </a>
                          <button
                            className={`p-2 rounded-lg transition-colors relative group/save ${
                              savedIds.has(listing.id)
                                ? "bg-green-50 text-green-700"
                                : "hover:bg-green-50 text-green-700"
                            }`}
                            onClick={() => handleSaveListing(listing)}
                            disabled={
                              savingId === listing.id ||
                              savedIds.has(listing.id)
                            }
                            type="button"
                            aria-label="Save listing"
                          >
                            {savingId === listing.id ? (
                              <RefreshCw className="w-4 h-4 animate-spin" />
                            ) : savedIds.has(listing.id) ? (
                              <Check className="w-4 h-4" />
                            ) : (
                              <SaveIcon className="w-4 h-4" />
                            )}
                            <span className="z-50 absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs rounded bg-slate-800 text-white opacity-0 group-hover/save:opacity-100 pointer-events-none transition-opacity">
                              {savedIds.has(listing.id) ? "Saved" : "Save"}
                            </span>
                          </button>
                          <button
                            className="p-2 rounded-lg transition-colors relative group/delete hover:bg-red-50 text-red-700"
                            onClick={() => handleDeleteListing(listing.id)}
                            disabled={deletingId === listing.id}
                            type="button"
                            aria-label="Delete listing"
                          >
                            {deletingId === listing.id ? (
                              <RefreshCw className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                            <span className="z-50 absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs rounded bg-slate-800 text-white opacity-0 group-hover/delete:opacity-100 pointer-events-none transition-opacity">
                              Delete
                            </span>
                          </button>
                          <button
                            className="p-2 rounded-lg hover:bg-blue-50 transition-colors relative group/copy"
                            onClick={async () => {
                              await navigator.clipboard.writeText(listing.url);
                              setCopiedId(listing.id);
                              setTimeout(() => setCopiedId(null), 1200);
                            }}
                            aria-label="Copy URL"
                            type="button"
                          >
                            {copiedId === listing.id ? (
                              <Check className="w-4 h-4 text-green-600" />
                            ) : (
                              <Copy className="w-4 h-4 text-slate-400 group-hover/copy:text-blue-600" />
                            )}
                            <span className="z-50 absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs rounded bg-slate-800 text-white opacity-0 group-hover/copy:opacity-100 pointer-events-none transition-opacity">
                              Copy URL
                            </span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Pagination */}
              <div className="border-t border-slate-200 bg-slate-50 px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <span className="text-sm text-slate-600">
                      Showing {(currentPage - 1) * pageSize + 1} to{" "}
                      {Math.min(currentPage * pageSize, totalCount)} of{" "}
                      {totalCount} results
                    </span>
                    <select
                      value={pageSize}
                      onChange={(e) =>
                        handlePageSizeChange(Number(e.target.value))
                      }
                      className="px-3 py-1 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={6}>6 per page</option>
                      <option value={12}>12 per page</option>
                      <option value={24}>24 per page</option>
                      <option value={48}>48 per page</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="p-2 rounded-lg hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>

                    {getPageNumbers().map((page, index) => (
                      <button
                        key={index}
                        onClick={() =>
                          typeof page === "number" && handlePageChange(page)
                        }
                        disabled={page === "..."}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                          page === currentPage
                            ? "bg-blue-600 text-white"
                            : page === "..."
                            ? "text-slate-400 cursor-default"
                            : "hover:bg-white text-slate-600"
                        }`}
                      >
                        {page}
                      </button>
                    ))}

                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="p-2 rounded-lg hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default DataPage;
