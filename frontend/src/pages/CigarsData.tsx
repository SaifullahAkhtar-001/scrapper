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
  parent_id: number;
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
  const [deletingId, setDeletingId] = useState<number | null>(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(48);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  // AI batch processing state
  const [aiRunning, setAiRunning] = useState(false);
  const [aiProcessed, setAiProcessed] = useState(0);
  const [aiTotal, setAiTotal] = useState<number | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

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
    setLoading(true);
    setError(null);
    try {
      // Build query
      let query = supabase
        .from("cigar_listings")
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

      // Apply sorting
      if (sortBy === "newest") {
        query = query.order("created_at", { ascending: false });
      } else if (sortBy === "oldest") {
        query = query.order("created_at", { ascending: true });
      } else if (sortBy === "price-high") {
        query = query.order("price", { ascending: false });
      } else if (sortBy === "price-low") {
        query = query.order("price", { ascending: true });
      }

      // Apply pagination
      const from = (currentPage - 1) * pageSize;
      const to = from + pageSize - 1;
      query = query.range(from, to);

      const { data, error, count } = await query;

      if (error) setError(error.message);
      else {
        setListings(data as ScrapedListing[]);
        setTotalCount(count || 0);
        setTotalPages(Math.ceil((count || 0) / pageSize));
      }
    } catch (err) {
      setError("Failed to fetch listings");
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

  const handleUnsaveListing = async (id: number, parent_id: number) => {
    try {
      setDeletingId(id);
      const { error: updateError } = await supabase
        .from("scraped_listings")
        .update({ saved: false })
        .eq("id", parent_id);
      const { error } = await supabase
        .from("cigar_listings")
        .delete()
        .eq("id", id);
      if (error || updateError) throw error || updateError;
      setListings((prev) => prev.filter((l) => l.id !== id));
      setTotalCount((prev) => Math.max(0, prev - 1));
    } catch (e) {
      console.error("Failed to unsave listing:", e);
      setError("Failed to unsave listing");
    } finally {
      setDeletingId(null);
    }
  };

  // Fetch total pending for progress display
  const refreshAiTotal = async () => {
    const { count } = await supabase
      .from("scraped_listings")
      .select("id", { count: "exact", head: true })
      .or("ai_status.is.null,ai_status.eq.false")
      .eq("saved", false);
    setAiTotal(count || 0);
  };

  useEffect(() => {
    refreshAiTotal();
  }, []);

  // AI classifier runner (chunked)
  const runAiClassifier = async () => {
    if (aiRunning) return;
    setAiRunning(true);
    setAiProcessed(0);
    setAiError(null);

    try {
      await refreshAiTotal();

      const apiKey = import.meta.env.VITE_OPENAI_API_KEY as string | undefined;
      const model = (import.meta.env.VITE_OPENAI_MODEL as string | undefined) || "gpt-5-nano";
      if (!apiKey) {
        throw new Error("Missing OpenAI API Key");
      }

      const BATCH_SIZE = 100;

      // Helper to pause between batches
      const pause = (ms: number) => new Promise((res) => setTimeout(res, ms));

      while (true) {
        // 1) Select next batch of unprocessed rows
        const { data: batch, error: selectError } = await supabase
          .from("scraped_listings")
          .select(
            "id,title,url,price,image_url,description,site,keyword,created_at,updated_at,saved,ai_status"
          )
          .or("ai_status.is.null,ai_status.eq.false")
          .eq("saved", false)
          .order("id", { ascending: true })
          .limit(BATCH_SIZE);

        if (selectError) throw selectError;
        if (!batch || batch.length === 0) break;

        const ids = batch.map((b) => b.id);

        // 2) Build Groq payload to classify
        const titlesPayload = batch.map((b) => ({ id: b.id, title: b.title }));
        const systemInstruction = `You are a strict cigar listing classifier. You will receive a JSON object with an array of items {id, title}. Return ONLY a JSON array of objects for items that are ACTUAL SMOKEABLE CIGARS available for purchase. Each object must include {id, title}.

INCLUDE ONLY:
- Individual cigars or cigar sticks with clear quantity (1-25 cigars)
- Cigars with specific brand names AND explicit cigar quantities
- Listings that clearly state "X cigars" or "X puros" where X is a number
- Single cigars or small bundles/packs of cigars for smoking

EXCLUDE ALL:

CONTAINERS & EMPTY ITEMS:
- Empty cigar boxes ("caja vacía", "empty box", "caja sin puros", "box only")
- Cigar boxes without cigars ("8 CIGAR BOXES", "caja de puros" without cigar count)
- Tins without cigars ("cigar tin", "lata", "tin box", "tobacco tin")
- Any listing mentioning "empty", "vacío/a", "sin contenido"

ACCESSORIES & NON-SMOKING ITEMS:
- Humidors, cutters, lighters, ashtrays, hygrometers
- Leather cases, pouches, travel cases, storage containers
- Cigar stands, holders, displays
- Collectibles, memorabilia, vintage items
- Dollhouse miniatures or toys

MEDIA & PROMOTIONAL ITEMS:
- Pictures, photographs, prints, artwork of cigars
- Vintage advertising materials, posters, signs
- Music CDs, cassettes, DVDs
- Books, magazines, catalogs
- Labels, bands, wrappers (without cigars)

BULK/UNCLEAR QUANTITIES:
- "Box lot", "mixed lot", "estate lot" without specific cigar count
- "Wholesale lot", "bulk items"
- Items where quantity is unclear or focused on containers
- "Various", "assorted", "mixed" without stating actual cigar numbers

SPANISH EXCLUSIONS:
- "Solo caja", "únicamente caja", "caja coleccionable"
- "Lata vacía", "tin vacío"
- "Accesorios", "colección", "memorabilia"
- "Imagen", "foto", "cuadro", "poster"
- "Vintage", "antiguo", "coleccionable"

QUALITY CHECKS:
- Must explicitly mention smokeable cigars/puros with quantity
- Cannot be primarily about the packaging/container
- Must be intended for actual smoking, not display/collection
- Avoid listings where the value is in the container, not contents

Return ONLY valid JSON array. No explanatory text.`
        const payload = {
          model,
          temperature: 0,
          messages: [
            { role: "system", content: systemInstruction },
            {
              role: "user",
              content: JSON.stringify({ items: titlesPayload }),
            },
          ],
        } as const;

        // 3) Call Groq
        const response = await fetch(
          "https://api.openai.com/v1/chat/completions",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${apiKey}`,
            },
            body: JSON.stringify(payload),
          }
        );

        if (!response.ok) {
          const txt = await response.text();
          throw new Error(`Groq API error: ${response.status} ${txt}`);
        }

        const json = await response.json();
        const raw = json?.choices?.[0]?.message?.content ?? "";

        // 4) Parse model JSON response robustly
        let positives: Array<{ id: number; title: string }> = [];
        try {
          const start = raw.indexOf("[");
          const end = raw.lastIndexOf("]");
          const slice = start >= 0 && end >= 0 ? raw.substring(start, end + 1) : raw;
          const parsed = JSON.parse(slice);
          if (Array.isArray(parsed)) {
            positives = parsed
              .map((x) => ({ id: Number(x.id), title: String(x.title || "") }))
              .filter((x) => Number.isFinite(x.id));
          }
        } catch (e) {
          console.warn("Failed to parse Groq response, raw=", raw);
          positives = [];
        }

        const positiveIds = positives.map((p) => p.id);

        // 5) Upsert positives into cigar_listings (batch)
        if (positiveIds.length > 0) {
          const { data: sourceRows, error: srcErr } = await supabase
            .from("scraped_listings")
            .select(
              "id,title,url,price,image_url,description,site,keyword,created_at,updated_at"
            )
            .in("id", positiveIds);
          if (srcErr) throw srcErr;

          const rowsToInsert = (sourceRows || []).map((r) => ({
            title: r.title,
            url: r.url,
            price: r.price,
            image_url: r.image_url,
            description: r.description,
            site: r.site,
            keyword: r.keyword,
            created_at: r.created_at,
            updated_at: r.updated_at,
            parent_id: r.id,
          }));

          if (rowsToInsert.length > 0) {
            const { error: insErr } = await supabase
              .from("cigar_listings")
              .upsert(rowsToInsert, { onConflict: "url", ignoreDuplicates: true });
            if (insErr) throw insErr;

            const { error: savedErr } = await supabase
              .from("scraped_listings")
              .update({ saved: true })
              .in("id", positiveIds);
            if (savedErr) throw savedErr;
          }
        }

        // 6) Mark processed batch ai_status = true
        const { error: updErr } = await supabase
          .from("scraped_listings")
          .update({ ai_status: true })
          .in("id", ids);
        if (updErr) throw updErr;

        setAiProcessed((prev) => prev + batch.length);
        await pause(250); // yield UI
      }

      // Refresh counts and visible listings
      await refreshAiTotal();
      await fetchListings();
    } catch (e: any) {
      console.error(e);
      setAiError(e?.message || "AI processing failed");
    } finally {
      setAiRunning(false);
    }
  };

  // Generate page numbers for pagination
  const getPageNumbers = () => {
    const pages = [] as Array<number | string>;
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
              <p className="text-slate-600 mt-2">Browse and manage your scraped data</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-3xl font-bold text-slate-800">{totalCount}</div>
                <div className="text-sm text-slate-500">Total Listings</div>
              </div>
              <button
                type="button"
                onClick={runAiClassifier}
                disabled={aiRunning}
                className={`px-4 py-2 rounded-lg font-medium text-white transition-all ${aiRunning
                  ? "bg-slate-400 cursor-not-allowed"
                  : "bg-green-600 hover:bg-green-700"
                  }`}
                aria-label="Run AI classifier"
                title="Classify scraped listings and push cigars"
              >
                <span className="inline-flex items-center gap-2">
                  {aiRunning ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : null}
                  {aiRunning ? "Processing..." : "Classify with AI"}
                </span>
              </button>
            </div>
          </div>

          {/* AI status */}
          {(aiRunning || aiError || (aiTotal ?? 0) > 0) && (
            <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-xl p-4 mb-4">
              <div className="flex items-center gap-2 text-slate-700">
                {aiError ? (
                  <>
                    <AlertCircle className="w-5 h-5 text-red-500" />
                    <span className="text-red-600">{aiError}</span>
                  </>
                ) : (
                  <>
                    {aiRunning ? (
                      <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-slate-500" />
                    )}
                    <span>
                      Pending: {aiTotal ?? 0} | Processed this run: {aiProcessed}
                    </span>
                  </>
                )}
              </div>
              {!aiRunning && (
                <button
                  type="button"
                  onClick={refreshAiTotal}
                  className="text-sm text-blue-600 hover:underline"
                >
                  Refresh pending
                </button>
              )}
            </div>
          )}

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
                  value={keyword.spanishkeyword ? `${keyword.spanishkeyword}` : ""}
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
                          {highlightKeywordInTitle(listing.title, listing.keyword)}
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
                                ? new Date(listing.created_at).toLocaleDateString()
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
                            className="p-2 rounded-lg transition-colors relative group/unsave hover:bg-red-50 text-red-700"
                            onClick={() => handleUnsaveListing(listing.id, listing.parent_id)}
                            disabled={deletingId === listing.id}
                            type="button"
                            aria-label="Unsave listing"
                          >
                            {deletingId === listing.id ? (
                              <RefreshCw className="w-4 h-4 animate-spin" />
                            ) : (
                              <Trash2 className="w-4 h-4" />
                            )}
                            <span className="z-50 absolute left-1/2 -translate-x-1/2 bottom-full mb-2 px-2 py-1 text-xs rounded bg-slate-800 text-white opacity-0 group-hover/unsave:opacity-100 pointer-events-none transition-opacity">
                              Unsave
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
                      Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalCount)} of {totalCount} results
                    </span>
                    <select
                      value={pageSize}
                      onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                      className="px-3 py-1 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={6}>6 per page</option>
                      <option value={12}>12 per page</option>
                      <option value={24}>24 per page</option>
                      <option value={48}>48 per page</option>
                      <option value={100}>100 per page</option>
                      <option value={500}>500 per page</option>
                      <option value={1000}>1000 per page</option>
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
                        onClick={() => typeof page === "number" && handlePageChange(page)}
                        disabled={page === "..."}
                        className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${page === currentPage
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
