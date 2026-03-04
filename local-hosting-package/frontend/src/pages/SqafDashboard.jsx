/**
 * SQAAF Dashboard – School Quality Assessment and Accreditation Framework
 * Pune District analytics: KPIs, score bands, block/section/school diagnostics, intervention priorities.
 * Data source: MongoDB (sqaaf_meta, sqaaf_schools, sqaaf_blocks). Load data via ETL: POST /api/sqaaf/import.
 */
import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import PageTransition from "@/components/PageTransition";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  ClipboardCheck,
  RefreshCw,
  School,
  TrendingUp,
  Target,
  AlertTriangle,
  BarChart3,
  PieChart as PieChartIcon,
  MapPin,
  Users,
  Download,
  Search,
  Menu,
  X,
} from "lucide-react";
import { toast } from "sonner";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  PieChart,
  Pie,
  Legend,
  LabelList,
} from "recharts";
import { getBackendUrl } from "@/lib/backend";

const API = `${getBackendUrl()}/api`;

/** Format number to exactly 2 decimal places for display across the dashboard. */
function fmt2(v) {
  if (v == null || v === "") return "—";
  const n = Number(v);
  if (Number.isNaN(n)) return "—";
  return n.toFixed(2);
}

const BAND_COLORS = {
  Critical: "#ef4444",
  "Needs Focus": "#f59e0b",
  Developing: "#eab308",
  Strong: "#22c55e",
  Exemplary: "#3b82f6",
};

const SQAAF_NAV_ITEMS = [
  { id: "executive", icon: BarChart3, label: "Executive Overview" },
  { id: "blocks", icon: MapPin, label: "Block Performance" },
  { id: "sections", icon: Target, label: "Domain/Section" },
  { id: "schools", icon: School, label: "School Diagnostics" },
  { id: "intervention", icon: AlertTriangle, label: "Policy Action" },
];

