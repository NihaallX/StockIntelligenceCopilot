'use client';

import React from 'react';
import { TermTooltip, InlineGlossary } from '@/components/TermTooltip';
import { TECHNICAL_GLOSSARY, getTermsByCategory } from '@/lib/glossary';

/**
 * Glossary Demo Page
 * 
 * Demonstrates the beginner education layer with interactive tooltips.
 * Shows how technical terms are explained in plain English.
 */
export default function GlossaryDemoPage() {
  const [selectedCategory, setSelectedCategory] = React.useState<'all' | 'technical' | 'fundamental' | 'risk' | 'general'>('all');

  const filteredTerms = selectedCategory === 'all' 
    ? Object.values(TECHNICAL_GLOSSARY)
    : getTermsByCategory(selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Beginner Education Layer
          </h1>
          <p className="text-gray-600">
            Hover over or tap technical terms to see plain English explanations
          </p>
        </div>

        {/* Example Analysis (with tooltips) */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Example Analysis (Interactive)
          </h2>
          
          <div className="space-y-4 text-gray-700 leading-relaxed">
            <p>
              <span className="font-semibold">RELIANCE.NS Analysis:</span> <TermTooltip term="RSI">RSI</TermTooltip> at 28 
              indicates <TermTooltip term="Oversold">oversold</TermTooltip> conditions. Price testing{' '}
              <TermTooltip term="Support">support</TermTooltip> at ₹2,500 with{' '}
              <TermTooltip term="Volume">volume</TermTooltip> 2.3x average.
            </p>

            <p>
              Current price (₹2,485) below <TermTooltip term="VWAP">VWAP</TermTooltip> (₹2,550) suggests 
              selling pressure dominated recent trades. However, strong{' '}
              <TermTooltip term="Momentum">momentum</TermTooltip> bounce off support indicates potential reversal.
            </p>

            <p>
              <span className="font-semibold">Setup:</span> Entry at ₹2,500, <TermTooltip term="StopLoss">stop loss</TermTooltip> at 
              ₹2,450 (2% risk), target at ₹2,650 (6% reward) = favorable{' '}
              <TermTooltip term="RiskReward">risk/reward ratio</TermTooltip> of 3:1.
            </p>

            <p className="text-sm text-gray-500 italic">
              Recommended <TermTooltip term="PositionSizing">position sizing</TermTooltip>: 2-3% of portfolio. 
              Monitor <TermTooltip term="Volatility">volatility</TermTooltip> for entry timing.
            </p>
          </div>
        </div>

        {/* Auto-Detection Demo */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Auto-Detection Demo
          </h2>
          
          <p className="text-gray-600 mb-4 text-sm">
            The InlineGlossary component automatically wraps known terms:
          </p>

          <div className="bg-gray-50 rounded p-4 text-gray-700">
            <InlineGlossary>
              TCS showing strong momentum as RSI breaks above 70 (overbought territory). 
              Price broke through resistance at ₹3,700 on high volume. VWAP indicates institutional 
              buying. Consider a breakout entry with a stop loss below support at ₹3,650.
            </InlineGlossary>
          </div>
        </div>

        {/* Category Filter */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Glossary Reference
          </h2>

          <div className="flex flex-wrap gap-2 mb-6">
            {(['all', 'technical', 'fundamental', 'risk', 'general'] as const).map(category => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`
                  px-4 py-2 rounded-lg font-medium transition-colors
                  ${selectedCategory === category 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }
                `}
              >
                {category.charAt(0).toUpperCase() + category.slice(1)} 
                {category !== 'all' && ` (${getTermsByCategory(category).length})`}
              </button>
            ))}
          </div>

          {/* Glossary Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredTerms.map(term => (
              <div key={term.term} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-bold text-lg text-gray-900">{term.term}</h3>
                    {term.fullName && (
                      <p className="text-sm text-gray-500">{term.fullName}</p>
                    )}
                  </div>
                  <span className={`
                    text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap
                    ${term.category === 'technical' ? 'bg-blue-100 text-blue-800' : ''}
                    ${term.category === 'fundamental' ? 'bg-green-100 text-green-800' : ''}
                    ${term.category === 'risk' ? 'bg-red-100 text-red-800' : ''}
                    ${term.category === 'general' ? 'bg-gray-100 text-gray-800' : ''}
                  `}>
                    {term.category}
                  </span>
                </div>

                <p className="text-sm text-gray-700 mb-3">
                  {term.definition}
                </p>

                {term.example && (
                  <div className="bg-gray-50 rounded p-2 mb-2">
                    <p className="text-xs text-gray-500 font-semibold mb-1">Example:</p>
                    <p className="text-xs text-gray-600 italic">
                      {term.example}
                    </p>
                  </div>
                )}

                {term.relatedTerms && term.relatedTerms.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    <span className="text-xs text-gray-500">Related:</span>
                    {term.relatedTerms.map(related => (
                      <span key={related} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                        {related}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Implementation Notes */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-bold text-blue-900 mb-3">
            📚 Implementation Notes
          </h3>
          
          <div className="space-y-2 text-sm text-blue-800">
            <p>
              <strong>Basic Usage:</strong> <code className="bg-blue-100 px-2 py-0.5 rounded">
                &lt;TermTooltip term="RSI"&gt;RSI&lt;/TermTooltip&gt;
              </code>
            </p>
            <p>
              <strong>Auto-Detection:</strong> <code className="bg-blue-100 px-2 py-0.5 rounded">
                &lt;InlineGlossary&gt;Your text here&lt;/InlineGlossary&gt;
              </code>
            </p>
            <p>
              <strong>Terms Covered:</strong> {Object.keys(TECHNICAL_GLOSSARY).length} technical terms 
              (VWAP, RSI, Support, Resistance, Volume, + 15 related)
            </p>
            <p>
              <strong>Mobile Support:</strong> Tap to show/hide tooltips on touchscreens
            </p>
            <p>
              <strong>Categories:</strong> Technical, Fundamental, Risk, General
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
