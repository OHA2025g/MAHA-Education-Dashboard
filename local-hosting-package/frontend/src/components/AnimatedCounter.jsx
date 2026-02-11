import { useState, useEffect, useRef } from "react";
import { cn } from "@/lib/utils";

/**
 * AnimatedCounter - Smoothly animates numbers from 0 to target value
 */
const AnimatedCounter = ({ 
  value, 
  duration = 1500, 
  decimals = 0,
  prefix = "",
  suffix = "",
  className,
  formatter = null
}) => {
  const [displayValue, setDisplayValue] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const startTimeRef = useRef(null);
  const animationFrameRef = useRef(null);
  const previousValueRef = useRef(value);

  useEffect(() => {
    // Only animate if value actually changed
    if (value === previousValueRef.current) return;
    
    const startValue = previousValueRef.current || 0;
    const endValue = value;
    const startTime = performance.now();
    startTimeRef.current = startTime;
    setIsAnimating(true);

    const animate = (currentTime) => {
      if (!startTimeRef.current) return;
      
      const elapsed = currentTime - startTimeRef.current;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function (ease-out-cubic)
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = startValue + (endValue - startValue) * eased;
      
      setDisplayValue(current);
      
      if (progress < 1) {
        animationFrameRef.current = requestAnimationFrame(animate);
      } else {
        setDisplayValue(endValue);
        setIsAnimating(false);
        previousValueRef.current = endValue;
      }
    };

    animationFrameRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [value, duration]);

  const formatNumber = (num) => {
    if (formatter) return formatter(num);
    return num.toLocaleString('en-IN', { 
      minimumFractionDigits: decimals, 
      maximumFractionDigits: decimals 
    });
  };

  return (
    <span className={cn("tabular-nums", className)}>
      {prefix}
      {formatNumber(displayValue)}
      {suffix}
    </span>
  );
};

export default AnimatedCounter;

