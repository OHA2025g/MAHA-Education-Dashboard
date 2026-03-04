import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getBackendUrl } from "@/lib/backend";

/**
 * Shown when dashboard data fails to load (e.g. backend not running).
 * Displays a clear message and Retry button.
 */
export default function DataLoadError({ onRetry, title = "Data could not be loaded" }) {
  const backendUrl = getBackendUrl();

  return (
    <div className="rounded-xl border border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/40 p-6 text-center max-w-lg mx-auto">
      <AlertCircle className="w-12 h-12 text-amber-600 dark:text-amber-500 mx-auto mb-3" />
      <h3 className="font-semibold text-slate-900 dark:text-slate-100">{title}</h3>
      <p className="text-sm text-slate-600 dark:text-slate-400 mt-2">
        Make sure the backend API is running at{" "}
        <code className="px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/50 text-xs">
          {backendUrl}
        </code>
        . From the project folder run: <code className="text-xs">docker compose up -d</code> (or start the backend manually).
      </p>
      {onRetry && (
        <Button
          variant="outline"
          className="mt-4 border-amber-300 dark:border-amber-700"
          onClick={onRetry}
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Retry
        </Button>
      )}
    </div>
  );
}
