"use client";

import { useState, useRef, useEffect } from "react";
import { HelpCircle } from "lucide-react";

interface TooltipProps {
  content: string;
  children?: React.ReactNode;
}

export function Tooltip({ content, children }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const triggerRef = useRef<HTMLButtonElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const trigger = triggerRef.current.getBoundingClientRect();
      const tooltip = tooltipRef.current.getBoundingClientRect();
      
      // Position above the icon
      let top = trigger.top - tooltip.height - 8;
      let left = trigger.left + trigger.width / 2 - tooltip.width / 2;
      
      // Keep within viewport
      if (left < 8) left = 8;
      if (left + tooltip.width > window.innerWidth - 8) {
        left = window.innerWidth - tooltip.width - 8;
      }
      if (top < 8) {
        // If no room above, show below
        top = trigger.bottom + 8;
      }
      
      setPosition({ top, left });
    }
  }, [isVisible]);

  return (
    <span className="relative inline-flex">
      <button
        ref={triggerRef}
        type="button"
        className="inline-flex items-center justify-center w-4 h-4 ml-1 text-muted-foreground hover:text-foreground transition-colors focus:outline-none focus:ring-2 focus:ring-primary rounded-full"
        onMouseEnter={() => setIsVisible(true)}
        onMouseLeave={() => setIsVisible(false)}
        onFocus={() => setIsVisible(true)}
        onBlur={() => setIsVisible(false)}
        onClick={(e) => {
          e.preventDefault();
          setIsVisible(!isVisible);
        }}
        aria-label="Help"
        aria-describedby={isVisible ? "tooltip-content" : undefined}
      >
        {children || <HelpCircle className="w-4 h-4" />}
      </button>
      
      {isVisible && (
        <div
          ref={tooltipRef}
          id="tooltip-content"
          role="tooltip"
          className="fixed z-[100] px-3 py-2 text-sm bg-popover text-popover-foreground border border-border rounded-lg shadow-lg max-w-xs"
          style={{ top: `${position.top}px`, left: `${position.left}px` }}
        >
          {content}
        </div>
      )}
    </span>
  );
}

interface FieldLabelProps {
  label: string;
  tooltip: string;
  required?: boolean;
}

export function FieldLabel({ label, tooltip, required }: FieldLabelProps) {
  return (
    <label className="block text-sm font-medium mb-2">
      {label}
      {required && <span className="text-destructive ml-1">*</span>}
      <Tooltip content={tooltip} />
    </label>
  );
}
