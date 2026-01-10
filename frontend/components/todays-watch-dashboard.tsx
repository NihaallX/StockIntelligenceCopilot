"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { AlertCircle, TrendingDown, AlertTriangle, Info, HelpCircle, RefreshCw } from "lucide-react"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"

interface TodaysWatchItem {
  ticker: string
  tags: string[]
  one_line: string
  severity: "watch" | "caution" | "alert"
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// VWAP explanation component
function VWAPExplainer() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="mb-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
      >
        <HelpCircle className="h-4 w-4" />
        What is VWAP?
      </button>
      
      {isOpen && (
        <Card className="mt-2 border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <h3 className="font-semibold text-blue-900 mb-2">VWAP = Volume Weighted Average Price</h3>
            <div className="text-sm text-blue-900 space-y-2">
              <p>
                <strong>Think of it as the "fair price"</strong> for a stock today based on where most trading happened.
              </p>
              
              <div className="space-y-1 ml-4">
                <p>• <strong>Price ABOVE VWAP</strong> → Stock is expensive right now (buyers are strong)</p>
                <p>• <strong>Price AT VWAP</strong> → Stock is at fair value (decision point)</p>
                <p>• <strong>Price BELOW VWAP</strong> → Stock is cheap right now (sellers are strong)</p>
              </div>
              
              <p className="pt-2">
                <strong>Why it matters:</strong> When price bounces off VWAP or breaks through it with high volume,
                it often signals a good entry or exit opportunity.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Helper to simplify tags
function simplifyTag(tag: string): string {
  const tagMap: Record<string, string> = {
    "vwap_bounce": "Bouncing at Fair Price",
    "vwap_rejection": "Rejected at Fair Price",
    "breakdown": "Breaking Down",
    "breakout": "Breaking Up",
    "high_volume": "High Trading Volume",
    "weakness": "Showing Weakness",
    "extended": "Overextended"
  }
  return tagMap[tag.toLowerCase()] || tag
}

// Helper to add actionable advice
function getActionableAdvice(tags: string[], severity: string): string {
  const hasBreakout = tags.some(t => t.toLowerCase().includes("breakout"))
  const hasBounce = tags.some(t => t.toLowerCase().includes("bounce"))
  const hasRejection = tags.some(t => t.toLowerCase().includes("rejection"))
  const hasBreakdown = tags.some(t => t.toLowerCase().includes("breakdown"))
  
  if (severity === "alert") {
    if (hasBreakdown) return "⚠️ Consider selling or avoiding - price is breaking down with volume"
    if (hasRejection) return "⚠️ Watch carefully - price is being rejected at key level"
    return "⚠️ Pay attention - significant move detected"
  }
  
  if (severity === "caution") {
    if (hasRejection) return "⚡ Wait and watch - sellers are pushing price down"
    if (hasBreakout) return "⚡ Potential buy - price breaking above with strength"
    return "⚡ Be cautious - mixed signals"
  }
  
  // watch
  if (hasBounce) return "👀 Could be entry point - price bouncing off support"
  if (hasBreakout) return "👀 Shows strength - price breaking higher"
  return "👀 Monitor - interesting setup forming"
}

export default function TodaysWatchDashboard() {
  const { tokens, handleAuthError } = useAuth()
  const [watchList, setWatchList] = useState<TodaysWatchItem[]>([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true)

  // Auto-refresh every 5 minutes
  useEffect(() => {
    if (tokens?.access_token) {
      fetchTodaysWatch()
    }

    if (tokens?.access_token && autoRefreshEnabled) {
      const interval = setInterval(() => {
        fetchTodaysWatch(true) // true = silent refresh
      }, 5 * 60 * 1000) // 5 minutes

      return () => clearInterval(interval)
    }
  }, [tokens, autoRefreshEnabled])

  const fetchTodaysWatch = async (silent = false) => {
    if (!tokens?.access_token) {
      setError("Authentication required")
      setLoading(false)
      return
    }

    try {
      if (silent) {
        setRefreshing(true)
      } else {
        setLoading(true)
      }
      setError(null)

      const response = await fetch(`${API_URL}/api/v1/intraday/todays-watch?min_severity=watch`, {
        headers: {
          Authorization: `Bearer ${tokens.access_token}`,
        },
      })
      
      if (response.status === 401) {
        // Token expired or invalid
        handleAuthError()
        return
      }
      
      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.statusText}`)
      }

      const data = await response.json()
      setWatchList(data)
      setLastUpdated(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
      console.error("Error fetching today's watch:", err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const handleManualRefresh = () => {
    fetchTodaysWatch(true)
  }

  const formatLastUpdated = (date: Date | null) => {
    if (!date) return "Never"
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return "Just now"
    if (diffMins === 1) return "1 minute ago"
    if (diffMins < 60) return `${diffMins} minutes ago`
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours === 1) return "1 hour ago"
    return `${diffHours} hours ago`
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "alert":
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case "caution":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      default:
        return <Info className="h-5 w-5 text-blue-500" />
    }
  }

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "alert":
        return <Badge variant="error">Alert</Badge>
      case "caution":
        return <Badge variant="warning" className="bg-yellow-500">Caution</Badge>
      default:
        return <Badge variant="info">Watch</Badge>
    }
  }

  if (loading && !refreshing) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Today's Watch</CardTitle>
          <CardDescription>Loading daily overview...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-20 bg-gray-200 rounded-lg"></div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Today's Watch</CardTitle>
              <CardDescription className="text-red-500">Error loading data</CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleManualRefresh}
              disabled={refreshing}
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Try Again
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <p>{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (watchList.length === 0) {
    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Today's Watch</CardTitle>
              <CardDescription>No significant patterns detected today</CardDescription>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-xs text-gray-500">
                Last checked: {formatLastUpdated(lastUpdated)}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualRefresh}
                disabled={refreshing}
                className="gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Checking...' : 'Check Again'}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            <TrendingDown className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>All monitored stocks appear normal.</p>
            <p className="text-sm mt-2">Check back during market hours for updates.</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* VWAP Education */}
      <VWAPExplainer />
      
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Today's Watch</CardTitle>
              <CardDescription>
                Your stocks that need attention today - shown in simple language
              </CardDescription>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-xs text-gray-500">
                Last updated: {formatLastUpdated(lastUpdated)}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={handleManualRefresh}
                disabled={refreshing}
                className="gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
                {refreshing ? 'Refreshing...' : 'Refresh'}
              </Button>
              <Button
                variant={autoRefreshEnabled ? "default" : "outline"}
                size="sm"
                onClick={() => setAutoRefreshEnabled(!autoRefreshEnabled)}
                title={autoRefreshEnabled ? "Auto-refresh ON (every 5 min)" : "Auto-refresh OFF"}
                className="text-xs"
              >
                {autoRefreshEnabled ? '🔄 Auto' : '⏸️ Manual'}
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {refreshing && (
            <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md flex items-center gap-2 text-blue-700">
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span className="text-sm">Updating data...</span>
            </div>
          )}
          
          <div className="space-y-3">
            {watchList.map((item) => (
              <Link 
                key={item.ticker} 
                href={`/dashboard/intraday/${item.ticker}`}
                className="block"
              >
                <Card className="hover:shadow-md transition-shadow cursor-pointer border-l-4"
                  style={{
                    borderLeftColor: 
                      item.severity === "alert" ? "#ef4444" : 
                      item.severity === "caution" ? "#eab308" : 
                      "#3b82f6"
                  }}
                >
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          {getSeverityIcon(item.severity)}
                          <span className="font-semibold text-lg">{item.ticker}</span>
                          {getSeverityBadge(item.severity)}
                        </div>
                        
                        <div className="flex flex-wrap gap-2 mb-3">
                          {item.tags.map((tag, idx) => (
                            <span 
                              key={idx}
                              className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-md font-medium"
                            >
                              {simplifyTag(tag)}
                            </span>
                          ))}
                        </div>
                        
                        {/* Original description */}
                        <p className="text-gray-700 text-sm mb-2">{item.one_line}</p>
                        
                        {/* Actionable advice in simple language */}
                        <div className="bg-gray-50 border-l-2 border-blue-400 pl-3 py-2 text-sm">
                          <p className="text-gray-800 font-medium">
                            {getActionableAdvice(item.tags, item.severity)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Simplified Disclaimer */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-4">
          <div className="flex gap-2 items-start">
            <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-900">
              <p className="font-semibold mb-1">📚 For Learning Only</p>
              <p>
                This system helps you understand what's happening with your stocks. 
                It doesn't tell you to buy or sell - that decision is always yours. 
                We show patterns and context to help you learn.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

