'use client';

import React from 'react';
import { GlossaryTerm, getGlossaryTerm, getRelatedTerms } from '@/lib/glossary';

interface TermTooltipProps {
  term: string;
  children: React.ReactNode;
  className?: string;
}

/**
 * TermTooltip Component
 * 
 * Wraps technical terms with a hover tooltip showing beginner-friendly definitions.
 * 
 * Usage:
 * <TermTooltip term="RSI">RSI</TermTooltip>
 * <TermTooltip term="Support">support level</TermTooltip>
 * 
 * Features:
 * - Shows full name (if available)
 * - Plain English definition
 * - Real-world example
 * - Related terms links (future enhancement)
 * - Mobile-friendly (tap to show/hide)
 */
export function TermTooltip({ term, children, className = '' }: TermTooltipProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const definition = getGlossaryTerm(term);
  const tooltipRef = React.useRef<HTMLDivElement>(null);

  // Close tooltip when clicking outside
  React.useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (tooltipRef.current && !tooltipRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  if (!definition) {
    // Term not in glossary - render as plain text
    return <span className={className}>{children}</span>;
  }

  return (
    <span className="relative inline-block" ref={tooltipRef}>
      {/* Trigger */}
      <button
        type="button"
        className={`
          underline decoration-dotted decoration-blue-400 
          hover:decoration-blue-600 
          cursor-help 
          transition-colors
          ${className}
        `}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        onClick={() => setIsOpen(!isOpen)} // Mobile tap support
        aria-label={`Learn about ${term}`}
      >
        {children}
      </button>

      {/* Tooltip Content */}
      {isOpen && (
        <div
          className="
            absolute z-50 
            left-1/2 -translate-x-1/2 
            bottom-full mb-2
            w-80 max-w-[90vw]
            bg-gray-900 
            text-white 
            rounded-lg 
            shadow-xl 
            p-4
            animate-in fade-in zoom-in-95 
            duration-200
            pointer-events-auto
          "
          role="tooltip"
        >
          {/* Arrow */}
          <div className="
            absolute 
            left-1/2 -translate-x-1/2 
            top-full 
            w-0 h-0 
            border-l-[8px] border-l-transparent 
            border-r-[8px] border-r-transparent 
            border-t-[8px] border-t-gray-900
          " />

          {/* Header */}
          <div className="mb-2">
            {definition.fullName ? (
              <>
                <p className="font-bold text-lg">{definition.term}</p>
                <p className="text-sm text-gray-400">{definition.fullName}</p>
              </>
            ) : (
              <p className="font-bold text-lg">{definition.term}</p>
            )}
          </div>

          {/* Definition */}
          <p className="text-sm text-gray-300 mb-3 leading-relaxed">
            {definition.definition}
          </p>

          {/* Example */}
          {definition.example && (
            <div className="bg-gray-800 rounded p-2 mb-2">
              <p className="text-xs text-gray-400 font-semibold mb-1">Example:</p>
              <p className="text-xs text-gray-300 italic leading-relaxed">
                {definition.example}
              </p>
            </div>
          )}

          {/* Category Badge */}
          <div className="flex items-center gap-2 mt-3">
            <span className={`
              text-xs px-2 py-0.5 rounded-full font-medium
              ${definition.category === 'technical' ? 'bg-blue-900 text-blue-200' : ''}
              ${definition.category === 'fundamental' ? 'bg-green-900 text-green-200' : ''}
              ${definition.category === 'risk' ? 'bg-red-900 text-red-200' : ''}
              ${definition.category === 'general' ? 'bg-gray-700 text-gray-300' : ''}
            `}>
              {definition.category}
            </span>

            {/* Related terms count (future: make clickable) */}
            {definition.relatedTerms && definition.relatedTerms.length > 0 && (
              <span className="text-xs text-gray-500">
                +{definition.relatedTerms.length} related
              </span>
            )}
          </div>
        </div>
      )}
    </span>
  );
}

/**
 * InlineGlossary Component
 * 
 * Automatically wraps known technical terms in tooltips within a text block.
 * 
 * Usage:
 * <InlineGlossary>
 *   RSI indicates oversold conditions near support at ₹2,500
 * </InlineGlossary>
 * 
 * Will automatically detect and wrap: RSI, support
 */
interface InlineGlossaryProps {
  children: string;
  className?: string;
}

export function InlineGlossary({ children, className = '' }: InlineGlossaryProps) {
  // Terms to auto-detect (priority order - longer terms first)
  const autoDetectTerms = [
    'Volume Weighted Average Price',
    'Relative Strength Index',
    'Risk/Reward',
    'Position Sizing',
    'Stop Loss',
    'Market Cap',
    'P/E Ratio',
    'Resistance',
    'Volatility',
    'Overbought',
    'Oversold',
    'Breakout',
    'Momentum',
    'Support',
    'Sector',
    'Trend',
    'Range',
    'Volume',
    'VWAP',
    'RSI',
  ];

  let processedText: (string | React.ReactElement)[] = [children];

  // Process each term
  autoDetectTerms.forEach(termToDetect => {
    const newProcessed: (string | React.ReactElement)[] = [];
    
    processedText.forEach((segment, index) => {
      if (typeof segment === 'string') {
        // Case-insensitive regex for whole words
        const regex = new RegExp(`\\b(${termToDetect})\\b`, 'gi');
        const parts = segment.split(regex);
        
        parts.forEach((part, partIndex) => {
          if (part.toLowerCase() === termToDetect.toLowerCase()) {
            // This is the term - wrap it
            const glossaryKey = Object.keys(TECHNICAL_GLOSSARY).find(
              key => TECHNICAL_GLOSSARY[key].term.toLowerCase() === termToDetect.toLowerCase() ||
                     TECHNICAL_GLOSSARY[key].fullName?.toLowerCase() === termToDetect.toLowerCase()
            );
            
            if (glossaryKey) {
              newProcessed.push(
                <TermTooltip key={`${index}-${partIndex}`} term={glossaryKey}>
                  {part}
                </TermTooltip>
              );
            } else {
              newProcessed.push(part);
            }
          } else if (part) {
            // Regular text
            newProcessed.push(part);
          }
        });
      } else {
        // Already a React element - keep it
        newProcessed.push(segment);
      }
    });
    
    processedText = newProcessed;
  });

  return <span className={className}>{processedText}</span>;
}

// Import glossary for InlineGlossary component
import { TECHNICAL_GLOSSARY } from '@/lib/glossary';
