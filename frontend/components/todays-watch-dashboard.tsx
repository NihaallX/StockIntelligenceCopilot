"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { AlertCircle, TrendingDown, AlertTriangle, Info } from "lucide-react"
import Link from "next/link"

interface TodaysWatchItem {
  ticker: string
  tags: string[]
  one_line: string
  severity: "watch" | "caution" | "alert"
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function TodaysWatchDashboard() {
  const [watchList, setWatchList] = useState<TodaysWatchItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchTodaysWatch()
  }, [])

  const fetchTodaysWatch = async () => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API_URL}/api/v1/intraday/todays-watch?min_severity=watch`)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.statusText}`)
      }

      const data = await response.json()
      setWatchList(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
      console.error("Error fetching today's watch:", err)
    } finally {
      setLoading(false)
    }
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
        return <Badge variant="destructive">Alert</Badge>
      case "caution":
        return <Badge variant="default" className="bg-yellow-500">Caution</Badge>
      default:
        return <Badge variant="secondary">Watch</Badge>
    }
  }

  if (loading) {
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
          <CardTitle>Today's Watch</CardTitle>
          <CardDescription className="text-red-500">Error loading data</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <p>{error}</p>
          </div>
          <button
            onClick={fetchTodaysWatch}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Retry
          </button>
        </CardContent>
      </Card>
    )
  }

  if (watchList.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Today's Watch</CardTitle>
          <CardDescription>No significant patterns detected today</CardDescription>
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
      <Card>
        <CardHeader>
          <CardTitle>Today's Watch</CardTitle>
          <CardDescription>
            Stocks flagged for weakness, extended moves, or portfolio risk
          </CardDescription>
        </CardHeader>
        <CardContent>
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
                        
                        <div className="flex flex-wrap gap-2 mb-2">
                          {item.tags.map((tag, idx) => (
                            <span 
                              key={idx}
                              className="text-sm px-2 py-1 bg-gray-100 rounded-md"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                        
                        <p className="text-gray-700 text-sm">{item.one_line}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Disclaimer */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="p-4">
          <div className="flex gap-2 items-start">
            <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-900">
              <p className="font-semibold mb-1">Conditional Analysis Only</p>
              <p>
                This system detects patterns and provides context. It does not recommend 
                trades or predict outcomes. All language is conditional ("if", "may") to 
                support your decision-making process.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
