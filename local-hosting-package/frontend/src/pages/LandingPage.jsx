import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { getBackendUrl } from "@/lib/backend";
import {
  School,
  LayoutDashboard,
  Award,
  ClipboardCheck,
  BookOpen,
  Target,
  Percent,
  UserX,
  GraduationCap,
  UserCircle,
  ArrowRight,
  Building2,
  MapPin,
  Sparkles,
} from "lucide-react";
import ThemeToggle from "@/components/ThemeToggle";

const SAFFRON = "#FF9933";
const BLUE_DARK = "#1e3a8a";
const BLUE_MID = "#2563eb";
const DEMO_EMAIL = "admin@mahaedume.gov.in";
const DEMO_PASSWORD = "admin123";
const BACKEND_URL = getBackendUrl();

const features = [
  { icon: LayoutDashboard, title: "UDISE Dashboard", description: "Unified District Information System for Education data and indicators." },
  { icon: Award, title: "PGI Dashboard", description: "Performance Grading Index for states and districts." },
  { icon: ClipboardCheck, title: "SQAF Dashboard", description: "School Quality Assessment and Accreditation framework." },
  { icon: BookOpen, title: "NAS Dashboard", description: "National Achievement Survey outcomes and learning levels." },
  { icon: Target, title: "NIPUN", description: "National Initiative for Proficiency in Reading with Understanding and Numeracy." },
  { icon: Percent, title: "GER", description: "Gross Enrolment Ratio across stages and regions." },
  { icon: UserX, title: "OOSC", description: "Out of School Children tracking and mainstreaming." },
  { icon: School, title: "Schools", description: "School-level data, infrastructure, and location insights." },
  { icon: GraduationCap, title: "Students", description: "Enrolment, attendance, and student-level analytics." },
  { icon: UserCircle, title: "Teachers", description: "Teacher deployment, qualifications, and capacity." },
];

// Glitter: 50% smaller (3–4px), full screen, rise from bottom to top
const GLITTER_PARTICLES = Array.from({ length: 80 }, (_, i) => ({
  id: i,
  left: (i * 3 + 1) % 99,
  delay: (i * 0.12) % 5,
  duration: 4 + (i % 3) * 0.7,
  size: 3 + (i % 2), // 3 or 4px (50% of 6–8)
  saffron: i % 6 === 0,
}));

