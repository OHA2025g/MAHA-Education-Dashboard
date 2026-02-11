import { Info } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import MetricInfoButton from "./MetricInfoButton";

/**
 * ChartInfoButton - Info button for charts/graphs
 * Shows formula and explanation when clicked
 */
const ChartInfoButton = ({ 
  metricKey,
  className,
  position = "top-right" // "top-right" | "top-left" | "bottom-right" | "bottom-left"
}) => {
  if (!metricKey) return null;

  const positionClasses = {
    "top-right": "absolute top-2 right-2",
    "top-left": "absolute top-2 left-2",
    "bottom-right": "absolute bottom-2 right-2",
    "bottom-left": "absolute bottom-2 left-2"
  };

  return (
    <div className={cn("z-10", positionClasses[position], className)}>
      <MetricInfoButton 
        metricKey={metricKey}
        variant="outline"
        size="sm"
        className="bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm shadow-sm hover:bg-white dark:hover:bg-slate-800"
      />
    </div>
  );
};

export default ChartInfoButton;

