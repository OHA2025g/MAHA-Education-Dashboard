import { GraduationCap } from "lucide-react";

export default function AppBootScreen({ title = "Maharashtra Education Dashboard", subtitle = "Loading…" }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,hsl(var(--accent))_0%,transparent_40%),radial-gradient(circle_at_80%_30%,hsl(var(--chart-3))_0%,transparent_45%)] opacity-[0.12]" />
        <div className="mx-auto flex min-h-screen max-w-4xl flex-col items-center justify-center px-4">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent text-accent-foreground shadow-sm">
              <GraduationCap className="h-6 w-6" />
            </div>
            <div>
              <div className="text-lg font-semibold tracking-tight">{title}</div>
              <div className="text-sm text-muted-foreground">{subtitle}</div>
            </div>
          </div>

          <div className="mt-8 w-full max-w-md">
            <div className="h-2 w-full overflow-hidden rounded-full bg-muted">
              <div className="h-full w-1/3 animate-pulse bg-accent" />
            </div>
            <div className="mt-3 text-center text-xs text-muted-foreground">
              Tip: Press <span className="font-medium">Ctrl</span>/<span className="font-medium">⌘</span>+
              <span className="font-medium">K</span> for quick navigation.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


