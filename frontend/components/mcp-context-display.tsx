/**
 * MCP Context Display Components
 * 
 * Frontend UI components for displaying Market Context Protocol (MCP) enrichment
 * in the Stock Intelligence Copilot dashboard.
 * 
 * Components:
 * 1. ContextBadge - Shows confidence level
 * 2. CitationPanel - Displays supporting sources
 * 3. ContextSummary - Shows context summary
 * 4. EmptyContextState - Graceful empty state
 */

import React from 'react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { ExternalLink, CheckCircle, AlertCircle, Info, ChevronDown } from 'lucide-react';

// Type definitions matching backend models
interface CitationSource {
  title: string;
  publisher: string;
  url: string;
  published_at?: string;
}

interface SupportingPoint {
  claim: string;
  sources: CitationSource[];
  confidence: 'high' | 'medium' | 'low';
  relevance_score: number;
}

interface MarketContext {
  context_summary: string;
  supporting_points: SupportingPoint[];
  data_sources_used: string[];
  disclaimer: string;
  enriched_at: string;
  mcp_status: 'success' | 'partial' | 'failed';
  failure_reason?: string;
}

/**
 * Context Confidence Badge
 * Displays the confidence level with appropriate styling
 */
export function ContextBadge({ confidence }: { confidence: 'high' | 'medium' | 'low' }) {
  const variants = {
    high: { icon: CheckCircle, variant: 'success' as const, label: 'Verified' },
    medium: { icon: Info, variant: 'info' as const, label: 'Supported' },
    low: { icon: AlertCircle, variant: 'warning' as const, label: 'Limited' }
  };
  
  const { icon: Icon, variant, label } = variants[confidence];
  
  return (
    <Badge variant={variant} className="flex items-center gap-1">
      <Icon className="w-3 h-3" />
      {label}
    </Badge>
  );
}

/**
 * Citation Source Display
 * Shows individual citation with publisher, title, and link
 */
function CitationItem({ source }: { source: CitationSource }) {
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-IN', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  return (
    <div className="border-l-2 border-blue-200 pl-3 py-2 hover:bg-gray-50 transition-colors">
      <a 
        href={source.url} 
        target="_blank" 
        rel="noopener noreferrer"
        className="text-blue-600 hover:text-blue-800 font-medium flex items-start gap-2 group"
      >
        <span className="flex-1">{source.title}</span>
        <ExternalLink className="w-4 h-4 flex-shrink-0 mt-1 opacity-0 group-hover:opacity-100 transition-opacity" />
      </a>
      <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
        <span className="font-semibold">{source.publisher}</span>
        {formatDate(source.published_at) && (
          <>
            <span>•</span>
            <span>{formatDate(source.published_at)}</span>
          </>
        )}
      </div>
    </div>
  );
}

/**
 * Supporting Point Display
 * Shows a claim with its sources and confidence
 */
function SupportingPointCard({ point }: { point: SupportingPoint }) {
  const [isOpen, setIsOpen] = React.useState(false);
  
  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <Card className="mb-3">
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-gray-50 transition-colors py-3">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <ContextBadge confidence={point.confidence} />
                  <span className="text-xs text-gray-500">
                    {point.sources.length} source{point.sources.length !== 1 ? 's' : ''}
                  </span>
                </div>
                <CardTitle className="text-sm font-normal text-gray-700">
                  {point.claim}
                </CardTitle>
              </div>
              <ChevronDown 
                className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
              />
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        
        <CollapsibleContent>
          <CardContent className="pt-0 pb-3 space-y-2">
            {point.sources.map((source, idx) => (
              <CitationItem key={idx} source={source} />
            ))}
          </CardContent>
        </CollapsibleContent>
      </Card>
    </Collapsible>
  );
}

/**
 * Main Context Panel
 * Complete MCP context display with summary and citations
 */
export function MCPContextPanel({ context }: { context: MarketContext | null | undefined }) {
  // Empty state
  if (!context) {
    return null;
  }
  
  // Failure state
  if (context.mcp_status === 'failed' || context.failure_reason === 'no_supporting_news') {
    return (
      <Alert variant="default" className="bg-yellow-50 border-yellow-200">
        <AlertCircle className="h-4 w-4 text-yellow-600" />
        <AlertTitle className="text-yellow-800">No Supporting Context Found</AlertTitle>
        <AlertDescription className="text-yellow-700">
          {context.failure_reason === 'no_supporting_news' 
            ? "No recent news or market context available for this stock. This movement may be speculative or based on market-wide factors."
            : "Market context temporarily unavailable. Analysis is based on technical indicators only."}
        </AlertDescription>
      </Alert>
    );
  }
  
  // Success/Partial state
  return (
    <Card className="border-blue-200 bg-blue-50/30">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Market Context</CardTitle>
          <div className="flex items-center gap-2">
            {context.mcp_status === 'partial' && (
              <Badge variant="warning">
                Partial Data
              </Badge>
            )}
            <span className="text-xs text-gray-500">
              {context.data_sources_used.join(', ')}
            </span>
          </div>
        </div>
        <CardDescription className="text-gray-700 mt-2">
          {context.context_summary}
        </CardDescription>
      </CardHeader>
      
      {context.supporting_points && context.supporting_points.length > 0 && (
        <CardContent>
          <h4 className="text-sm font-semibold text-gray-600 mb-3">Supporting Evidence</h4>
          <div className="space-y-0">
            {context.supporting_points.map((point, idx) => (
              <SupportingPointCard key={idx} point={point} />
            ))}
          </div>
          
          <Alert variant="default" className="mt-4 bg-gray-50 border-gray-200">
            <Info className="h-4 w-4" />
            <AlertDescription className="text-xs text-gray-600">
              {context.disclaimer}
            </AlertDescription>
          </Alert>
        </CardContent>
      )}
    </Card>
  );
}

/**
 * Compact Context Badge (for signal cards)
 * Minimal display for use in signal/opportunity cards
 */
export function CompactContextBadge({ 
  context 
}: { 
  context: MarketContext | null | undefined 
}) {
  if (!context || context.mcp_status === 'failed') {
    return null;
  }
  
  const hasHighConfidence = context.supporting_points?.some(p => p.confidence === 'high');
  const sourceCount = context.supporting_points?.reduce((acc, p) => acc + p.sources.length, 0) || 0;
  
  return (
    <div className="flex items-center gap-2 text-xs">
      {hasHighConfidence ? (
        <ContextBadge confidence="high" />
      ) : (
        <ContextBadge confidence="medium" />
      )}
      <span className="text-gray-500">
        {sourceCount} citation{sourceCount !== 1 ? 's' : ''}
      </span>
    </div>
  );
}

/**
 * Usage Example:
 * 
 * import { MCPContextPanel, CompactContextBadge } from '@/components/mcp-context-display';
 * 
 * // In your signal/opportunity card:
 * <CompactContextBadge context={signal.market_context} />
 * 
 * // In detailed view:
 * <MCPContextPanel context={signal.market_context} />
 */
