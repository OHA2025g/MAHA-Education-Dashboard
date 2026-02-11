import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator, CommandShortcut } from "@/components/ui/command";
import { ArrowRight, LogOut, RotateCcw, Settings2 } from "lucide-react";
import { useTheme } from "next-themes";
import { useScope } from "@/context/ScopeContext";

function isMacLike() {
  if (typeof navigator === "undefined") return false;
  return /Mac|iPhone|iPad|iPod/i.test(navigator.platform);
}

export default function CommandPalette({ navItems, onLogout }) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { clearScope } = useScope();
  const { resolvedTheme, setTheme } = useTheme();

  const platformKey = isMacLike() ? "⌘" : "Ctrl";

  useEffect(() => {
    const onKeyDown = (e) => {
      const isK = e.key?.toLowerCase?.() === "k";
      if (!isK) return;
      if (!(e.metaKey || e.ctrlKey)) return;
      e.preventDefault();
      setOpen((v) => !v);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  useEffect(() => {
    const onOpen = () => setOpen(true);
    window.addEventListener("open-command-palette", onOpen);
    return () => window.removeEventListener("open-command-palette", onOpen);
  }, []);

  const navigable = useMemo(() => {
    const items = Array.isArray(navItems) ? navItems : [];
    return items
      .filter((x) => x && x.path && x.label)
      .map((x) => ({
        ...x,
        isActive: location.pathname === x.path || (x.exact && location.pathname === "/"),
      }));
  }, [navItems, location.pathname]);

  const go = (path) => {
    if (!path) return;
    setOpen(false);
    navigate(path);
  };

  const doClearScope = () => {
    clearScope?.();
    setOpen(false);
  };

  const toggleTheme = () => {
    const cur = resolvedTheme || "light";
    setTheme(cur === "dark" ? "light" : "dark");
    setOpen(false);
  };

  const doLogout = () => {
    setOpen(false);
    if (typeof onLogout === "function") onLogout();
  };

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Search dashboards, actions…" />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>

        <CommandGroup heading="Navigate">
          {navigable.map((item) => (
            <CommandItem
              key={item.path}
              onSelect={() => go(item.path)}
              className={item.isActive ? "data-[selected=true]:bg-accent/70" : undefined}
            >
              {item.icon ? <item.icon className="h-4 w-4" /> : <ArrowRight className="h-4 w-4" />}
              <span>{item.label}</span>
              <CommandShortcut>↵</CommandShortcut>
            </CommandItem>
          ))}
        </CommandGroup>

        <CommandSeparator />

        <CommandGroup heading="Actions">
          <CommandItem onSelect={doClearScope}>
            <RotateCcw className="h-4 w-4" />
            <span>Clear scope filters</span>
          </CommandItem>
          <CommandItem onSelect={toggleTheme}>
            <Settings2 className="h-4 w-4" />
            <span>Toggle theme</span>
            <CommandShortcut>{platformKey} T</CommandShortcut>
          </CommandItem>
          <CommandItem onSelect={doLogout}>
            <LogOut className="h-4 w-4" />
            <span>Logout</span>
          </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  );
}


