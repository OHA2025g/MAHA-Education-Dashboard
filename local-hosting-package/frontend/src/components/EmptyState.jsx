import { FileQuestion, Inbox, Search, TrendingUp, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/**
 * EmptyState - Premium empty state with illustrations and actions
 */
const EmptyState = ({
  icon: Icon = Inbox,
  title = "No data available",
  description = "There's nothing to display here yet.",
  action,
  actionLabel,
  className,
  variant = "default"
}) => {
  const variants = {
    default: {
      icon: "text-slate-400",
      bg: "bg-slate-50 dark:bg-slate-900/50"
    },
    search: {
      icon: "text-blue-400",
      bg: "bg-blue-50 dark:bg-blue-900/20"
    },
    error: {
      icon: "text-red-400",
      bg: "bg-red-50 dark:bg-red-900/20"
    },
    success: {
      icon: "text-emerald-400",
      bg: "bg-emerald-50 dark:bg-emerald-900/20"
    }
  };

  const variantStyles = variants[variant] || variants.default;
  const iconMap = {
    default: Inbox,
    search: Search,
    error: AlertCircle,
    success: TrendingUp
  };
  const FinalIcon = Icon === Inbox && variant !== "default" ? iconMap[variant] : Icon;

  return (
    <div className={cn(
      "flex flex-col items-center justify-center py-16 px-4",
      variantStyles.bg,
      "rounded-lg border border-slate-200 dark:border-slate-700",
      className
    )}>
      <div className={cn(
        "relative mb-6",
        "animate-fade-in-up"
      )}>
        {/* Animated background circle */}
        <div className={cn(
          "absolute inset-0 rounded-full opacity-20 blur-2xl",
          variantStyles.bg,
          "animate-pulse"
        )} />
        
        {/* Icon */}
        <div className={cn(
          "relative p-6 rounded-full",
          variantStyles.bg,
          "border-2 border-dashed border-slate-300 dark:border-slate-600"
        )}>
          <FinalIcon className={cn("w-12 h-12", variantStyles.icon)} strokeWidth={1.5} />
        </div>

        {/* Decorative dots */}
        <div className="absolute -top-2 -right-2 w-3 h-3 bg-blue-400 rounded-full animate-ping" />
        <div className="absolute -bottom-2 -left-2 w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
      </div>

      <h3 className={cn(
        "text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2",
        "animate-fade-in-up"
      )} style={{ animationDelay: "100ms" }}>
        {title}
      </h3>
      
      <p className={cn(
        "text-sm text-slate-500 dark:text-slate-400 text-center max-w-sm mb-6",
        "animate-fade-in-up"
      )} style={{ animationDelay: "200ms" }}>
        {description}
      </p>

      {action && actionLabel && (
        <div className="animate-fade-in-up" style={{ animationDelay: "300ms" }}>
          <Button onClick={action} variant="outline" size="sm">
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};

export default EmptyState;

