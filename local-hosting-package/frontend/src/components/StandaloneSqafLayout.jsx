import React from "react";
import { Outlet, Link, useNavigate } from "react-router-dom";
import { ClipboardCheck, ArrowLeft, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";

/**
 * Standalone layout for the independent SQAAF Dashboard.
 * Not part of MH Education Dashboard 2025-26; linked from the Landing Page "SQAF Dashboard" card.
 */
const StandaloneSqafLayout = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    if (onLogout) onLogout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50/80">
      <header className="dashboard-header glass px-4 lg:px-8 py-4 border-b border-slate-200/80 sticky top-0 z-40">
        <div className="flex items-center justify-between gap-4 max-w-[1600px] mx-auto">
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className="flex items-center gap-2 text-slate-600 hover:text-slate-900 transition-colors"
              title="Back to MH Education Dashboard"
            >
              <ArrowLeft className="w-5 h-5" />
              <span className="text-sm font-medium hidden sm:inline">Back to MH Education</span>
            </Link>
            <div className="h-6 w-px bg-slate-300" />
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
                <ClipboardCheck className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-slate-800 tracking-tight" style={{ fontFamily: "Manrope" }}>
                  SQAAF Dashboard
                </h1>
                <p className="text-xs text-slate-500">School Quality Assessment & Accreditation</p>
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-slate-600 truncate max-w-[140px]">{user?.full_name || "User"}</span>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleLogout}
              className="text-slate-500 hover:text-slate-900"
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
};

export default StandaloneSqafLayout;
