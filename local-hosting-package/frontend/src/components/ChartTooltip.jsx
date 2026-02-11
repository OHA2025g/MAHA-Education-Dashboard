import { cn } from "@/lib/utils";

/**
 * Enhanced Chart Tooltip with better styling
 */
export const EnhancedTooltip = ({ active, payload, label, formatter, labelFormatter }) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className={cn(
      "bg-white dark:bg-slate-800",
      "border border-slate-200 dark:border-slate-700",
      "rounded-lg shadow-xl",
      "p-3 min-w-[180px]",
      "backdrop-blur-sm"
    )}>
      <div className="mb-2 pb-2 border-b border-slate-200 dark:border-slate-700">
        <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">
          {labelFormatter ? labelFormatter(label) : label}
        </p>
      </div>
      <div className="space-y-1.5">
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-xs text-slate-600 dark:text-slate-400">
                {entry.name}
              </span>
            </div>
            <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 tabular-nums">
              {formatter ? formatter(entry.value, entry.name) : entry.value?.toLocaleString('en-IN')}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default EnhancedTooltip;