const KPICard = ({ label, value, suffix = "", icon: Icon, color = "blue", description }) => {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    green: "bg-emerald-50 text-emerald-600",
    red: "bg-red-50 text-red-600",
    amber: "bg-amber-50 text-amber-600",
    purple: "bg-purple-50 text-purple-600",
    cyan: "bg-cyan-50 text-cyan-600",
  };
  return (
    <Card className="border-slate-200">
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">{label}</p>
            <div className="flex items-baseline gap-1 mt-1">
              <span className="text-2xl font-bold text-slate-900 tabular-nums" style={{ fontFamily: "Manrope" }}>
                {typeof value === "number" ? fmt2(value) : value ?? "—"}
              </span>
              {suffix && <span className="text-lg text-slate-500">{suffix}</span>}
            </div>
            {description && <p className="text-xs text-slate-400 mt-1">{description}</p>}
          </div>
          {Icon && (
            <div className={`p-2 rounded-lg ${colors[color]}`}>
              <Icon className="w-5 h-5" strokeWidth={1.5} />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

function downloadCSV(rows, filename) {
  if (!rows.length) return;
  const headers = Object.keys(rows[0]);
  const csv = [headers.join(","), ...rows.map((r) => headers.map((h) => JSON.stringify(r[h] ?? "")).join(","))].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

/** Truncate long question text for Y-axis; full text in tooltip. */
function truncateQuestion(text, maxLen = 52) {
  if (!text || typeof text !== "string") return "";
  const t = text.trim();
  return t.length <= maxLen ? t : t.slice(0, maxLen).trim() + "…";
}

/** Tooltip for Bottom 10 Questions chart: show full question and mean. */
function BottomQuestionsTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const row = payload[0]?.payload;
  const question = row?.question ?? label;
  const mean = row?.["mean_score_%"];
  return (
    <div className="rounded-lg border border-slate-200 bg-white px-3 py-2 shadow-md max-w-sm">
      <p className="text-xs font-medium text-slate-500 mb-1">Mean: {mean != null ? `${fmt2(mean)}%` : "—"}</p>
      <p className="text-xs text-slate-700 whitespace-normal break-words">{question}</p>
    </div>
  );
}

const SqafDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [blockPerf, setBlockPerf] = useState(null);
  const [sectionAnalysis, setSectionAnalysis] = useState(null);
  const [schoolsList, setSchoolsList] = useState({ schools: [], total: 0 });
  const [intervention, setIntervention] = useState(null);
  const [schoolDetail, setSchoolDetail] = useState(null);
  const [activeTab, setActiveTab] = useState("executive");
  const [blockFilter, setBlockFilter] = useState("");
  const [clusterFilter, setClusterFilter] = useState("");
  const [managementFilter, setManagementFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [schoolSearch, setSchoolSearch] = useState("");
  const [selectedSchoolCode, setSelectedSchoolCode] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [overviewError, setOverviewError] = useState(null);
  const [importLoading, setImportLoading] = useState(false);
  const fetchOverview = useCallback(async () => {
    setOverviewError(null);
    try {
      const res = await axios.get(`${API}/sqaaf/overview`, {
        params: {
          block: blockFilter || undefined,
          cluster: clusterFilter || undefined,
          school_management: managementFilter || undefined,
          school_category: categoryFilter || undefined,
        },
      });
      setOverview(res.data);
    } catch (e) {
      console.error(e);
      const msg = e.response?.data?.detail ?? e.message ?? "Failed to load SQAAF overview";
      setOverviewError(Array.isArray(msg) ? msg.join(" ") : msg);
      toast.error("Failed to load SQAAF overview");
      setOverview(null);
    }
  }, [blockFilter, clusterFilter, managementFilter, categoryFilter]);

  const fetchBlockPerf = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/sqaaf/block-performance`, { params: { block: blockFilter || undefined } });
      setBlockPerf(res.data);
    } catch (e) {
      console.error(e);
      setBlockPerf(null);
    }
  }, [blockFilter]);

  const fetchSectionAnalysis = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/sqaaf/section-analysis`);
      setSectionAnalysis(res.data);
    } catch (e) {
      console.error(e);
      setSectionAnalysis(null);
    }
  }, []);

  const fetchSchools = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/sqaaf/schools`, {
        params: {
          block: blockFilter || undefined,
          cluster: clusterFilter || undefined,
          school_management: managementFilter || undefined,
          school_category: categoryFilter || undefined,
          search: schoolSearch || undefined,
          limit: 500,
          offset: 0,
        },
      });
      setSchoolsList({ schools: res.data.schools, total: res.data.total });
    } catch (e) {
      console.error(e);
      setSchoolsList({ schools: [], total: 0 });
    }
  }, [blockFilter, clusterFilter, managementFilter, categoryFilter, schoolSearch]);

  const fetchIntervention = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/sqaaf/intervention`, { params: { block: blockFilter || undefined } });
      setIntervention(res.data);
    } catch (e) {
      console.error(e);
      setIntervention(null);
    }
  }, [blockFilter]);

  const fetchSchoolDetail = useCallback(async (code) => {
    if (!code) return;
    try {
      const res = await axios.get(`${API}/sqaaf/school-detail/${encodeURIComponent(code)}`);
      setSchoolDetail(res.data);
    } catch (e) {
      toast.error("School detail not found");
      setSchoolDetail(null);
    }
  }, []);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchOverview(), fetchBlockPerf(), fetchSectionAnalysis(), fetchSchools(), fetchIntervention()]);
    setLoading(false);
  }, [fetchOverview, fetchBlockPerf, fetchSectionAnalysis, fetchSchools, fetchIntervention]);

  const runImport = useCallback(async () => {
    setImportLoading(true);
    setOverviewError(null);
    try {
      const res = await axios.post(`${API}/sqaaf/import`);
      toast.success(`Loaded ${res.data?.n_schools ?? 0} schools into MongoDB`);
      await fetchAll();
    } catch (e) {
      const msg = e.response?.data?.detail ?? e.message ?? "Import failed";
      setOverviewError(Array.isArray(msg) ? msg.join(" ") : msg);
      toast.error("SQAAF import failed");
    } finally {
      setImportLoading(false);
    }
  }, [fetchAll]);

  const hasData = overview && overview.n_schools > 0;

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  useEffect(() => {
    if (selectedSchoolCode) fetchSchoolDetail(selectedSchoolCode);
  }, [selectedSchoolCode, fetchSchoolDetail]);

  useEffect(() => {
    if (activeTab === "blocks" && hasData && !blockPerf) fetchBlockPerf();
  }, [activeTab, hasData, blockPerf, fetchBlockPerf]);

  if (loading && !overview) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <div className="animate-fade-in" data-testid="sqaaf-dashboard">
      {!hasData ? (
        <div className="space-y-6 p-4 lg:p-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: "Manrope" }}>
                SQAAF Dashboard
              </h1>
              <p className="text-slate-500 mt-1">School Quality Assessment &amp; Accreditation • Pune District</p>
            </div>
            <Button variant="outline" size="sm" onClick={fetchAll}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
          <Card className="border-slate-200">
            <CardContent className="py-12 text-center">
              <ClipboardCheck className="w-16 h-16 mx-auto text-slate-300 mb-4" />
              <h3 className="text-xl font-semibold text-slate-700 mb-2">No SQAAF Data Available</h3>
              <p className="text-slate-500 mb-2">The dashboard reads from MongoDB. Load the Excel file once using the button below (or run ETL: <code className="text-xs bg-slate-100 px-1 rounded">POST /api/sqaaf/import</code>).</p>
              <Button className="mt-4" onClick={runImport} disabled={importLoading}>
                {importLoading ? "Loading…" : "Load from Excel (ETL)"}
              </Button>
              {overviewError && (
                <div className="mt-4 max-w-xl mx-auto text-left">
                  <p className="text-sm font-medium text-amber-800 mb-1">Error:</p>
                  <p className="text-sm text-amber-700">{overviewError}</p>
                  <p className="text-xs text-slate-500 mt-2">Tip: Place Pune_District_SQAAF.xlsx in <code className="bg-slate-100 px-1 rounded">backend/data/excel/</code> or set <code className="bg-slate-100 px-1 rounded">SQAAF_EXCEL_PATH</code> to its full path.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="dashboard-layout">
          {/* Left sidebar – same theme as MH Education Dashboard */}
          <aside className={`sidebar fixed inset-y-0 left-0 z-50 w-60 transform transition-transform duration-300 lg:translate-x-0 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
            <div className="flex flex-col h-full">
              <div className="flex items-center justify-between px-4 py-5 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
                    <ClipboardCheck className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-lg font-bold text-white tracking-tight" style={{ fontFamily: "Manrope" }}>
                      SQAAF
                    </h1>
                    <p className="text-xs text-slate-400">School Quality Assessment</p>
                  </div>
                </div>
                <button
                  type="button"
                  className="lg:hidden text-slate-400 hover:text-white p-1"
                  onClick={() => setSidebarOpen(false)}
                  aria-label="Close menu"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <nav className="flex-1 py-4 overflow-y-auto">
                <div className="px-3 mb-2">
                  <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                    Sections
                  </span>
                </div>
                {SQAAF_NAV_ITEMS.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className={`sidebar-item w-full text-left ${activeTab === item.id ? "active" : ""}`}
                    onClick={() => {
                      setActiveTab(item.id);
                      setSidebarOpen(false);
                    }}
                    data-testid={`sqaaf-nav-${item.id}`}
                  >
                    <item.icon className="w-5 h-5 shrink-0" strokeWidth={1.5} />
                    <span className="font-medium">{item.label}</span>
                  </button>
                ))}
              </nav>
            </div>
          </aside>
          {sidebarOpen && (
            <div
              className="fixed inset-0 bg-black/50 z-40 lg:hidden"
              onClick={() => setSidebarOpen(false)}
              aria-hidden
            />
          )}
          <main className="main-content min-h-screen">
            <div className="p-4 lg:p-8">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
                <div className="flex items-center gap-3">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="lg:hidden shrink-0"
                    onClick={() => setSidebarOpen(true)}
                    aria-label="Open menu"
                  >
                    <Menu className="w-5 h-5" />
                  </Button>
                  <div>
                    <h1 className="text-2xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: "Manrope" }}>
                      {SQAAF_NAV_ITEMS.find((n) => n.id === activeTab)?.label ?? "SQAAF"}
                    </h1>
                    <p className="text-slate-500 text-sm mt-0.5">
                      School Quality Assessment &amp; Accreditation • Pune District • 128 Questions • Data from MongoDB
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm" onClick={fetchAll} className="shrink-0">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
              </div>
              <PageTransition>
                {activeTab === "executive" && (
                <div className="space-y-6">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                <KPICard label="Overall SQAAF Score" value={overview.district_mean} suffix="%" icon={TrendingUp} color="blue" description="District mean" />
                <KPICard label="Median Score" value={overview.district_median} suffix="%" icon={BarChart3} color="purple" />
                <KPICard label="Std Dev (Inequality)" value={overview.district_std} icon={AlertTriangle} color="amber" description="Performance spread" />
                <KPICard label="Completion Rate" value={overview.completion_rate} suffix="%" icon={ClipboardCheck} color="cyan" description="Mean Answered %" />
                <KPICard label="Full Compliance" value={overview.full_compliance_rate} suffix="%" icon={Target} color="green" description={`${overview.full_compliance_count} schools (128/128)`} />
                <KPICard label="% Critical (≤40)" value={overview.critical_pct} suffix="%" icon={AlertTriangle} color="red" />
                <KPICard label="Intervention Load" value={overview.intervention_load} suffix="%" icon={AlertTriangle} color="red" description="Schools &lt;60%" />
                <KPICard label="Equity Gap" value={overview.equity_gap} icon={Users} color="amber" description="Top25% − Bottom25%" />
                <KPICard label="Inter-Block Gap" value={overview.block_gap_display} icon={MapPin} color="purple" description="Best − Worst block mean" />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-slate-200">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">SQAAF Score Distribution</CardTitle>
                    <CardDescription>Histogram of school scores (5% bins). Shows spread across the district.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={overview.score_histogram || []}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="bin_start" label={{ value: "Score %", position: "insideBottom", offset: -5 }} />
                          <YAxis />
                          <Tooltip formatter={(v) => [v, "Schools"]} labelFormatter={(l) => `Score ${fmt2(l)}%`} />
                          <Bar dataKey="count" name="Schools" fill="#3b82f6" radius={[2, 2, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
                <Card className="border-slate-200">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">Score Band Distribution</CardTitle>
                    <CardDescription>Share of schools in each quality band (Critical to Exemplary).</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={(overview.band_distribution || []).filter((d) => d.count > 0)}
                            dataKey="count"
                            nameKey="band"
                            cx="50%"
                            cy="50%"
                            innerRadius={60}
                            outerRadius={95}
                            paddingAngle={2}
                            label={({ band, pct }) => `${band} ${fmt2(pct)}%`}
                          >
                            {(overview.band_distribution || []).filter((d) => d.count > 0).map((entry, i) => (
                              <Cell key={i} fill={BAND_COLORS[entry.band] || "#94a3b8"} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(v, n, p) => [`${v} schools (${fmt2(p.payload.pct)}%)`, p.payload.band]} />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="border-slate-200">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">Top 5 vs Bottom 5 Blocks by Mean Score</CardTitle>
                    <CardDescription>Best and worst performing blocks for targeted support.</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={[
                            ...(overview.top5_blocks || []).map((b) => ({ ...b, block: `${b.block} (Top)`, fill: "#22c55e" })),
                            ...(overview.bottom5_blocks || []).map((b) => ({ ...b, block: `${b.block} (Bottom)`, fill: "#ef4444" })),
                          ]}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="block" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={70} />
                          <YAxis />
                          <Tooltip formatter={(v) => [fmt2(v), "Mean %"]} />
                          <Bar dataKey="mean_score" name="Mean Score %" radius={[4, 4, 0, 0]}>
                            <LabelList dataKey="mean_score" position="top" formatter={(v) => fmt2(v)} />
                            {[
                              ...(overview.top5_blocks || []).map((_, i) => <Cell key={`t${i}`} fill="#22c55e" />),
                              ...(overview.bottom5_blocks || []).map((_, i) => <Cell key={`b${i}`} fill="#ef4444" />),
                            ]}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
                <Card className="border-slate-200">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">Inter-Block Performance Gap</CardTitle>
                    <CardDescription>Difference between best and worst block mean scores (equity indicator).</CardDescription>
                  </CardHeader>
                  <CardContent className="flex items-center justify-center h-64">
                    <div className="text-center">
                      <p className="text-5xl font-bold text-slate-800" style={{ fontFamily: "Manrope" }}>
                        {typeof overview.block_gap_display === "number" ? fmt2(overview.block_gap_display) : overview.block_gap_display}
                      </p>
                      <p className="text-slate-500 mt-1">points (max block mean − min block mean)</p>
                    </div>
                  </CardContent>
                </Card>
              </div>
                </div>
                )}

                {activeTab === "blocks" && (
                <div className="space-y-6">
              {!blockPerf ? (
                <Card className="border-slate-200">
                  <CardContent className="py-12 text-center">
                    <MapPin className="w-12 h-12 mx-auto text-slate-300 mb-3" />
                    <p className="text-slate-600 font-medium">Block performance data not loaded</p>
                    <p className="text-slate-500 text-sm mt-1">Click Refresh above or retry below.</p>
                    <Button className="mt-4" variant="outline" size="sm" onClick={() => fetchBlockPerf()} disabled={loading}>
                      {loading ? "Loading…" : "Load Block Performance"}
                    </Button>
                  </CardContent>
                </Card>
              ) : (blockPerf.block_summary && blockPerf.block_summary.length === 0) ? (
                <Card className="border-slate-200">
                  <CardContent className="py-12 text-center text-slate-500">
                    No block-level data available for the current filters.
                  </CardContent>
                </Card>
              ) : blockPerf ? (
                <>
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">Mean SQAAF Score by Block</CardTitle>
                        <CardDescription>Ranked by mean score (highest first).</CardDescription>
                      </div>
                      <Button variant="outline" size="sm" onClick={() => downloadCSV(blockPerf.block_summary || [], "sqaaf_block_summary.csv")}>
                        <Download className="w-4 h-4 mr-2" />
                        Download CSV
                      </Button>
                    </CardHeader>
                    <CardContent>
                      <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={blockPerf.block_summary || []} layout="vertical" margin={{ left: 80 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis type="number" domain={[0, 100]} />
                            <YAxis dataKey="block" type="category" width={75} tick={{ fontSize: 11 }} />
                            <Tooltip formatter={(v) => [fmt2(v), "Mean %"]} />
                            <Bar dataKey="mean" name="Mean %" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Block × Section Mean Scores (Top 10 Sections)</CardTitle>
                      <CardDescription>Heatmap: darker green = higher score.</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto">
                        <Table>
                          <TableHeader>
                            <TableRow className="bg-slate-50">
                              <TableHead className="font-medium">Block</TableHead>
                              <TableHead className="font-medium text-right">Schools</TableHead>
                              {(blockPerf.heatmap_sections || []).map((s) => (
                                <TableHead key={s} className="text-right font-medium">{s}</TableHead>
                              ))}
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {(blockPerf.heatmap || []).map((row, i) => (
                              <TableRow key={i}>
                                <TableCell className="font-medium">{row.block}</TableCell>
                                <TableCell className="text-right tabular-nums">{row.schools}</TableCell>
                                {(blockPerf.heatmap_sections || []).map((s) => (
                                  <TableCell key={s} className="text-right tabular-nums" style={{ backgroundColor: `rgba(34, 197, 94, ${(row[s] || 0) / 100})` }}>
                                    {row[s] != null ? fmt2(row[s]) : "–"}
                                  </TableCell>
                                ))}
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Block Summary Table</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50">
                            <TableHead>Block</TableHead>
                            <TableHead className="text-right">Schools</TableHead>
                            <TableHead className="text-right">Mean</TableHead>
                            <TableHead className="text-right">Median</TableHead>
                            <TableHead className="text-right">Std Dev</TableHead>
                            <TableHead className="text-right">% Critical</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {(blockPerf.block_summary || []).map((b, i) => (
                            <TableRow key={i}>
                              <TableCell className="font-medium">{b.block}</TableCell>
                              <TableCell className="text-right tabular-nums">{b.schools}</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(b.mean)}</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(b.median)}</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(b.std)}</TableCell>
                              <TableCell className="text-right">
                                <Badge className={b.critical_pct > 20 ? "bg-red-100 text-red-700" : "bg-slate-100"}>{fmt2(b.critical_pct)}%</Badge>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </>
              ) : null}
                </div>
                )}

                {activeTab === "sections" && (
                <div className="space-y-6">
              {sectionAnalysis && (
                <>
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between">
                      <div>
                        <CardTitle className="text-lg">Section Mean Scores (Low to High)</CardTitle>
                        <CardDescription>Domain performance; lower sections need focus.</CardDescription>
                      </div>
                      <Button variant="outline" size="sm" onClick={() => downloadCSV(sectionAnalysis.section_summary || [], "sqaaf_section_summary.csv")}>
                        <Download className="w-4 h-4 mr-2" />
                        Download CSV
                      </Button>
                    </CardHeader>
                    <CardContent>
                      <div className="h-96">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={sectionAnalysis.section_means_sorted || []} layout="vertical" margin={{ left: 40 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis type="number" domain={[0, 100]} />
                            <YAxis dataKey="section" type="category" width={50} tick={{ fontSize: 10 }} />
                            <Tooltip formatter={(v) => [fmt2(v), "Mean %"]} />
                            <Bar dataKey="mean" name="Mean %" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Section Gap vs District Mean</CardTitle>
                      <CardDescription>Divergence: Section mean − District mean (negative = below average).</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={sectionAnalysis.section_means_sorted || []} margin={{ left: 40 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis dataKey="section" tick={{ fontSize: 10 }} />
                            <YAxis />
                            <Tooltip formatter={(v) => [fmt2(v), "Gap"]} />
                            <Bar dataKey="gap" name="Gap (pts)" radius={[4, 4, 0, 0]}>
                              {(sectionAnalysis.section_means_sorted || []).map((entry, i) => (
                                <Cell key={i} fill={entry.gap < 0 ? "#ef4444" : "#22c55e"} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Section Summary</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50">
                            <TableHead>Section</TableHead>
                            <TableHead className="text-right">Questions</TableHead>
                            <TableHead className="text-right">Coverage %</TableHead>
                            <TableHead className="text-right">Mean</TableHead>
                            <TableHead className="text-right">Median</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {(sectionAnalysis.section_summary || []).map((s, i) => (
                            <TableRow key={i}>
                              <TableCell className="font-medium">{s.section}</TableCell>
                              <TableCell className="text-right tabular-nums">{s.question_count}</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(s["coverage_%"])}%</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(s.mean)}</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(s.median)}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </>
              )}
                </div>
                )}

                {activeTab === "schools" && (
                <div className="space-y-6">
              <Card className="border-slate-200">
                <CardHeader className="pb-2 flex flex-row items-center justify-between">
                  <CardTitle className="text-lg">Schools</CardTitle>
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                      <Input
                        placeholder="Search by name or code..."
                        className="pl-8 w-64"
                        value={schoolSearch}
                        onChange={(e) => setSchoolSearch(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && fetchSchools()}
                      />
                    </div>
                    <Button size="sm" onClick={fetchSchools}>Search</Button>
                    <Button variant="outline" size="sm" onClick={() => downloadCSV(schoolsList.schools, "sqaaf_schools.csv")}>
                      <Download className="w-4 h-4 mr-2" />
                      Download CSV
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto max-h-[400px] overflow-y-auto">
                    <Table>
                      <TableHeader>
                        <TableRow className="bg-slate-50">
                          <TableHead>School Code</TableHead>
                          <TableHead>School Name</TableHead>
                          <TableHead>Block</TableHead>
                          <TableHead>Cluster</TableHead>
                          <TableHead>Management</TableHead>
                          <TableHead>Category</TableHead>
                          <TableHead className="text-right">Answered %</TableHead>
                          <TableHead className="text-right">SQAAF %</TableHead>
                          <TableHead>Band</TableHead>
                          <TableHead></TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {schoolsList.schools.map((s, i) => (
                          <TableRow
                            key={i}
                            className={selectedSchoolCode === s.school_code ? "bg-blue-50" : ""}
                            onClick={() => setSelectedSchoolCode(s.school_code)}
                          >
                            <TableCell className="font-mono text-sm">{s.school_code}</TableCell>
                            <TableCell className="max-w-[180px] truncate">{s.school_name}</TableCell>
                            <TableCell>{s.block}</TableCell>
                            <TableCell>{s.cluster}</TableCell>
                            <TableCell>{s.school_management}</TableCell>
                            <TableCell>{s.school_category}</TableCell>
                            <TableCell className="text-right tabular-nums">{fmt2(s["Answered_%"])}%</TableCell>
                            <TableCell className="text-right tabular-nums font-medium">{fmt2(s["SQAAF_Score_%"])}</TableCell>
                            <TableCell>
                              <Badge style={{ backgroundColor: BAND_COLORS[s.Band] || "#94a3b8", color: "#fff" }}>{s.Band}</Badge>
                            </TableCell>
                            <TableCell>
                              <Button size="sm" variant="ghost" onClick={(ev) => { ev.stopPropagation(); setSelectedSchoolCode(s.school_code); }}>Detail</Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  <p className="text-sm text-slate-500 mt-2">Showing {schoolsList.schools.length} of {schoolsList.total}. Click a row or Detail to see section profile and lowest questions.</p>
                </CardContent>
              </Card>
              {schoolDetail && (
                <Card className="border-slate-200 border-l-4 border-l-blue-500">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-lg">School Detail: {schoolDetail.school?.school_name || schoolDetail.school?.school_code}</CardTitle>
                    <CardDescription>Section score profile vs block and district; lowest 10 questions.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={schoolDetail.section_profile || []} margin={{ left: 50 }}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis dataKey="section" tick={{ fontSize: 9 }} />
                          <YAxis domain={[0, 100]} />
                          <Tooltip formatter={(v) => fmt2(v)} />
                          <Legend />
                          <Bar dataKey="school_score" name="School" fill="#3b82f6" radius={[2, 2, 0, 0]} />
                          <Bar dataKey="block_mean" name="Block mean" fill="#22c55e" radius={[2, 2, 0, 0]} />
                          <Bar dataKey="district_mean" name="District mean" fill="#94a3b8" radius={[2, 2, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                    <div>
                      <p className="font-medium text-slate-700 mb-2">Lowest 10 answered questions (for this school)</p>
                      <Table>
                        <TableHeader>
                          <TableRow className="bg-slate-50">
                            <TableHead>Question</TableHead>
                            <TableHead className="text-right">Score</TableHead>
                            <TableHead className="text-right">Score %</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {(schoolDetail.lowest_10_questions || []).map((q, i) => (
                            <TableRow key={i}>
                              <TableCell className="font-mono text-xs">{q.question}</TableCell>
                              <TableCell className="text-right tabular-nums">{typeof q.score === "number" ? fmt2(q.score) : q.score}</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(q.score_pct)}%</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </div>
                  </CardContent>
                </Card>
              )}
                </div>
                )}

                {activeTab === "intervention" && (
                <div className="space-y-6">
              {intervention && (
                <>
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2 flex flex-row items-center justify-between">
                      <CardTitle className="text-lg">Critical Schools (Score ≤40)</CardTitle>
                      <Button variant="outline" size="sm" onClick={() => downloadCSV(intervention.critical_schools || [], "sqaaf_critical_schools.csv")}>
                        <Download className="w-4 h-4 mr-2" />
                        Download CSV
                      </Button>
                    </CardHeader>
                    <CardContent>
                      <div className="overflow-x-auto max-h-[300px] overflow-y-auto">
                        <Table>
                          <TableHeader>
                            <TableRow className="bg-slate-50">
                              <TableHead>School Code</TableHead>
                              <TableHead>School Name</TableHead>
                              <TableHead>Block</TableHead>
                              <TableHead className="text-right">Answered %</TableHead>
                              <TableHead className="text-right">SQAAF %</TableHead>
                            </TableRow>
                          </TableHeader>
                          <TableBody>
                            {(intervention.critical_schools || []).map((s, i) => (
                              <TableRow key={i}>
                                <TableCell className="font-mono">{s.school_code}</TableCell>
                                <TableCell className="max-w-[200px] truncate">{s.school_name}</TableCell>
                                <TableCell>{s.block}</TableCell>
                                <TableCell className="text-right tabular-nums">{fmt2(s["Answered_%"])}%</TableCell>
                                <TableCell className="text-right tabular-nums font-bold text-red-600">{fmt2(s["SQAAF_Score_%"])}</TableCell>
                              </TableRow>
                            ))}
                          </TableBody>
                        </Table>
                      </div>
                    </CardContent>
                  </Card>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <Card className="border-slate-200">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-lg">Bottom 10 Questions (Overall Mean)</CardTitle>
                        <CardDescription>Pareto: lowest-scoring questions across all schools.</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="h-[420px]">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={intervention.bottom_questions || []} layout="vertical" margin={{ left: 8 }}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                              <XAxis type="number" domain={[0, 100]} />
                              <YAxis
                                dataKey="question"
                                type="category"
                                width={260}
                                tick={{ fontSize: 11 }}
                                tickFormatter={(v) => truncateQuestion(v, 48)}
                                interval={0}
                              />
                              <Tooltip content={<BottomQuestionsTooltip />} cursor={{ fill: "rgba(0,0,0,0.04)" }} />
                              <Bar dataKey="mean_score_%" name="Mean %" fill="#ef4444" radius={[0, 4, 4, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                        <p className="text-xs text-slate-500 mt-2">Hover a bar to see the full question text.</p>
                      </CardContent>
                    </Card>
                    <Card className="border-slate-200">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-lg">Priority Domains (Bottom 5 Sections)</CardTitle>
                        <CardDescription>Focus improvement here first.</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {(intervention.priority_domains || []).map((d, i) => (
                            <li key={i} className="flex justify-between items-center">
                              <span className="font-medium">Section {d.section}</span>
                              <Badge variant="secondary">{fmt2(d.mean)}%</Badge>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  </div>
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Block Intervention Priority Index</CardTitle>
                      <CardDescription>0.6×(% schools &lt;60) + 0.4×(% critical). Higher = more intervention needed.</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={(intervention.block_intervention_index || []).sort((a, b) => b.intervention_index - a.intervention_index)}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis dataKey="block" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={60} />
                            <YAxis />
                            <Tooltip formatter={(v) => [fmt2(v), "Index"]} />
                            <Bar dataKey="intervention_index" name="Index" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                      <Table className="mt-4">
                        <TableHeader>
                          <TableRow className="bg-slate-50">
                            <TableHead>Block</TableHead>
                            <TableHead className="text-right">Index</TableHead>
                            <TableHead className="text-right">% Critical</TableHead>
                            <TableHead className="text-right">% &lt;60</TableHead>
                            <TableHead className="text-right">Schools</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {(intervention.block_intervention_index || []).sort((a, b) => b.intervention_index - a.intervention_index).map((b, i) => (
                            <TableRow key={i}>
                              <TableCell className="font-medium">{b.block}</TableCell>
                              <TableCell className="text-right tabular-nums font-medium">{fmt2(b.intervention_index)}</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(b.critical_pct)}%</TableCell>
                              <TableCell className="text-right tabular-nums">{fmt2(b.pct_below_60)}%</TableCell>
                              <TableCell className="text-right tabular-nums">{b.schools}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </>
              )}
                </div>
                )}
              </PageTransition>
            </div>
          </main>
        </div>
      )}
    </div>
  );
};

export default SqafDashboard;
