"use client"

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Search, X, TrendingUp } from 'lucide-react'

export interface TickerResult {
  ticker: string
  company_name: string
  exchange: 'NYSE' | 'NASDAQ' | 'NSE' | 'BSE'
  country: 'US' | 'IN'
  currency: 'USD' | 'INR'
  sector?: string
  industry?: string
  ticker_format: string
  is_supported: boolean
}

interface TickerSearchProps {
  onSelect: (ticker: TickerResult) => void
  placeholder?: string
  initialValue?: string
  country?: 'US' | 'IN'
  className?: string
}

export function TickerSearch({
  onSelect,
  placeholder = "Search stocks (e.g., AAPL, Microsoft)...",
  initialValue = "",
  country,
  className = ""
}: TickerSearchProps) {
  const [query, setQuery] = useState(initialValue)
  const [results, setResults] = useState<TickerResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [error, setError] = useState<string | null>(null)
  
  const inputRef = useRef<HTMLInputElement>(null)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const debounceTimer = useRef<NodeJS.Timeout | null>(null)

  // Debounced search
  const searchTickers = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 1) {
      setResults([])
      setIsOpen(false)
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      // Note: This component is not currently used. 
      // Autocomplete is implemented directly in analysis page using frontend-only list.
      setResults([])
      setError('Search unavailable - use inline autocomplete')
    } catch (err) {
      console.error('Ticker search error:', err)
      setError('Search unavailable')
      setResults([])
    } finally {
      setIsLoading(false)
    }
  }, [country])

  // Handle input change with debounce
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setQuery(value)

    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }

    debounceTimer.current = setTimeout(() => {
      searchTickers(value)
    }, 300)
  }

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((prev) => (prev + 1) % results.length)
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((prev) => (prev - 1 + results.length) % results.length)
        break
      case 'Enter':
        e.preventDefault()
        if (results[selectedIndex]) {
          handleSelect(results[selectedIndex])
        }
        break
      case 'Escape':
        e.preventDefault()
        setIsOpen(false)
        break
    }
  }

  // Handle selection
  const handleSelect = (ticker: TickerResult) => {
    setQuery(ticker.ticker)
    setIsOpen(false)
    onSelect(ticker)
  }

  // Handle clear
  const handleClear = () => {
    setQuery('')
    setResults([])
    setIsOpen(false)
    inputRef.current?.focus()
  }

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Exchange badge color
  const getExchangeBadgeColor = (exchange: string) => {
    switch (exchange) {
      case 'NYSE':
      case 'NASDAQ':
        return 'bg-blue-100 text-blue-700 border-blue-200'
      case 'NSE':
      case 'BSE':
        return 'bg-orange-100 text-orange-700 border-orange-200'
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200'
    }
  }

  // Country flag
  const getCountryFlag = (countryCode: string) => {
    return countryCode === 'US' ? '🇺🇸' : countryCode === 'IN' ? '🇮🇳' : countryCode
  }

  return (
    <div className={`relative ${className}`}>
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all"
          autoComplete="off"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        )}
        {isLoading && (
          <div className="absolute right-10 top-1/2 -translate-y-1/2">
            <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
          </div>
        )}
      </div>

      {/* Dropdown Results */}
      {isOpen && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-y-auto"
        >
          {error ? (
            <div className="p-4 text-center text-red-600">
              {error}
            </div>
          ) : results.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              No results found for "{query}"
            </div>
          ) : (
            <ul className="py-1">
              {results.map((result, index) => (
                <li key={`${result.ticker}-${result.exchange}`}>
                  <button
                    onClick={() => handleSelect(result)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors ${
                      index === selectedIndex ? 'bg-blue-50' : ''
                    }`}
                    onMouseEnter={() => setSelectedIndex(index)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-semibold text-gray-900">
                            {result.ticker}
                          </span>
                          <span
                            className={`px-2 py-0.5 text-xs font-medium rounded border ${getExchangeBadgeColor(
                              result.exchange
                            )}`}
                          >
                            {result.exchange}
                          </span>
                          <span className="text-sm">
                            {getCountryFlag(result.country)}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600 truncate">
                          {result.company_name}
                        </div>
                        {result.sector && (
                          <div className="text-xs text-gray-500 mt-1">
                            {result.sector}
                            {result.industry && ` • ${result.industry}`}
                          </div>
                        )}
                      </div>
                      <div className="ml-3 flex items-center text-gray-400">
                        <TrendingUp className="h-4 w-4" />
                      </div>
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
