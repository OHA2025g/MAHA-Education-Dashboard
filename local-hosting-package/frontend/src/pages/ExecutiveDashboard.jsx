import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { useScope } from "@/context/ScopeContext";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { RefreshCw, Users, Building2, GraduationCap, Settings, Trophy, TrendingUp, ShieldCheck, CheckCircle2, AlertTriangle, BarChart3, MapPin, X, Search } from "lucide-react";
import { toast } from "sonner";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, LineChart, Line } from "recharts";
import ExportPanel from "@/components/ExportPanel";
import MaharashtraMap from "@/components/MaharashtraMap";
import { getBackendUrl } from "@/lib/backend";
import { BlockLink, DistrictLink, SchoolLink } from "@/components/DrilldownLink";
import { useNavigate } from "react-router-dom";

const BACKEND_URL = getBackendUrl();
const API = `${BACKEND_URL}/api`;

import MetricInfoButton from "@/components/MetricInfoButton";

const KPICard = ({ label, value, suffix = "", icon: Icon, color = "blue", description, size = "normal", metricKey = null, onClick = null }) => {
  const colors = { 
    blue: "bg-blue-50 text-blue-600 border-blue-200", 
    green: "bg-emerald-50 text-emerald-600 border-emerald-200", 
    red: "bg-red-50 text-red-600 border-red-200", 
    amber: "bg-amber-50 text-amber-600 border-amber-200", 
    purple: "bg-purple-50 text-purple-600 border-purple-200",
    cyan: "bg-cyan-50 text-cyan-600 border-cyan-200"
  };
  const isLarge = size === "large";
  return (
    <Card 
      className={`border-slate-200 ${isLarge ? 'col-span-2' : ''} ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`} 
      data-testid={`kpi-${label.toLowerCase().replace(/\s+/g, '-')}`}
      onClick={onClick}
    >
      <CardContent className={isLarge ? "p-6" : "p-4"}>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className={`flex items-center gap-2 ${isLarge ? 'text-sm' : 'text-xs'}`}>
              <p className={`font-medium text-slate-500 uppercase tracking-wider`}>{label}</p>
              {metricKey && (
                <MetricInfoButton 
                  metricKey={metricKey}
                  variant="ghost"
                  size="sm"
                />
              )}
            </div>
            <div className="flex items-baseline gap-1 mt-1">
              <span className={`font-bold text-slate-900 tabular-nums ${isLarge ? 'text-4xl' : 'text-2xl'}`} style={{ fontFamily: 'Manrope' }}>
                {typeof value === 'number' ? value.toLocaleString('en-IN') : value}
              </span>
              {suffix && <span className={`text-slate-500 ${isLarge ? 'text-xl' : 'text-lg'}`}>{suffix}</span>}
            </div>
            {description && <p className={`text-slate-400 mt-1 ${isLarge ? 'text-sm' : 'text-xs'}`}>{description}</p>}
          </div>
          {Icon && <div className={`rounded-lg border ${colors[color]} ${isLarge ? 'p-3' : 'p-2'}`}><Icon className={isLarge ? "w-6 h-6" : "w-5 h-5"} strokeWidth={1.5} /></div>}
        </div>
      </CardContent>
    </Card>
  );
};

const GaugeChart = ({ value, label, size = "normal", color, metricKey = null }) => {
  const getColor = (val) => val >= 85 ? "#10b981" : val >= 70 ? "#f59e0b" : "#ef4444";
  const actualColor = color || getColor(value);
  const isLarge = size === "large";
  const radius = isLarge ? 55 : 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDasharray = `${(value / 100) * circumference} ${circumference}`;
  const svgSize = isLarge ? 140 : 112;
  const center = svgSize / 2;
  
  return (
    <div className="flex flex-col items-center relative">
      {metricKey && (
        <div className="absolute -top-2 -right-2 z-10">
          <MetricInfoButton 
            metricKey={metricKey}
            variant="outline"
            size="sm"
            className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm shadow-sm"
          />
        </div>
      )}
      <div className={`relative ${isLarge ? 'w-36 h-36' : 'w-28 h-28'}`}>
        <svg className="w-full h-full transform -rotate-90">
          <circle cx={center} cy={center} r={radius} stroke="#e2e8f0" strokeWidth={isLarge ? 12 : 10} fill="none" />
          <circle cx={center} cy={center} r={radius} stroke={actualColor} strokeWidth={isLarge ? 12 : 10} fill="none" strokeDasharray={strokeDasharray} strokeLinecap="round" />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className={`font-bold ${isLarge ? 'text-2xl' : 'text-xl'}`} style={{ color: actualColor }}>{value}%</span>
        </div>
      </div>
      <p className={`text-slate-600 mt-2 text-center max-w-[120px] ${isLarge ? 'text-base font-medium' : 'text-sm'}`}>{label}</p>
    </div>
  );
};

