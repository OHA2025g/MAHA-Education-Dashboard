import React from "react";
import { AlertTriangle, Bug, Copy, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

function safeStringifyError(error, info) {
  try {
    return JSON.stringify(
      {
        name: error?.name,
        message: error?.message,
        stack: error?.stack,
        componentStack: info?.componentStack,
        userAgent: typeof navigator !== "undefined" ? navigator.userAgent : undefined,
        url: typeof window !== "undefined" ? window.location.href : undefined,
        ts: new Date().toISOString(),
      },
      null,
      2,
    );
  } catch {
    return String(error || "Unknown error");
  }
}

export default class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, info: null, detailsOpen: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    this.setState({ info });
    // eslint-disable-next-line no-console
    console.error("AppErrorBoundary caught an error:", error, info);
  }

  reset = () => {
    this.setState({ hasError: false, error: null, info: null, detailsOpen: false });
    if (typeof this.props.onReset === "function") this.props.onReset();
  };

  reload = () => {
    if (typeof window !== "undefined") window.location.reload();
  };

  copyDetails = async () => {
    const { error, info } = this.state;
    const payload = safeStringifyError(error, info);
    try {
      await navigator.clipboard.writeText(payload);
      toast.success("Error details copied");
    } catch {
      toast.error("Could not copy error details");
    }
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    const { error, info, detailsOpen } = this.state;
    const details = safeStringifyError(error, info);

    return (
      <div className="min-h-screen bg-background text-foreground">
        <div className="mx-auto max-w-3xl px-4 py-10">
          <div className="rounded-2xl border bg-card p-6 shadow-sm">
            <div className="flex items-start gap-4">
              <div className="mt-0.5 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-destructive/10 text-destructive">
                <AlertTriangle className="h-5 w-5" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <h1 className="text-xl font-semibold tracking-tight">Something went wrong</h1>
                  <span className="inline-flex items-center gap-1 rounded-full border bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                    <Bug className="h-3.5 w-3.5" />
                    UI crash
                  </span>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">
                  Try again. If it keeps happening, copy the details and share them with the dev team.
                </p>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Button onClick={this.reset} variant="default">
                    <RotateCcw className="mr-2 h-4 w-4" />
                    Try again
                  </Button>
                  <Button onClick={this.reload} variant="secondary">
                    Reload page
                  </Button>
                  <Button onClick={this.copyDetails} variant="outline">
                    <Copy className="mr-2 h-4 w-4" />
                    Copy details
                  </Button>
                  <Button
                    onClick={() => this.setState({ detailsOpen: !detailsOpen })}
                    variant="ghost"
                    className="text-muted-foreground"
                  >
                    {detailsOpen ? "Hide details" : "Show details"}
                  </Button>
                </div>

                {detailsOpen ? (
                  <pre className="mt-4 max-h-[360px] overflow-auto rounded-xl border bg-muted/30 p-3 text-xs leading-relaxed text-muted-foreground">
                    {details}
                  </pre>
                ) : null}
              </div>
            </div>
          </div>

          <p className="mt-6 text-center text-xs text-muted-foreground">
            Maharashtra Education Dashboard • If needed, refresh and sign in again.
          </p>
        </div>
      </div>
    );
  }
}


