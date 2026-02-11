import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import AppErrorBoundary from "@/components/AppErrorBoundary";
import { ThemeProvider } from "next-themes";

// Suppress ResizeObserver loop errors (harmless, caused by Recharts and other libraries)
// This is a known issue with React 18+ StrictMode and ResizeObserver API
const originalError = console.error;
console.error = (...args) => {
  if (
    typeof args[0] === 'string' &&
    args[0].includes('ResizeObserver loop completed with undelivered notifications')
  ) {
    // Suppress this specific error - it's harmless and caused by Recharts
    return;
  }
  originalError.call(console, ...args);
};

// Also handle unhandled errors
window.addEventListener('error', (event) => {
  if (
    event.message &&
    event.message.includes('ResizeObserver loop completed with undelivered notifications')
  ) {
    event.preventDefault();
    return false;
  }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  if (
    event.reason &&
    typeof event.reason === 'string' &&
    event.reason.includes('ResizeObserver loop')
  ) {
    event.preventDefault();
    return false;
  }
});

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <AppErrorBoundary>
      <ThemeProvider attribute="class" defaultTheme="light" enableSystem={false}>
        <App />
      </ThemeProvider>
    </AppErrorBoundary>
  </React.StrictMode>,
);