const DomainCard = ({ title, icon: Icon, index, metrics, color, onClick, metricKey = null }) => {
  const getRAGColor = (val) => val >= 85 ? "bg-emerald-500" : val >= 70 ? "bg-amber-500" : "bg-red-500";
  return (
    <Card className="border-slate-200 hover:shadow-md transition-shadow cursor-pointer relative" onClick={onClick}>
      {metricKey && (
        <div className="absolute top-3 right-3 z-10" onClick={(e) => e.stopPropagation()}>
          <MetricInfoButton 
            metricKey={metricKey}
            variant="ghost"
            size="sm"
          />
        </div>
      )}
      <CardContent className="p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${color}`}><Icon className="w-5 h-5" /></div>
            <h3 className="font-semibold text-slate-800">{title}</h3>
          </div>
          <div className={`w-3 h-3 rounded-full ${getRAGColor(index)}`} title={`Score: ${index}`} />
        </div>
        <div className="flex items-end justify-between">
          <div>
            <p className="text-4xl font-bold text-slate-900" style={{ fontFamily: 'Manrope' }}>{index}</p>
            <p className="text-xs text-slate-500 mt-1">Domain Index</p>
          </div>
          <div className="text-right space-y-1">
            {metrics.map((m, i) => (
              <p key={i} className="text-xs text-slate-600"><span className="font-medium">{m.label}:</span> {m.value}</p>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

const ExecutiveDashboard = () => {
  const { scope } = useScope();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [overview, setOverview] = useState(null);
  const [identity, setIdentity] = useState(null);
  const [infrastructure, setInfrastructure] = useState(null);
  const [teacher, setTeacher] = useState(null);
  const [operational, setOperational] = useState(null);
  const [shi, setShi] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [schoolModalOpen, setSchoolModalOpen] = useState(false);
  const [schoolModalData, setSchoolModalData] = useState(null);
  const [schoolModalLoading, setSchoolModalLoading] = useState(false);
  const [schoolFilters, setSchoolFilters] = useState({
    schoolName: "",
    blockName: "",
    udiseCode: "",
    studentsMin: "",
    studentsMax: "",
    teachers: ""
  });

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      // Build scope parameters - the axios interceptor will merge them with localStorage values
      // Also pass district_name, block_name, school_name to help with matching
      const requestParams = {};
      if (scope.districtCode && scope.districtCode.trim()) {
        requestParams.district_code = scope.districtCode.trim();
      }
      if (scope.districtName && scope.districtName.trim()) {
        requestParams.district_name = scope.districtName.trim();
      }
      if (scope.blockCode && scope.blockCode.trim()) {
        requestParams.block_code = scope.blockCode.trim();
      }
      if (scope.blockName && scope.blockName.trim()) {
        requestParams.block_name = scope.blockName.trim();
      }
      if (scope.udiseCode && scope.udiseCode.trim()) {
        requestParams.udise_code = scope.udiseCode.trim();
      }
      if (scope.schoolName && scope.schoolName.trim()) {
        requestParams.school_name = scope.schoolName.trim();
      }

      const [overviewRes, identityRes, infraRes, teacherRes, opsRes, shiRes, mapRes] = await Promise.all([
        axios.get(`${API}/executive/overview`, { params: requestParams }),
        axios.get(`${API}/executive/student-identity`, { params: requestParams }),
        axios.get(`${API}/executive/infrastructure-facilities`, { params: requestParams }),
        axios.get(`${API}/executive/teacher-staffing`, { params: requestParams }),
        axios.get(`${API}/executive/operational-performance`, { params: requestParams }),
        axios.get(`${API}/executive/school-health-index`, { params: requestParams }),
        axios.get(`${API}/executive/district-map-data`, { params: requestParams })
      ]);
      setOverview(overviewRes.data);
      setIdentity(identityRes.data);
      setInfrastructure(infraRes.data);
      setTeacher(teacherRes.data);
      setOperational(opsRes.data);
      setShi(shiRes.data);
      setMapData(mapRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      console.error("Error details:", error.response?.data || error.message);
      toast.error("Failed to load executive dashboard");
    } finally {
      setLoading(false);
    }
  }, [scope.version, scope.districtCode, scope.districtName, scope.blockCode, scope.blockName, scope.udiseCode, scope.schoolName]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSchoolCountClick = async (teacherCount) => {
    setSchoolModalOpen(true);
    setSchoolModalLoading(true);
    setSchoolModalData(null);
    // Reset filters when opening modal
    setSchoolFilters({
      schoolName: "",
      blockName: "",
      udiseCode: "",
      studentsMin: "",
      studentsMax: "",
      teachers: ""
    });
    
    try {
      const params = new URLSearchParams();
      if (scope.district_code) params.append('district_code', scope.district_code);
      if (scope.block_code) params.append('block_code', scope.block_code);
      if (scope.udise_code) params.append('udise_code', scope.udise_code);
      params.append('teacher_count', teacherCount);
      params.append('limit', '500');
      
      const response = await axios.get(`${API}/executive/schools-by-teacher-count?${params.toString()}`);
      setSchoolModalData(response.data);
    } catch (error) {
      console.error("Error fetching schools:", error);
      toast.error("Failed to load school list");
      setSchoolModalOpen(false);
    } finally {
      setSchoolModalLoading(false);
    }
  };

  // Filter schools based on filter values
  const getFilteredSchools = () => {
    if (!schoolModalData?.schools) return [];
    
    return schoolModalData.schools.filter(school => {
      // School Name filter
      if (schoolFilters.schoolName && !school.school_name?.toLowerCase().includes(schoolFilters.schoolName.toLowerCase())) {
        return false;
      }
      
      // Block Name filter
      if (schoolFilters.blockName && !school.block_name?.toLowerCase().includes(schoolFilters.blockName.toLowerCase())) {
        return false;
      }
      
      // UDISE Code filter
      if (schoolFilters.udiseCode && !school.udise_code?.includes(schoolFilters.udiseCode)) {
        return false;
      }
      
      // Students Min filter
      if (schoolFilters.studentsMin) {
        const min = parseInt(schoolFilters.studentsMin);
        if (isNaN(min) || (school.student_count || 0) < min) {
          return false;
        }
      }
      
      // Students Max filter
      if (schoolFilters.studentsMax) {
        const max = parseInt(schoolFilters.studentsMax);
        if (isNaN(max) || (school.student_count || 0) > max) {
          return false;
        }
      }
      
      // Teachers filter (exact match)
      if (schoolFilters.teachers && school.teacher_count !== parseInt(schoolFilters.teachers)) {
        return false;
      }
      
      return true;
    });
  };

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-slate-900 text-white p-3 rounded-lg shadow-lg">
          <p className="font-medium">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>{entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}</p>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading) return <div className="flex items-center justify-center h-96"><div className="loading-spinner" /></div>;
  if (!shi || !identity) return <div className="text-center py-12"><p className="text-slate-500">No data available. Please import data first.</p></div>;

  return (
    <div className="space-y-6 animate-fade-in" data-testid="executive-dashboard">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight" style={{ fontFamily: 'Manrope' }}>Executive Dashboard</h1>
          <p className="text-slate-500 mt-1">Holistic KPIs & School Health Index • Pune District • 2025-26</p>
        </div>
        <div className="flex gap-2">
          <ExportPanel dashboardName="executive-summary" dashboardTitle="Executive Summary" />
          <Button variant="outline" size="sm" onClick={fetchData} data-testid="refresh-btn"><RefreshCw className="w-4 h-4 mr-2" />Refresh</Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="bg-slate-100 flex-wrap h-auto gap-1 p-1">
          <TabsTrigger value="overview" data-testid="tab-overview"><BarChart3 className="w-4 h-4 mr-2" />Overview</TabsTrigger>
          <TabsTrigger value="map" data-testid="tab-map"><MapPin className="w-4 h-4 mr-2" />Map View</TabsTrigger>
          <TabsTrigger value="identity" data-testid="tab-identity"><ShieldCheck className="w-4 h-4 mr-2" />Student Identity</TabsTrigger>
          <TabsTrigger value="infrastructure" data-testid="tab-infrastructure"><Building2 className="w-4 h-4 mr-2" />Infrastructure</TabsTrigger>
          <TabsTrigger value="teacher" data-testid="tab-teacher"><GraduationCap className="w-4 h-4 mr-2" />Teacher & Staffing</TabsTrigger>
          <TabsTrigger value="operational" data-testid="tab-operational"><Settings className="w-4 h-4 mr-2" />Operational</TabsTrigger>
          <TabsTrigger value="shi" data-testid="tab-shi"><Trophy className="w-4 h-4 mr-2" />School Health Index</TabsTrigger>
        </TabsList>

        {/* EXECUTIVE OVERVIEW */}
        <TabsContent value="overview" className="space-y-6">
          {/* SHI Hero Card */}
          <Card className="border-slate-200 bg-gradient-to-r from-slate-50 to-white">
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row items-center justify-between gap-6">
                <div className="flex items-center gap-6">
                  <div className="relative">
                    <GaugeChart 
                      value={shi.summary.school_health_index} 
                      label="" 
                      size="large" 
                      color={shi.summary.rag_status.color}
                      metricKey="school_health_index"
                    />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-2xl font-bold text-slate-900">School Health Index</h2>
                      <MetricInfoButton 
                        metricKey="school_health_index"
                        variant="ghost"
                        size="sm"
                      />
                    </div>
                    <p className="text-slate-500">Composite score across all domains</p>
                    <Badge className={`mt-2 ${shi.summary.rag_status.status === 'Green' ? 'bg-emerald-100 text-emerald-700' : shi.summary.rag_status.status === 'Amber' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>
                      {shi.summary.rag_status.status} Status
                    </Badge>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-3 bg-white rounded-lg border">
                    <p className="text-2xl font-bold text-slate-900">{overview?.quick_stats?.total_schools?.toLocaleString()}</p>
                    <p className="text-xs text-slate-500">Schools</p>
                  </div>
                  <div className="text-center p-3 bg-white rounded-lg border">
                    <p className="text-2xl font-bold text-slate-900">{(overview?.quick_stats?.total_students / 100000).toFixed(1)}L</p>
                    <p className="text-xs text-slate-500">Students</p>
                  </div>
                  <div className="text-center p-3 bg-white rounded-lg border">
                    <p className="text-2xl font-bold text-slate-900">{overview?.quick_stats?.total_teachers?.toLocaleString()}</p>
                    <p className="text-xs text-slate-500">Teachers</p>
                  </div>
                  <div className="text-center p-3 bg-white rounded-lg border">
                    <p className="text-2xl font-bold text-slate-900">{overview?.quick_stats?.total_classrooms?.toLocaleString()}</p>
                    <p className="text-xs text-slate-500">Classrooms</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Domain Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <DomainCard 
              title="Student Identity" 
              icon={ShieldCheck} 
              index={overview?.domain_summary?.identity?.index || 0}
              metrics={[
                {label: "Aadhaar", value: `${overview?.domain_summary?.identity?.aadhaar_pct}%`},
                {label: "APAAR", value: `${overview?.domain_summary?.identity?.apaar_pct}%`}
              ]}
              color="bg-blue-50 text-blue-600"
              onClick={() => setActiveTab("identity")}
              metricKey="student_identity_domain_index"
            />
            <DomainCard 
              title="Infrastructure" 
              icon={Building2} 
              index={overview?.domain_summary?.infrastructure?.index || 0}
              metrics={[
                {label: "Classroom", value: `${overview?.domain_summary?.infrastructure?.classroom_health}%`},
                {label: "Toilet", value: `${overview?.domain_summary?.infrastructure?.toilet_functional}%`}
              ]}
              color="bg-emerald-50 text-emerald-600"
              onClick={() => setActiveTab("infrastructure")}
              metricKey="infrastructure_domain_index"
            />
            <DomainCard 
              title="Teacher Quality" 
              icon={GraduationCap} 
              index={overview?.domain_summary?.teacher?.index || 0}
              metrics={[
                {label: "Teachers", value: overview?.domain_summary?.teacher?.total_teachers?.toLocaleString()},
                {label: "CTET", value: `${overview?.domain_summary?.teacher?.ctet_pct}%`}
              ]}
              color="bg-purple-50 text-purple-600"
              onClick={() => setActiveTab("teacher")}
              metricKey="teacher_quality_domain_index"
            />
            <DomainCard 
              title="Operational" 
              icon={Settings} 
              index={overview?.domain_summary?.operational?.index || 0}
              metrics={[
                {label: "Completion", value: `${overview?.domain_summary?.operational?.completion_rate}%`},
                {label: "Certified", value: `${overview?.domain_summary?.operational?.certification_rate}%`}
              ]}
              color="bg-amber-50 text-amber-600"
              onClick={() => setActiveTab("operational")}
              metricKey="operational_domain_index"
            />
          </div>

          {/* SHI Breakdown Chart */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">SHI Domain Contribution</CardTitle></CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={shi.shi_breakdown} layout="vertical" margin={{ left: 100 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis type="number" domain={[0, 30]} />
                      <YAxis dataKey="domain" type="category" tick={{ fontSize: 12 }} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="contribution" name="Contribution" radius={[0, 4, 4, 0]}>
                        {shi.shi_breakdown.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Domain Performance Radar</CardTitle></CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={[
                      { domain: "Identity", score: overview?.domain_summary?.identity?.index || 0 },
                      { domain: "Infrastructure", score: overview?.domain_summary?.infrastructure?.index || 0 },
                      { domain: "Teacher", score: overview?.domain_summary?.teacher?.index || 0 },
                      { domain: "Operational", score: overview?.domain_summary?.operational?.index || 0 }
                    ]}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="domain" tick={{ fontSize: 11 }} />
                      <PolarRadiusAxis angle={30} domain={[0, 100]} />
                      <Radar name="Score" dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.5} />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Block Rankings */}
          <Card className="border-slate-200">
            <CardHeader className="pb-2"><CardTitle className="text-lg">Block-wise SHI Rankings</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50">
                      <TableHead>Rank</TableHead>
                      <TableHead>Block</TableHead>
                      <TableHead className="text-right">SHI Score</TableHead>
                      <TableHead className="text-right">Identity</TableHead>
                      <TableHead className="text-right">Infrastructure</TableHead>
                      <TableHead className="text-right">Teacher</TableHead>
                      <TableHead className="text-right">Operational</TableHead>
                      <TableHead className="text-center">Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {shi.block_rankings?.slice(0, 10).map((block) => (
                      <TableRow key={block.block_name}>
                        <TableCell className="font-medium">{block.rank}</TableCell>
                        <TableCell className="font-medium">
                          <BlockLink blockCode={block.block_code}>{block.block_name}</BlockLink>
                        </TableCell>
                        <TableCell className="text-right"><span className="text-lg font-bold">{block.shi_score}</span></TableCell>
                        <TableCell className="text-right">{block.identity_score}</TableCell>
                        <TableCell className="text-right">{block.infra_score}</TableCell>
                        <TableCell className="text-right">{block.teacher_score}</TableCell>
                        <TableCell className="text-right">{block.ops_score}</TableCell>
                        <TableCell className="text-center">
                          <Badge className={block.rag.status === 'Green' ? 'bg-emerald-100 text-emerald-700' : block.rag.status === 'Amber' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}>
                            {block.rag.status}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* MAP VIEW */}
        <TabsContent value="map" className="space-y-6">
          <MaharashtraMap 
            data={mapData} 
            onDistrictClick={(district) => {
              if (district?.district_code) {
                navigate(`/district/${district.district_code}`);
                return;
              }
              toast.info(`Selected: ${district.district_name}`, {
                description: `Schools: ${district.total_schools?.toLocaleString()} | Students: ${district.total_students?.toLocaleString()}`
              });
            }}
          />
          
          {/* District Summary Table */}
          {mapData?.districts && (
            <Card className="border-slate-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">District-wise Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow className="bg-slate-50">
                        <TableHead>District</TableHead>
                        <TableHead className="text-right">Schools</TableHead>
                        <TableHead className="text-right">Students</TableHead>
                        <TableHead className="text-right">Teachers</TableHead>
                        <TableHead className="text-right">SHI</TableHead>
                        <TableHead className="text-right">Aadhaar %</TableHead>
                        <TableHead className="text-right">APAAR %</TableHead>
                        <TableHead className="text-right">Infra Index</TableHead>
                        <TableHead className="text-center">Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {mapData.districts.filter(d => d.has_data).map((district) => (
                        <TableRow key={district.district_name}>
                          <TableCell className="font-medium">
                            <DistrictLink districtCode={district.district_code}>{district.district_name}</DistrictLink>
                          </TableCell>
                          <TableCell className="text-right">{district.total_schools?.toLocaleString()}</TableCell>
                          <TableCell className="text-right">{district.total_students?.toLocaleString()}</TableCell>
                          <TableCell className="text-right">{district.total_teachers?.toLocaleString()}</TableCell>
                          <TableCell className="text-right font-bold">{district.metrics.shi || 'N/A'}</TableCell>
                          <TableCell className="text-right">{district.metrics.aadhaar_coverage || 'N/A'}%</TableCell>
                          <TableCell className="text-right">{district.metrics.apaar_coverage || 'N/A'}%</TableCell>
                          <TableCell className="text-right">{district.metrics.infrastructure_index || 'N/A'}%</TableCell>
                          <TableCell className="text-center">
                            <Badge className={district.metrics.shi >= 70 ? 'bg-emerald-100 text-emerald-700' : district.metrics.shi >= 50 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-700'}>
                              {district.metrics.shi >= 70 ? 'Good' : district.metrics.shi >= 50 ? 'Average' : 'Data Available'}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                      {mapData.districts.filter(d => !d.has_data).slice(0, 5).map((district) => (
                        <TableRow key={district.district_name} className="text-slate-400">
                          <TableCell className="font-medium">{district.district_name}</TableCell>
                          <TableCell className="text-right">-</TableCell>
                          <TableCell className="text-right">-</TableCell>
                          <TableCell className="text-right">-</TableCell>
                          <TableCell className="text-right">-</TableCell>
                          <TableCell className="text-right">-</TableCell>
                          <TableCell className="text-right">-</TableCell>
                          <TableCell className="text-right">-</TableCell>
                          <TableCell className="text-center">
                            <Badge variant="outline" className="text-slate-400">No Data</Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
                {mapData.summary?.districts_no_data > 5 && (
                  <p className="text-sm text-slate-400 mt-2 text-center">
                    + {mapData.summary.districts_no_data - 5} more districts without data
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* STUDENT IDENTITY TAB */}
        <TabsContent value="identity" className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <KPICard label="Total Students" value={(identity.summary.total_students / 100000).toFixed(1)} suffix="L" icon={Users} color="blue" />
            <KPICard label="Aadhaar Coverage" value={identity.aadhaar_metrics.aadhaar_coverage_pct} suffix="%" icon={ShieldCheck} color="green" />
            <KPICard label="APAAR Coverage" value={identity.apaar_metrics.apaar_coverage_pct} suffix="%" icon={CheckCircle2} color="purple" />
            <KPICard label="Name Mismatch" value={identity.aadhaar_metrics.name_mismatch_rate} suffix="%" icon={AlertTriangle} color="amber" />
            <KPICard label="Identity Index" value={identity.summary.identity_compliance_index} icon={Trophy} color="cyan" size="normal" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Compliance Metrics</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap justify-around gap-4 py-4">
                  {identity.compliance_breakdown.map((item, idx) => (
                    <GaugeChart key={idx} value={item.value} label={item.metric} color={item.color} />
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Block-wise Aadhaar Coverage</CardTitle></CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[...identity.block_performance].sort((a, b) => b.aadhaar_pct - a.aadhaar_pct).slice(0, 10)} layout="vertical" margin={{ left: 80 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis type="number" domain={[0, 100]} />
                      <YAxis dataKey="block_name" type="category" tick={{ fontSize: 11 }} />
                      <Tooltip content={<CustomTooltip />} />
                      <Bar dataKey="aadhaar_pct" name="Aadhaar %" fill="#3b82f6" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* INFRASTRUCTURE TAB */}
        <TabsContent value="infrastructure" className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <KPICard label="Total Classrooms" value={infrastructure.classroom_metrics.total_classrooms} icon={Building2} color="blue" />
            <KPICard label="Classroom Health" value={infrastructure.classroom_metrics.classroom_health_pct} suffix="%" icon={CheckCircle2} color="green" />
            <KPICard label="Toilet Functional" value={infrastructure.toilet_metrics.functional_pct} suffix="%" icon={CheckCircle2} color="cyan" />
            <KPICard label="Water Coverage" value={infrastructure.toilet_metrics.water_coverage_pct} suffix="%" icon={TrendingUp} color="purple" />
            <KPICard label="Infra Index" value={infrastructure.summary.infrastructure_index} icon={Trophy} color="amber" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Infrastructure Index Breakdown</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap justify-around gap-4 py-4">
                  {infrastructure.index_breakdown.map((item, idx) => (
                    <GaugeChart key={idx} value={item.value} label={`${item.metric} (${item.weight}%)`} color={item.color} />
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Water Safety Metrics</CardTitle></CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={[
                      { metric: "Tap Water", value: infrastructure?.water_safety?.tap_water_pct || 0 },
                      { metric: "Purified", value: infrastructure?.water_safety?.purified_water_pct || 0 },
                      { metric: "Tested", value: infrastructure?.water_safety?.water_tested_pct || 0 },
                      { metric: "Rainwater", value: infrastructure?.water_safety?.rainwater_harvest_pct || 0 }
                    ]}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                      <XAxis dataKey="metric" />
                      <YAxis domain={[0, 100]} />
                      <Tooltip 
                        content={<CustomTooltip />}
                        formatter={(value) => [`${value}%`, "Coverage %"]}
                      />
                      <Bar dataKey="value" name="Coverage %" radius={[4, 4, 0, 0]}>
                        {[
                          { metric: "Tap Water", value: infrastructure?.water_safety?.tap_water_pct || 0 },
                          { metric: "Purified", value: infrastructure?.water_safety?.purified_water_pct || 0 },
                          { metric: "Tested", value: infrastructure?.water_safety?.water_tested_pct || 0 },
                          { metric: "Rainwater", value: infrastructure?.water_safety?.rainwater_harvest_pct || 0 }
                        ].map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.value > 0 ? "#06b6d4" : "#e2e8f0"} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* TEACHER TAB */}
        <TabsContent value="teacher" className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <KPICard label="Total Teachers" value={teacher.summary.total_teachers} icon={GraduationCap} color="blue" />
            <KPICard 
              label="Zero Teacher Schools" 
              value={teacher.school_teacher_distribution?.zero_teacher_schools || 0} 
              icon={Building2} 
              color="red"
              onClick={() => handleSchoolCountClick(0)}
            />
            <KPICard 
              label="One Teacher Schools" 
              value={teacher.school_teacher_distribution?.one_teacher_schools || 0} 
              icon={Building2} 
              color="amber"
              onClick={() => handleSchoolCountClick(1)}
            />
            <KPICard 
              label="Two Teacher Schools" 
              value={teacher.school_teacher_distribution?.two_teacher_schools || 0} 
              icon={Building2} 
              color="cyan"
              onClick={() => handleSchoolCountClick(2)}
            />
            <KPICard label="Quality Index" value={teacher.summary.teacher_quality_index} icon={Trophy} color="amber" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Teacher Quality Breakdown</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap justify-around gap-4 py-4">
                  {teacher.quality_breakdown.map((item, idx) => (
                    <GaugeChart key={idx} value={item.value} label={item.metric} color={item.color} metricKey={item.metricKey} />
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Risk Metrics</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 py-4">
                  <div className="text-center p-4 bg-amber-50 rounded-lg relative">
                    <div className="absolute top-2 right-2">
                      <MetricInfoButton metricKey="retirement_risk" />
                    </div>
                    <p className="text-3xl font-bold text-amber-600">{teacher.risk_metrics.retirement_risk_pct}%</p>
                    <p className="text-sm text-slate-500">Retirement Risk</p>
                    <p className="text-xs text-slate-400">{teacher.risk_metrics.retirement_risk_count} teachers</p>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-3xl font-bold text-blue-600">{teacher.demographic_metrics.avg_service_years}</p>
                    <p className="text-sm text-slate-500">Avg Service Years</p>
                  </div>
                  <div className="text-center p-4 bg-emerald-50 rounded-lg">
                    <p className="text-3xl font-bold text-emerald-600">{teacher.risk_metrics.growth_rate}%</p>
                    <p className="text-sm text-slate-500">YoY Growth</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-3xl font-bold text-purple-600">{teacher.demographic_metrics.gender_parity_index}</p>
                    <p className="text-sm text-slate-500">Gender Parity</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Qualification Metrics Section */}
          {teacher.qualification_metrics && (() => {
            // Helper function to shorten qualification names
            const shortenQualification = (name) => {
              if (!name) return "";
              const str = String(name);
              
              // Professional qualifications
              if (str.includes("B.Ed") && str.includes("equivalent")) return "B.Ed or equivalent";
              if (str.includes("M.Ed") && str.includes("equivalent")) return "M.Ed or equivalent";
              if (str.includes("Diploma") && str.includes("basic teacher")) return "Basic Teacher Diploma";
              if (str.includes("D.El.Ed")) return "D.El.Ed";
              if (str.includes("B.El.Ed")) return "B.El.Ed";
              if (str.includes("None")) return "None/Untrained";
              if (str.includes("special education")) return "Special Education";
              if (str.includes("Pursuing")) return "Pursuing Course";
              if (str.includes("Nursery") || str.includes("Pre-school")) return "Nursery Teacher Ed";
              if (str.includes("Others")) return "Others";
              
              // Academic qualifications
              if (str.includes("Post graduate")) return "Post Graduate";
              if (str.includes("Graduate") && !str.includes("Post")) return "Graduate";
              if (str.includes("Higher Secondary")) return "Higher Secondary";
              if (str.includes("Secondary") && !str.includes("Higher")) return "Secondary";
              if (str.includes("M.Phil")) return "M.Phil";
              if (str.includes("Ph.D")) return "Ph.D";
              if (str.includes("Post Doctoral")) return "Post Doctoral";
              if (str.includes("Below secondary")) return "Below Secondary";
              
              // Fallback: take first part before dash or limit length
              if (str.includes(" - ")) return str.split(" - ")[1]?.substring(0, 30) || str.substring(0, 30);
              if (str.includes("-")) return str.split("-")[1]?.trim().substring(0, 30) || str.substring(0, 30);
              return str.length > 30 ? str.substring(0, 30) + "..." : str;
            };

            // Process data with shortened labels
            const profData = (teacher.qualification_metrics.professional_qualification_distribution || [])
              .slice(0, 8)
              .map(item => ({
                ...item,
                shortLabel: shortenQualification(item.qualification),
                fullLabel: item.qualification
              }));

            const acadData = (teacher.qualification_metrics.academic_qualification_distribution || [])
              .slice(0, 8)
              .map(item => ({
                ...item,
                shortLabel: shortenQualification(item.qualification),
                fullLabel: item.qualification
              }));

            return (
              <div className="space-y-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <KPICard 
                    label="B.Ed or Higher" 
                    value={teacher.qualification_metrics.b_ed_or_higher_pct} 
                    suffix="%" 
                    icon={GraduationCap} 
                    color="green" 
                  />
                  <KPICard 
                    label="Post Graduate" 
                    value={teacher.qualification_metrics.post_graduate_pct} 
                    suffix="%" 
                    icon={GraduationCap} 
                    color="purple" 
                  />
                  <KPICard 
                    label="Top Prof. Qual." 
                    value={teacher.qualification_metrics.top_professional_qualification?.percentage || 0} 
                    suffix="%" 
                    icon={CheckCircle2} 
                    color="blue" 
                  />
                  <KPICard 
                    label="Top Acad. Qual." 
                    value={teacher.qualification_metrics.top_academic_qualification?.percentage || 0} 
                    suffix="%" 
                    icon={CheckCircle2} 
                    color="cyan" 
                  />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="border-slate-200">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Professional Qualification Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-96">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart 
                            data={profData}
                            layout="vertical"
                            margin={{ left: 90, right: 30, top: 10, bottom: 10 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis 
                              type="number" 
                              domain={[0, 100]} 
                              tick={{ fontSize: 11 }}
                              label={{ value: 'Percentage (%)', position: 'insideBottom', offset: -5, style: { fontSize: 12 } }}
                            />
                            <YAxis 
                              dataKey="shortLabel" 
                              type="category" 
                              tick={{ fontSize: 11, width: 85 }}
                              width={85}
                              interval={0}
                            />
                            <Tooltip 
                              content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  const data = payload[0].payload;
                                  return (
                                    <div className="bg-white dark:bg-slate-800 p-3 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg">
                                      <p className="font-semibold text-sm mb-1">{data.fullLabel}</p>
                                      <p className="text-sm text-slate-600 dark:text-slate-400">
                                        <span className="font-medium">{data.percentage}%</span> ({data.count.toLocaleString()} teachers)
                                      </p>
                                    </div>
                                  );
                                }
                                return null;
                              }}
                            />
                            <Bar dataKey="percentage" name="Percentage" radius={[0, 4, 4, 0]}>
                              {profData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.percentage >= 30 ? "#10b981" : entry.percentage >= 10 ? "#3b82f6" : "#f59e0b"} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="border-slate-200">
                    <CardHeader className="pb-2">
                      <CardTitle className="text-lg">Academic Qualification Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="h-96">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart 
                            data={acadData}
                            layout="vertical"
                            margin={{ left: 90, right: 30, top: 10, bottom: 10 }}
                          >
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis 
                              type="number" 
                              domain={[0, 100]} 
                              tick={{ fontSize: 11 }}
                              label={{ value: 'Percentage (%)', position: 'insideBottom', offset: -5, style: { fontSize: 12 } }}
                            />
                            <YAxis 
                              dataKey="shortLabel" 
                              type="category" 
                              tick={{ fontSize: 11, width: 85 }}
                              width={85}
                              interval={0}
                            />
                            <Tooltip 
                              content={({ active, payload }) => {
                                if (active && payload && payload.length) {
                                  const data = payload[0].payload;
                                  return (
                                    <div className="bg-white dark:bg-slate-800 p-3 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg">
                                      <p className="font-semibold text-sm mb-1">{data.fullLabel}</p>
                                      <p className="text-sm text-slate-600 dark:text-slate-400">
                                        <span className="font-medium">{data.percentage}%</span> ({data.count.toLocaleString()} teachers)
                                      </p>
                                    </div>
                                  );
                                }
                                return null;
                              }}
                            />
                            <Bar dataKey="percentage" name="Percentage" radius={[0, 4, 4, 0]}>
                              {acadData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.percentage >= 40 ? "#8b5cf6" : entry.percentage >= 20 ? "#3b82f6" : "#f59e0b"} />
                              ))}
                            </Bar>
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            );
          })()}
        </TabsContent>

        {/* OPERATIONAL TAB */}
        <TabsContent value="operational" className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            <KPICard label="Total Students" value={(operational.summary.total_students / 100000).toFixed(1)} suffix="L" icon={Users} color="blue" />
            <KPICard label="Completion Rate" value={operational.data_entry_metrics.completion_rate} suffix="%" icon={CheckCircle2} color="green" />
            <KPICard label="Certification" value={operational.data_entry_metrics.certification_rate} suffix="%" icon={ShieldCheck} color="purple" />
            <KPICard label="Data Accuracy" value={operational.dropbox_metrics.data_accuracy} suffix="%" icon={TrendingUp} color="cyan" />
            <KPICard label="Ops Index" value={operational.summary.operational_index} icon={Trophy} color="amber" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Operational Index Breakdown</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap justify-around gap-4 py-4">
                  {operational.index_breakdown.map((item, idx) => (
                    <GaugeChart key={idx} value={item.value} label={item.metric} color={item.color} />
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="border-slate-200">
              <CardHeader className="pb-2"><CardTitle className="text-lg">Enrolment & Gender</CardTitle></CardHeader>
              <CardContent>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie 
                        data={[
                          { name: "Girls", value: operational.enrolment_metrics.girls_enrolment, color: "#ec4899" },
                          { name: "Boys", value: operational.enrolment_metrics.boys_enrolment, color: "#3b82f6" }
                        ]} 
                        dataKey="value" 
                        nameKey="name" 
                        cx="50%" 
                        cy="50%" 
                        outerRadius={80}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        <Cell fill="#ec4899" />
                        <Cell fill="#3b82f6" />
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* SHI TAB */}
        <TabsContent value="shi" className="space-y-6">
          <Card className="border-slate-200 bg-gradient-to-r from-emerald-50 to-white">
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                <div className="flex items-center gap-8">
                  <GaugeChart value={shi.summary.school_health_index} label="" size="large" color={shi.summary.rag_status.color} />
                  <div>
                    <h2 className="text-3xl font-bold text-slate-900">School Health Index</h2>
                    <p className="text-slate-500 mt-1">Composite measure of school ecosystem health</p>
                    <div className="flex gap-4 mt-4">
                      <Badge className={shi.summary.rag_status.status === 'Green' ? 'bg-emerald-100 text-emerald-700' : shi.summary.rag_status.status === 'Amber' ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}>
                        {shi.summary.rag_status.status}
                      </Badge>
                      <span className="text-slate-500">{shi.summary.total_schools?.toLocaleString()} Schools | {(shi.summary.total_students / 100000).toFixed(1)}L Students</span>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-emerald-100 rounded-lg">
                    <p className="text-2xl font-bold text-emerald-700">{shi.rag_distribution?.green || 0}</p>
                    <p className="text-xs text-emerald-600">Green Blocks</p>
                  </div>
                  <div className="text-center p-3 bg-amber-100 rounded-lg">
                    <p className="text-2xl font-bold text-amber-700">{shi.rag_distribution?.amber || 0}</p>
                    <p className="text-xs text-amber-600">Amber Blocks</p>
                  </div>
                  <div className="text-center p-3 bg-red-100 rounded-lg">
                    <p className="text-2xl font-bold text-red-700">{shi.rag_distribution?.red || 0}</p>
                    <p className="text-xs text-red-600">Red Blocks</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(shi.domain_scores).map(([key, domain]) => (
              <Card key={key} className={`border-l-4 ${domain.rag.status === 'Green' ? 'border-l-emerald-500' : domain.rag.status === 'Amber' ? 'border-l-amber-500' : 'border-l-red-500'}`}>
                <CardContent className="p-4">
                  <p className="text-xs text-slate-500 uppercase">{key.replace('_', ' ')}</p>
                  <p className="text-3xl font-bold mt-1" style={{ color: domain.rag.color }}>{domain.score}</p>
                  <p className="text-xs text-slate-400">Weight: {domain.weight}%</p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card className="border-slate-200">
            <CardHeader className="pb-2"><CardTitle className="text-lg">Complete Block Rankings by SHI</CardTitle></CardHeader>
            <CardContent>
              <div className="overflow-x-auto max-h-96 overflow-y-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="bg-slate-50 sticky top-0">
                      <TableHead>Rank</TableHead>
                      <TableHead>Block</TableHead>
                      <TableHead className="text-right">SHI</TableHead>
                      <TableHead className="text-right">Identity</TableHead>
                      <TableHead className="text-right">Infra</TableHead>
                      <TableHead className="text-right">Teacher</TableHead>
                      <TableHead className="text-right">Ops</TableHead>
                      <TableHead className="text-center">RAG</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {shi.block_rankings?.map((block) => (
                      <TableRow key={block.block_name}>
                        <TableCell>{block.rank}</TableCell>
                        <TableCell className="font-medium">
                          <BlockLink blockCode={block.block_code}>{block.block_name}</BlockLink>
                        </TableCell>
                        <TableCell className="text-right font-bold">{block.shi_score}</TableCell>
                        <TableCell className="text-right">{block.identity_score}</TableCell>
                        <TableCell className="text-right">{block.infra_score}</TableCell>
                        <TableCell className="text-right">{block.teacher_score}</TableCell>
                        <TableCell className="text-right">{block.ops_score}</TableCell>
                        <TableCell className="text-center">
                          <div className={`w-4 h-4 rounded-full mx-auto`} style={{ backgroundColor: block.rag.color }} />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* School List Modal */}
      <Dialog open={schoolModalOpen} onOpenChange={setSchoolModalOpen}>
        <DialogContent className="max-w-4xl max-h-[85vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle className="text-xl font-bold">
              {schoolModalData?.teacher_count === 0 && "Zero Teacher Schools"}
              {schoolModalData?.teacher_count === 1 && "One Teacher Schools"}
              {schoolModalData?.teacher_count === 2 && "Two Teacher Schools"}
            </DialogTitle>
            <DialogDescription>
              {schoolModalData && `Total: ${schoolModalData.total_schools} schools`}
            </DialogDescription>
          </DialogHeader>
          
          {/* Filter Section */}
          {schoolModalData?.schools && schoolModalData.schools.length > 0 && (
            <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600 dark:text-slate-400">School Name</label>
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
                    <Input
                      placeholder="Search..."
                      value={schoolFilters.schoolName}
                      onChange={(e) => setSchoolFilters({...schoolFilters, schoolName: e.target.value})}
                      className="pl-8 h-8 text-sm"
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600 dark:text-slate-400">Block</label>
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
                    <Input
                      placeholder="Search..."
                      value={schoolFilters.blockName}
                      onChange={(e) => setSchoolFilters({...schoolFilters, blockName: e.target.value})}
                      className="pl-8 h-8 text-sm"
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600 dark:text-slate-400">UDISE Code</label>
                  <div className="relative">
                    <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
                    <Input
                      placeholder="Search..."
                      value={schoolFilters.udiseCode}
                      onChange={(e) => setSchoolFilters({...schoolFilters, udiseCode: e.target.value})}
                      className="pl-8 h-8 text-sm font-mono"
                    />
                  </div>
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600 dark:text-slate-400">Students (Min)</label>
                  <Input
                    type="number"
                    placeholder="Min"
                    value={schoolFilters.studentsMin}
                    onChange={(e) => setSchoolFilters({...schoolFilters, studentsMin: e.target.value})}
                    className="h-8 text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600 dark:text-slate-400">Students (Max)</label>
                  <Input
                    type="number"
                    placeholder="Max"
                    value={schoolFilters.studentsMax}
                    onChange={(e) => setSchoolFilters({...schoolFilters, studentsMax: e.target.value})}
                    className="h-8 text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-xs font-medium text-slate-600 dark:text-slate-400">Teachers</label>
                  <Input
                    type="number"
                    placeholder="Count"
                    value={schoolFilters.teachers}
                    onChange={(e) => setSchoolFilters({...schoolFilters, teachers: e.target.value})}
                    className="h-8 text-sm"
                  />
                </div>
              </div>
              {(schoolFilters.schoolName || schoolFilters.blockName || schoolFilters.udiseCode || schoolFilters.studentsMin || schoolFilters.studentsMax || schoolFilters.teachers) && (
                <div className="mt-3 flex items-center justify-between">
                  <p className="text-xs text-slate-500">
                    {getFilteredSchools().length} of {schoolModalData.schools.length} schools match filters
                  </p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSchoolFilters({
                      schoolName: "",
                      blockName: "",
                      udiseCode: "",
                      studentsMin: "",
                      studentsMax: "",
                      teachers: ""
                    })}
                    className="h-7 text-xs"
                  >
                    Clear Filters
                  </Button>
                </div>
              )}
            </div>
          )}
          
          <div className="flex-1 overflow-y-auto mt-4">
            {schoolModalLoading ? (
              <div className="flex items-center justify-center h-64">
                <div className="loading-spinner" />
              </div>
            ) : (() => {
              const filteredSchools = getFilteredSchools();
              return filteredSchools.length > 0 ? (
                <div className="space-y-2">
                  <Table>
                    <TableHeader className="sticky top-0 bg-white dark:bg-slate-900 z-10">
                      <TableRow>
                        <TableHead className="w-12">#</TableHead>
                        <TableHead>School Name</TableHead>
                        <TableHead>Block</TableHead>
                        <TableHead className="text-right">UDISE Code</TableHead>
                        <TableHead className="text-right">Students</TableHead>
                        <TableHead className="text-right">Teachers</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredSchools.map((school, index) => (
                        <TableRow 
                          key={school.udise_code} 
                          className="hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer"
                          onClick={() => {
                            if (school.udise_code) {
                              setSchoolModalOpen(false);
                              navigate(`/school/${school.udise_code}`);
                            }
                          }}
                        >
                          <TableCell className="text-slate-500">{index + 1}</TableCell>
                          <TableCell className="font-medium">
                            <span 
                              onClick={(e) => {
                                e.stopPropagation();
                                if (school.udise_code) {
                                  setSchoolModalOpen(false);
                                  navigate(`/school/${school.udise_code}`);
                                }
                              }}
                              className="text-blue-700 hover:underline underline-offset-2 cursor-pointer"
                            >
                              {school.school_name || "N/A"}
                            </span>
                          </TableCell>
                          <TableCell>
                            <span 
                              onClick={(e) => {
                                e.stopPropagation();
                                if (school.block_code) {
                                  navigate(`/block/${school.block_code}`);
                                }
                              }}
                              className="text-blue-700 hover:underline underline-offset-2 cursor-pointer"
                            >
                              {school.block_name || "N/A"}
                            </span>
                          </TableCell>
                          <TableCell className="text-right text-slate-500 font-mono text-sm">{school.udise_code || "N/A"}</TableCell>
                          <TableCell className="text-right font-semibold">{school.student_count?.toLocaleString('en-IN') || 0}</TableCell>
                          <TableCell className="text-right">
                            <Badge variant="outline" className={school.teacher_count === 0 ? "bg-red-50 text-red-700 border-red-200" : school.teacher_count === 1 ? "bg-amber-50 text-amber-700 border-amber-200" : "bg-cyan-50 text-cyan-700 border-cyan-200"}>
                              {school.teacher_count}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : schoolModalData?.schools && schoolModalData.schools.length > 0 ? (
                <div className="text-center py-12">
                  <p className="text-slate-500">No schools match the current filters</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSchoolFilters({
                      schoolName: "",
                      blockName: "",
                      udiseCode: "",
                      studentsMin: "",
                      studentsMax: "",
                      teachers: ""
                    })}
                    className="mt-2"
                  >
                    Clear Filters
                  </Button>
                </div>
              ) : (
                <div className="text-center py-12">
                  <p className="text-slate-500">No schools found</p>
                </div>
              );
            })()}
          </div>
          
          <div className="flex justify-between items-center pt-4 border-t mt-4">
            <p className="text-sm text-slate-500">
              Showing {(() => {
                const filtered = getFilteredSchools();
                return filtered.length;
              })()} of {schoolModalData?.total_schools || 0} schools
              {(() => {
                const filtered = getFilteredSchools();
                const total = schoolModalData?.schools?.length || 0;
                if (filtered.length !== total && total > 0) {
                  return ` (${filtered.length} of ${total} displayed)`;
                }
                return "";
              })()}
            </p>
            <Button variant="outline" onClick={() => setSchoolModalOpen(false)}>
              Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ExecutiveDashboard;
