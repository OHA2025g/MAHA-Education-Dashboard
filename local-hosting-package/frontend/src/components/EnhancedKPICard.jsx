import { useState, useEffect } from "react";
import { TrendingUp, TrendingDown, Minus, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";
import AnimatedCounter from "./AnimatedCounter";
import MetricInfoButton from "./MetricInfoButton";

/**
 * Enhanced KPICard with animated counters, gradients, and premium effects
 */
const EnhancedKPICard = ({ 
  label, 
  value, 
  suffix = "", 
  trend = null, 
  trendValue = null,
  icon: Icon,
  className,
  onClick,
  testId,
  color = "blue",
  gradient = false,
  pulse = false,
  size = "normal",
  metricKey = null
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation when component mounts
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const getTrendIcon = () => {
    if (trend === "up") return <TrendingUp className="w-4 h-4 text-emerald-500" />;
    if (trend === "down") return <TrendingDown className="w-4 h-4 text-red-500" />;
    return <Minus className="w-4 h-4 text-slate-400" />;
  };
  
  const getTrendColor = () => {
    if (trend === "up") return "text-emerald-600";
    if (trend === "down") return "text-red-600";
    return "text-slate-500";
  };

  const colorClasses = {
    blue: {
      bg: "bg-gradient-to-br from-blue-50 to-blue-100/50",
      icon: "bg-gradient-to-br from-blue-500 to-blue-600",
      border: "border-blue-200/50",
      glow: "shadow-blue-500/20"
    },
    green: {
      bg: "bg-gradient-to-br from-emerald-50 to-emerald-100/50",
      icon: "bg-gradient-to-br from-emerald-500 to-emerald-600",
      border: "border-emerald-200/50",
      glow: "shadow-emerald-500/20"
    },
    purple: {
      bg: "bg-gradient-to-br from-purple-50 to-purple-100/50",
      icon: "bg-gradient-to-br from-purple-500 to-purple-600",
      border: "border-purple-200/50",
      glow: "shadow-purple-500/20"
    },
    amber: {
      bg: "bg-gradient-to-br from-amber-50 to-amber-100/50",
      icon: "bg-gradient-to-br from-amber-500 to-amber-600",
      border: "border-amber-200/50",
      glow: "shadow-amber-500/20"
    },
    red: {
      bg: "bg-gradient-to-br from-red-50 to-red-100/50",
      icon: "bg-gradient-to-br from-red-500 to-red-600",
      border: "border-red-200/50",
      glow: "shadow-red-500/20"
    },
    cyan: {
      bg: "bg-gradient-to-br from-cyan-50 to-cyan-100/50",
      icon: "bg-gradient-to-br from-cyan-500 to-cyan-600",
      border: "border-cyan-200/50",
      glow: "shadow-cyan-500/20"
    }
  };

  const colors = colorClasses[color] || colorClasses.blue;
  const isLarge = size === "large";

  return (
    <div 
      className={cn(
        "kpi-card group cursor-pointer relative overflow-hidden",
        "transition-all duration-300 ease-out",
        "hover:shadow-xl hover:-translate-y-1",
        gradient && colors.bg,
        !gradient && "bg-white",
        colors.border && "border",
        isHovered && `shadow-lg ${colors.glow}`,
        isVisible && "animate-fade-in-up",
        pulse && "animate-pulse-subtle",
        className
      )}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      data-testid={testId}
      style={{
        animationDelay: `${Math.random() * 200}ms`
      }}
    >
      {/* Animated background gradient on hover */}
      {gradient && (
        <div className={cn(
          "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500",
          colors.bg
        )} />
      )}

      {/* Shine effect on hover */}
      <div className={cn(
        "absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000",
        "bg-gradient-to-r from-transparent via-white/20 to-transparent",
        "pointer-events-none"
      )} />

      <div className="relative flex items-start justify-between z-10">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <p className="kpi-label">{label}</p>
            {metricKey && (
              <MetricInfoButton 
                metricKey={metricKey}
                variant="ghost"
                size="sm"
              />
            )}
            {pulse && (
              <Sparkles className="w-3 h-3 text-amber-500 animate-pulse" />
            )}
          </div>
          <div className="flex items-baseline gap-2">
            {typeof value === 'number' ? (
              <AnimatedCounter
                value={value}
                duration={1500}
                className={cn(
                  "kpi-value",
                  isLarge && "text-4xl"
                )}
              />
            ) : (
              <span className={cn("kpi-value", isLarge && "text-4xl")}>
                {value}
              </span>
            )}
            {suffix && (
              <span className={cn(
                "text-lg font-semibold text-slate-500 transition-colors",
                isHovered && "text-slate-700"
              )}>
                {suffix}
              </span>
            )}
          </div>
          {trend && trendValue && (
            <div className={cn(
              "flex items-center gap-1 mt-2 transition-all duration-300",
              getTrendColor(),
              isHovered && "scale-105"
            )}>
              {getTrendIcon()}
              <span className="text-sm font-medium">{trendValue}</span>
            </div>
          )}
        </div>
        {Icon && (
          <div className={cn(
            "p-3 rounded-xl transition-all duration-300",
            "group-hover:scale-110 group-hover:rotate-3",
            gradient ? colors.icon : "bg-slate-100 group-hover:bg-slate-200"
          )}>
            <Icon 
              className={cn(
                "transition-colors duration-300",
                gradient ? "w-6 h-6 text-white" : "w-5 h-5 text-slate-600",
                isLarge && "w-7 h-7"
              )} 
              strokeWidth={1.5} 
            />
          </div>
        )}
      </div>

      {/* Decorative corner accent */}
      <div className={cn(
        "absolute top-0 right-0 w-20 h-20 opacity-10 group-hover:opacity-20 transition-opacity",
        "bg-gradient-to-br from-current to-transparent rounded-bl-full",
        gradient && colors.icon
      )} />
    </div>
  );
};

export default EnhancedKPICard;