const LandingPage = ({ onLogin }) => {
  const navigate = useNavigate();
  const [hoveredCard, setHoveredCard] = useState(null);
  const [udiseLoading, setUdiseLoading] = useState(false);
  const [teachersLoading, setTeachersLoading] = useState(false);
  const [studentsLoading, setStudentsLoading] = useState(false);
  const [schoolsLoading, setSchoolsLoading] = useState(false);
  const [sqafLoading, setSqafLoading] = useState(false);

  const demoLoginAndGo = async (targetPath, successMessage) => {
    if (!onLogin) {
      navigate(targetPath);
      return;
    }
    try {
      const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
        email: DEMO_EMAIL,
        password: DEMO_PASSWORD,
      });
      const { access_token, user } = response.data;
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(user));
      axios.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
      toast.success(successMessage || `Signed in as ${user.full_name}`);
      onLogin(user);
      navigate(targetPath);
    } catch (err) {
      const msg = err.response?.data?.detail || "Login failed. Try signing in from the login page.";
      toast.error(msg);
    }
  };

  const handleUdiseClick = async () => {
    setUdiseLoading(true);
    try {
      await demoLoginAndGo("/executive-dashboard", `Signed in as demo user. Opening Executive Dashboard…`);
    } finally {
      setUdiseLoading(false);
    }
  };

  const handleTeachersClick = async () => {
    setTeachersLoading(true);
    try {
      await demoLoginAndGo("/teacher-dashboard", `Signed in as demo user. Opening Teacher Analytics…`);
    } finally {
      setTeachersLoading(false);
    }
  };

  const handleStudentsClick = async () => {
    setStudentsLoading(true);
    try {
      await demoLoginAndGo("/enrolment-dashboard", `Signed in as demo user. Opening Enrolment Analytics…`);
    } finally {
      setStudentsLoading(false);
    }
  };

  const handleSchoolsClick = async () => {
    setSchoolsLoading(true);
    try {
      await demoLoginAndGo("/dropbox-dashboard", `Signed in as demo user. Opening Dropbox Remarks Analytics…`);
    } finally {
      setSchoolsLoading(false);
    }
  };

  const handleSqafClick = async () => {
    setSqafLoading(true);
    try {
      await demoLoginAndGo("/sqaaf", `Signed in as demo user. Opening SQAAF Dashboard…`);
    } finally {
      setSqafLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col relative"
      style={{
        background: `linear-gradient(180deg,
          ${BLUE_DARK} 0%,
          #2563eb 12%,
          rgba(255,255,255,0.95) 28%,
          #ffffff 38%,
          #ffffff 52%,
          rgba(255,255,255,0.97) 58%,
          rgba(255,153,51,0.15) 68%,
          rgba(30,58,138,0.92) 82%,
          ${BLUE_DARK} 100%)`,
      }}
    >
      {/* Full-screen glitter: bottom to top, 50% smaller */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden" aria-hidden>
        {GLITTER_PARTICLES.map((p) => (
          <span
            key={p.id}
            className="absolute rounded-full bottom-0"
            style={{
              left: `${p.left}%`,
              width: `${p.size}px`,
              height: `${p.size}px`,
              marginLeft: `-${p.size / 2}px`,
              background: p.saffron ? "#FF9933" : "#ffffff",
              boxShadow: p.saffron
                ? "0 0 6px 2px rgba(255,153,51,0.85), 0 0 12px 4px rgba(255,153,51,0.4)"
                : "0 0 6px 2px rgba(255,255,255,0.85), 0 0 12px 4px rgba(255,255,255,0.45)",
              animation: `glitter-rise ${p.duration}s linear infinite`,
              animationDelay: `${p.delay}s`,
            }}
          />
        ))}
      </div>
      <style>{`
        @keyframes gradient-shift {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }
        @keyframes glitter-rise {
          0% { transform: translateY(0); opacity: 0.75; }
          100% { transform: translateY(-100vh); opacity: 0.8; }
        }
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        @keyframes shimmer-sweep {
          0% { transform: translateX(-100%) skewX(-12deg); }
          100% { transform: translateX(200%) skewX(-12deg); }
        }
        .hero-gradient {
          background: transparent;
        }
        .card-interactive {
          transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }
        .card-interactive:hover {
          transform: translateY(-4px) scale(1.02);
          box-shadow: 0 20px 40px -12px rgba(30, 58, 138, 0.25), 0 0 0 2px ${SAFFRON}40;
        }
        .btn-saffron {
          background: ${SAFFRON};
          color: #fff;
          transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }
        .btn-saffron:hover {
          background: #e88b2a;
          transform: translateY(-2px);
          box-shadow: 0 12px 24px -8px ${SAFFRON}99;
        }
        .btn-saffron:active {
          transform: translateY(0);
        }
      `}</style>

      {/* Top bar - blended with page gradient */}
      <header
        className="sticky top-0 z-50 relative flex items-center justify-between px-4 lg:px-10 py-3 shadow-sm backdrop-blur-md"
        style={{
          background: `linear-gradient(90deg, rgba(30,58,138,0.93) 0%, rgba(37,99,235,0.93) 50%, rgba(255,153,51,0.27) 100%)`,
          borderBottom: "2px solid rgba(255,153,51,0.5)",
        }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-11 h-11 rounded-xl flex items-center justify-center transition-all duration-300 hover:scale-110 hover:rotate-6"
            style={{ background: `linear-gradient(135deg, ${BLUE_DARK}, ${SAFFRON})` }}
          >
            <School className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="font-bold text-lg text-white" style={{ fontFamily: "Manrope" }}>
              MahaEduMe
            </span>
            <span className="block text-[11px] uppercase tracking-wider text-white/80">
              School Education Analytics
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <ThemeToggle className="text-white hover:bg-white/20 rounded-lg p-2" />
          <Button
            variant="outline"
            className="border-2 border-white/80 text-white hover:bg-white hover:text-[#1e3a8a] font-semibold rounded-xl transition-all duration-200"
            onClick={() => navigate("/login")}
          >
            Sign In
          </Button>
        </div>
      </header>

      {/* Hero - blue gradient with white text */}
      <section className="hero-gradient relative overflow-hidden px-4 lg:px-10 py-16 lg:py-24">
        {/* Shimmer sweep - diagonal light band moving across hero */}
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden" aria-hidden>
          <div
            className="absolute top-0 bottom-0 w-[60%] opacity-80"
            style={{
              background: "linear-gradient(105deg, transparent 0%, rgba(255,255,255,0.12) 30%, rgba(255,255,255,0.35) 50%, rgba(255,255,255,0.12) 70%, transparent 100%)",
              animation: "shimmer-sweep 5s ease-in-out infinite",
            }}
          />
        </div>
        {/* Decorative circles */}
        <div className="absolute top-20 left-10 w-32 h-32 rounded-full border-2 border-white/20 animate-[float_4s_ease-in-out_infinite]" />
        <div className="absolute bottom-24 right-20 w-48 h-48 rounded-full border-2 border-white/10 animate-[float_5s_ease-in-out_infinite]" style={{ animationDelay: "1s" }} />
        <div className="absolute top-1/2 right-1/4 w-24 h-24 rounded-full bg-[#FF9933]/20 blur-2xl animate-[float_6s_ease-in-out_infinite]" style={{ animationDelay: "2s" }} />

        <div className="relative z-10 max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/15 backdrop-blur text-white/95 text-sm mb-6 border border-white/20 transition-all duration-300 hover:bg-white/25 hover:scale-105">
            <MapPin className="w-4 h-4" />
            <span>Pune District • Maharashtra</span>
            <Sparkles className="w-4 h-4 text-[#FF9933]" />
          </div>
          <h1
            className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-white mb-4 drop-shadow-lg"
            style={{ fontFamily: "Manrope" }}
          >
            School Education
            <br />
            <span className="text-[#FF9933] drop-shadow-md">Analytics Portal</span>
          </h1>
          <p className="text-lg sm:text-xl max-w-2xl mx-auto mb-10" style={{ color: SAFFRON }}>
            One platform for evidence-based decision-making. Monitor school health, enrolment, infrastructure and compliance across every block and school.
          </p>
          <Button
            size="lg"
            className="btn-saffron px-8 py-6 text-base font-semibold rounded-xl"
            onClick={() => navigate("/login")}
          >
            Enter Dashboard
            <ArrowRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
      </section>

      {/* Feature cards - blended section (no separate strip) */}
      <section className="px-4 lg:px-10 py-16 lg:py-20 relative">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-2xl font-bold text-[#1e3a8a] mb-2 text-center" style={{ fontFamily: "Manrope" }}>
            What you can do
          </h2>
          <p className="text-gray-600 text-center max-w-2xl mx-auto mb-10">
            Ten mission-ready dashboards in one place — UDISE, PGI, SQAF, NAS, NIPUN, GER, OOSC and more.
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-5">
            {features.map((f, i) => (
              <div
                key={f.title}
                onMouseEnter={() => setHoveredCard(i)}
                onMouseLeave={() => setHoveredCard(null)}
                className={`card-interactive rounded-2xl border-2 bg-white p-5 cursor-pointer relative ${
                  hoveredCard === i
                    ? "border-[#FF9933] shadow-xl"
                    : "border-blue-100 hover:border-blue-200"
                } ${(f.title === "UDISE Dashboard" && udiseLoading) || (f.title === "Teachers" && teachersLoading) || (f.title === "Students" && studentsLoading) || (f.title === "Schools" && schoolsLoading) || (f.title === "SQAF Dashboard" && sqafLoading) ? "pointer-events-none opacity-75" : ""}`}
                onClick={() => {
                  if (f.title === "UDISE Dashboard") handleUdiseClick();
                  else if (f.title === "Teachers") handleTeachersClick();
                  else if (f.title === "Students") handleStudentsClick();
                  else if (f.title === "Schools") handleSchoolsClick();
                  else if (f.title === "SQAF Dashboard") handleSqafClick();
                  else navigate("/login");
                }}
                onKeyDown={(e) => {
                  if (e.key !== "Enter") return;
                  if (f.title === "UDISE Dashboard") handleUdiseClick();
                  else if (f.title === "Teachers") handleTeachersClick();
                  else if (f.title === "Students") handleStudentsClick();
                  else if (f.title === "Schools") handleSchoolsClick();
                  else if (f.title === "SQAF Dashboard") handleSqafClick();
                  else navigate("/login");
                }}
                role="button"
                tabIndex={0}
              >
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center mb-3 transition-colors duration-200 ${
                    hoveredCard === i ? "bg-[#FF9933]/20" : "bg-blue-100"
                  }`}
                  style={hoveredCard === i ? { color: SAFFRON } : { color: BLUE_MID }}
                >
                  <f.icon className="w-6 h-6" />
                </div>
                <h3 className="font-semibold text-[#1e3a8a] mb-1">{f.title}</h3>
                <p className="text-sm text-gray-600 leading-snug">{f.description}</p>
                {f.title === "UDISE Dashboard" && udiseLoading && (
                  <div className="absolute inset-0 rounded-2xl bg-white/80 flex items-center justify-center">
                    <span className="text-sm font-medium text-[#1e3a8a]">Signing in…</span>
                  </div>
                )}
                {f.title === "Teachers" && teachersLoading && (
                  <div className="absolute inset-0 rounded-2xl bg-white/80 flex items-center justify-center">
                    <span className="text-sm font-medium text-[#1e3a8a]">Signing in…</span>
                  </div>
                )}
                {f.title === "Students" && studentsLoading && (
                  <div className="absolute inset-0 rounded-2xl bg-white/80 flex items-center justify-center">
                    <span className="text-sm font-medium text-[#1e3a8a]">Signing in…</span>
                  </div>
                )}
                {f.title === "Schools" && schoolsLoading && (
                  <div className="absolute inset-0 rounded-2xl bg-white/80 flex items-center justify-center">
                    <span className="text-sm font-medium text-[#1e3a8a]">Signing in…</span>
                  </div>
                )}
                {f.title === "SQAF Dashboard" && sqafLoading && (
                  <div className="absolute inset-0 rounded-2xl bg-white/80 flex items-center justify-center">
                    <span className="text-sm font-medium text-[#1e3a8a]">Signing in…</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer - blended with page gradient (no separate block) */}
      <footer
        className="py-6 px-4 text-white relative"
        style={{
          background: `linear-gradient(180deg, rgba(30,58,138,0.97) 0%, ${BLUE_DARK} 30%, ${BLUE_DARK} 100%)`,
          boxShadow: "0 -4px 20px rgba(255,153,51,0.15)",
        }}
      >
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-white/90 text-sm">
            <Building2 className="w-5 h-5 text-[#FF9933]" />
            <span>Government of Maharashtra • Education Department</span>
          </div>
          <p className="text-white/80 text-sm">
            © {new Date().getFullYear()} MahaEduMe • Powered by Agrayian AI Labs
          </p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
