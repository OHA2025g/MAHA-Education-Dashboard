import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

/**
 * PageTransition - Smooth fade-in animation for page changes
 */
const PageTransition = ({ children }) => {
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const [transitionStage, setTransitionStage] = useState("entering");

  useEffect(() => {
    if (location !== displayLocation) {
      setTransitionStage("exiting");
    }
  }, [location, displayLocation]);

  useEffect(() => {
    if (transitionStage === "exiting") {
      const timer = setTimeout(() => {
        setDisplayLocation(location);
        setTransitionStage("entering");
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [transitionStage, location]);

  return (
    <div
      className={cn(
        "transition-all duration-300 ease-out",
        transitionStage === "entering" && "opacity-100 translate-y-0",
        transitionStage === "exiting" && "opacity-0 translate-y-4"
      )}
    >
      {children}
    </div>
  );
};

export default PageTransition;

