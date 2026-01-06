"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ArrowLeft, TrendingUp, TrendingDown, AlertCircle, Info } from "lucide-react"
import Link from "next/link"

interface StockDetail {
  ticker: string
  explanation: string
  conditional_note: string
  context_badge: {
    labels: string[]
    tooltip: string
  }
  risk_summary: string
  severity: string
  detected_at: string
  current_price: number
  change_pct: number
  vwap: number
  volume_ratio: number
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function IntradayStockDetail() {
  const params = useParams()
  const ticker = params?.ticker as string
  
  const [detail, setDetail] = useState<StockDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (ticker) {
      fetchStockDetail(ticker)
    }
  }, [ticker])

  const fetchStockDetail = async (tickerSymbol: string) => {
    try {
      setLoading(true)
      setError(null)

      const response = await fetch(`${API_URL}/api/v1/intraday/stock/${tickerSymbol}`)
      
      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.statusText}`)
      }

      const data = await response.json()
      setDetail(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error")
      console.error("Error fetching stock detail:", err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error || !detail) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <p>{error || "Stock not found"}</p>
            </div>
            <Link href="/dashboard/intraday" className="mt-4 inline-block text-blue-600">
              ← Back to Today's Watch
            </Link>
          </CardContent>
        </Card>
      </div>
    )
  }

  const isPositive = detail.change_pct >= 0

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/intraday" className="text-gray-600 hover:text-gray-900">
          <ArrowLeft className="h-6 w-6" />
        </Link>
        <div>
          <h1 className="text-3xl font-bold">{detail.ticker}</h1>
          <p className="text-gray-500 text-sm">
            Updated {new Date(detail.detected_at).toLocaleTimeString()}
          </p>
        </div>
      </div>

      {/* Price Card */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-gray-500 mb-1">Current Price</p>
              <p className="text-2xl font-bold">₹{detail.current_price.toFixed(2)}</p>
            </div>
            
            <div>
              <p className="text-sm text-gray-500 mb-1">Today's Change</p>
              <div className="flex items-center gap-2">
                {isPositive ? (
                  <TrendingUp className="h-5 w-5 text-green-600" />
                ) : (
                  <TrendingDown className="h-5 w-5 text-red-600" />
                )}
                <p className={`text-2xl font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                  {detail.change_pct > 0 ? '+' : ''}{detail.change_pct.toFixed(2)}%
                </p>
              </div>
            </div>
            
            <div>
              <p className="text-sm text-gray-500 mb-1">VWAP</p>
              <p className="text-2xl font-bold">₹{detail.vwap.toFixed(2)}</p>
              <p className="text-xs text-gray-500">
                {detail.current_price > detail.vwap ? 'Above' : 'Below'} average
              </p>
            </div>
            
            <div>
              <p className="text-sm text-gray-500 mb-1">Volume</p>
              <p className="text-2xl font-bold">{detail.volume_ratio.toFixed(2)}x</p>
              <p className="text-xs text-gray-500">vs 20-day avg</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Risk Summary */}
      <Card className={
        detail.severity === "alert" ? "border-red-300 bg-red-50" :
        detail.severity === "caution" ? "border-yellow-300 bg-yellow-50" :
        "border-blue-300 bg-blue-50"
      }>
        <CardContent className="p-4">
          <p className="text-lg font-semibold">{detail.risk_summary}</p>
        </CardContent>
      </Card>

      {/* Market Context */}
      {detail.context_badge.labels.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Market Context</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-3">
              {detail.context_badge.labels.map((label, idx) => (
                <Badge key={idx} variant="secondary">
                  {label}
                </Badge>
              ))}
            </div>
            <p className="text-sm text-gray-700">{detail.context_badge.tooltip}</p>
          </CardContent>
        </Card>
      )}

      {/* Explanation */}
      <Card>
        <CardHeader>
          <CardTitle>What We Detected</CardTitle>
          <CardDescription>Pattern analysis for today</CardDescription>
        </CardHeader>
        <CardContent className="prose prose-sm max-w-none">
          <div 
            dangerouslySetInnerHTML={{ 
              __html: detail.explanation.replace(/\n/g, '<br />') 
            }} 
          />
        </CardContent>
      </Card>

      {/* Conditional Note */}
      {detail.conditional_note && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <div className="flex gap-3 items-start">
              <Info className="h-5 w-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-semibold text-blue-900 mb-1">Conditional Note</p>
                <p className="text-sm text-blue-800">{detail.conditional_note}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Disclaimer */}
      <Card className="border-gray-300">
        <CardContent className="p-4">
          <p className="text-xs text-gray-600">
            <strong>Important:</strong> This analysis detects patterns and provides context. 
            It does NOT recommend buying or selling. All language is conditional to support 
            your independent decision-making. Please conduct your own research and consult 
            a financial advisor if needed.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
