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
  Trash2,
  Sparkles,
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

  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(48);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);

  const [aiRunning, setAiRunning] = useState(false);
  const [aiProcessed, setAiProcessed] = useState(0);
  const [aiTotal, setAiTotal] = useState<number | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

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
      let query = supabase
        .from("cigar_listings")
        .select("*", { count: "exact" });

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

      if (sortBy === "newest") {
        query = query.order("created_at", { ascending: false });
      } else if (sortBy === "oldest") {
        query = query.order("created_at", { ascending: true });
      } else if (sortBy === "price-high") {
        query = query.order("price", { ascending: false });
      } else if (sortBy === "price-low") {
        query = query.order("price", { ascending: true });
      }

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
        <mark key={idx} className="bg-amber-100 text-amber-900 rounded px-0.5">
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

      const pause = (ms: number) => new Promise((res) => setTimeout(res, ms));

      while (true) {
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

        const { error: updErr } = await supabase
          .from("scraped_listings")
          .update({ ai_status: true })
          .in("id", ids);
        if (updErr) throw updErr;

        setAiProcessed((prev) => prev + batch.length);
        await pause(250);
      }

      await refreshAiTotal();
      await fetchListings();
    } catch (e: any) {
      console.error(e);
      setAiError(e?.message || "AI processing failed");
    } finally {
      setAiRunning(false);
    }
  };

  return (
    <PageLayout wide>
      <PageHeader
        title="Cigar Listings"
        description="Curated cigar listings from scraped data"
        stat={{ value: totalCount, label: "Total" }}
        actions={
          <Button
            onClick={runAiClassifier}
            disabled={aiRunning}
            variant="secondary"
          >
            {aiRunning ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
            {aiRunning ? "Processing..." : "Classify with AI"}
          </Button>
        }
      />

      {(aiRunning || aiError || (aiTotal ?? 0) > 0) && (
        <Card className="mb-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-zinc-600">
              {aiError ? (
                <>
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  <span className="text-red-600">{aiError}</span>
                </>
              ) : (
                <>
                  {aiRunning && <RefreshCw className="w-4 h-4 animate-spin text-zinc-400" />}
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
                className="text-sm text-zinc-600 hover:text-zinc-900 underline underline-offset-2"
              >
                Refresh pending
              </button>
            )}
          </div>
        </Card>
      )}

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
                value={keyword.spanishkeyword ? `${keyword.spanishkeyword}` : ""}
              >
                {keyword.spanishkeyword ? `${keyword.spanishkeyword}` : ""}
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
            title={searchQuery ? "No matching listings" : "No listings found"}
            description={searchQuery ? "Try adjusting your search terms" : "Start scraping to see data here"}
          />
        ) : (
          <>
            <div className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {listings.map((listing) => (
                  <div
                    key={listing.id}
                    className="border border-zinc-200 rounded-lg overflow-hidden bg-white hover:border-zinc-300 transition-colors"
                  >
                    <div className="relative h-44 bg-zinc-100">
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
                      <div className="absolute top-2 left-2">
                        <Badge variant="info">{listing.site}</Badge>
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
                          className="p-1.5 rounded-md border border-zinc-200 text-zinc-500 hover:bg-red-50 hover:text-red-600 hover:border-red-200 transition-colors"
                          onClick={() => handleUnsaveListing(listing.id, listing.parent_id)}
                          disabled={deletingId === listing.id}
                          type="button"
                          aria-label="Unsave listing"
                          title="Unsave"
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
