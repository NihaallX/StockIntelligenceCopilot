import { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp, Calendar, Building2 } from 'lucide-react';
import { SupportingPoint } from '@/lib/api';
import { ConfidenceBadge } from './ConfidenceBadge';

interface CitationsPanelProps {
  supportingPoints: SupportingPoint[];
  className?: string;
}

export function CitationsPanel({ supportingPoints, className = '' }: CitationsPanelProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-IN', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    } catch {
      return null;
    }
  };

  if (!supportingPoints || supportingPoints.length === 0) {
    return null;
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {supportingPoints.map((point, index) => {
        const isExpanded = expandedIndex === index;
        const hasMultipleSources = point.sources && point.sources.length > 1;

        return (
          <div
            key={index}
            className="p-4 bg-background border border-border rounded-lg hover:border-primary/30 transition-all"
          >
            {/* Claim header */}
            <div className="flex items-start justify-between gap-3 mb-2">
              <div className="flex-1">
                <p className="text-sm font-medium leading-relaxed">{point.claim}</p>
              </div>
              <div className="flex-shrink-0">
                <ConfidenceBadge level={point.confidence} />
              </div>
            </div>

            {/* First source (always visible) */}
            {point.sources && point.sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-border">
                <div className="space-y-2">
                  <CitationItem source={point.sources[0]} formatDate={formatDate} />
                  
                  {/* Show/Hide button for additional sources */}
                  {hasMultipleSources && (
                    <button
                      onClick={() => toggleExpand(index)}
                      className="flex items-center gap-1.5 text-xs text-primary hover:text-primary/80 transition-colors mt-2"
                    >
                      {isExpanded ? (
                        <>
                          <ChevronUp className="w-3.5 h-3.5" />
                          Hide {point.sources.length - 1} more source{point.sources.length - 1 !== 1 ? 's' : ''}
                        </>
                      ) : (
                        <>
                          <ChevronDown className="w-3.5 h-3.5" />
                          Show {point.sources.length - 1} more source{point.sources.length - 1 !== 1 ? 's' : ''}
                        </>
                      )}
                    </button>
                  )}

                  {/* Additional sources (expandable) */}
                  {isExpanded && point.sources.slice(1).map((source, i) => (
                    <div key={i} className="pt-2 border-t border-border/50">
                      <CitationItem source={source} formatDate={formatDate} />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Relevance score (debug info - can be hidden in production) */}
            {point.relevance_score !== undefined && (
              <div className="mt-2 text-xs text-muted-foreground">
                Relevance: {(point.relevance_score * 100).toFixed(0)}%
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

interface CitationItemProps {
  source: {
    title: string;
    publisher: string;
    url: string;
    published_at?: string;
  };
  formatDate: (dateString?: string) => string | null;
}

function CitationItem({ source, formatDate }: CitationItemProps) {
  const formattedDate = formatDate(source.published_at);

  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 mt-1">
        <Building2 className="w-4 h-4 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm font-medium text-primary hover:text-primary/80 hover:underline transition-colors line-clamp-2 block"
        >
          {source.title}
        </a>
        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
          <span className="font-medium">{source.publisher}</span>
          {formattedDate && (
            <>
              <span>•</span>
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                <span>{formattedDate}</span>
              </div>
            </>
          )}
          <span>•</span>
          <a
            href={source.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 hover:text-primary transition-colors"
          >
            View source
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
}
