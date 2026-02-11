import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import { cn } from "@/lib/utils";

/**
 * AnimatedCard - Card that animates in when scrolled into view
 */
const AnimatedCard = ({ 
  children, 
  className,
  delay = 0,
  direction = "up",
  ...props 
}) => {
  const [ref, isVisible] = useScrollAnimation({ threshold: 0.1 });

  const directions = {
    up: "translate-y-8",
    down: "-translate-y-8",
    left: "translate-x-8",
    right: "-translate-x-8",
    fade: ""
  };

  return (
    <div
      ref={ref}
      className={cn(
        "transition-all duration-700 ease-out",
        isVisible 
          ? "opacity-100 translate-y-0 translate-x-0" 
          : `opacity-0 ${directions[direction]}`,
        className
      )}
      style={{
        transitionDelay: `${delay}ms`
      }}
      {...props}
    >
      {children}
    </div>
  );
};

export default AnimatedCard;

