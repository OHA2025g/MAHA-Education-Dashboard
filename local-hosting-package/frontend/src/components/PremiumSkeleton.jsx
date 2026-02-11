import { cn } from "@/lib/utils";

/**
 * PremiumSkeleton - Enhanced skeleton loader with shimmer effect
 */
const PremiumSkeleton = ({ 
  className, 
  variant = "default",
  lines = 1,
  ...props 
}) => {
  const variants = {
    default: "h-4 w-full rounded",
    circular: "h-12 w-12 rounded-full",
    rectangular: "h-20 w-full rounded-lg",
    text: "h-4 w-3/4 rounded",
    title: "h-6 w-2/3 rounded",
    card: "h-32 w-full rounded-lg"
  };

  if (lines > 1) {
    return (
      <div className={cn("space-y-2", className)} {...props}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "relative overflow-hidden rounded",
              variants[variant] || variants.default,
              "bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200",
              "dark:from-slate-800 dark:via-slate-700 dark:to-slate-800",
              "animate-shimmer"
            )}
            style={{
              animationDelay: `${i * 100}ms`
            }}
          />
        ))}
      </div>
    );
  }

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded",
        variants[variant] || variants.default,
        "bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200",
        "dark:from-slate-800 dark:via-slate-700 dark:to-slate-800",
        "animate-shimmer",
        className
      )}
      {...props}
    />
  );
};

export const SkeletonCard = () => (
  <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6 space-y-4">
    <PremiumSkeleton variant="title" />
    <PremiumSkeleton variant="text" lines={3} />
    <div className="flex gap-4">
      <PremiumSkeleton variant="circular" />
      <div className="flex-1 space-y-2">
        <PremiumSkeleton variant="text" />
        <PremiumSkeleton variant="text" className="w-2/3" />
      </div>
    </div>
  </div>
);

export const SkeletonKPICard = () => (
  <div className="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-5">
    <PremiumSkeleton variant="text" className="w-24 mb-3" />
    <PremiumSkeleton variant="title" className="w-32 mb-2" />
    <div className="flex items-center gap-2">
      <PremiumSkeleton variant="circular" />
      <PremiumSkeleton variant="text" className="w-20" />
    </div>
  </div>
);

export default PremiumSkeleton;

