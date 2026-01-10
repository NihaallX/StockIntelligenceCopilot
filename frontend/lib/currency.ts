/**
 * Currency formatting utilities for Phase 2D
 * 
 * Handles:
 * - Locale-aware number formatting
 * - Currency symbols ($ / ₹)
 * - Explicit currency labels
 * - No silent conversions
 */

export type CurrencyCode = 'USD' | 'INR'

interface CurrencyConfig {
  locale: string
  symbol: string
  name: string
  decimalPlaces: number
}

const CURRENCY_CONFIGS: Record<CurrencyCode, CurrencyConfig> = {
  USD: {
    locale: 'en-US',
    symbol: '$',
    name: 'USD',
    decimalPlaces: 2
  },
  INR: {
    locale: 'en-IN',
    symbol: '₹',
    name: 'INR',
    decimalPlaces: 2
  }
}

/**
 * Format a price with currency symbol
 * Example: formatPrice(1234.56, 'USD') => "$1,234.56"
 */
export function formatPrice(price: number, currency: CurrencyCode = 'USD'): string {
  const config = CURRENCY_CONFIGS[currency]
  
  const formatter = new Intl.NumberFormat(config.locale, {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: config.decimalPlaces,
    maximumFractionDigits: config.decimalPlaces
  })
  
  return formatter.format(price)
}

/**
 * Format a large number with currency (e.g., market cap)
 * Example: formatLargeNumber(1234567890, 'USD') => "$1.23B"
 */
export function formatLargeNumber(value: number, currency: CurrencyCode = 'USD'): string {
  const config = CURRENCY_CONFIGS[currency]
  const absValue = Math.abs(value)
  
  let formatted: string
  
  if (absValue >= 1e12) {
    formatted = (value / 1e12).toFixed(2) + 'T'
  } else if (absValue >= 1e9) {
    formatted = (value / 1e9).toFixed(2) + 'B'
  } else if (absValue >= 1e6) {
    formatted = (value / 1e6).toFixed(2) + 'M'
  } else if (absValue >= 1e3) {
    formatted = (value / 1e3).toFixed(2) + 'K'
  } else {
    formatted = value.toFixed(config.decimalPlaces)
  }
  
  return `${config.symbol}${formatted}`
}

/**
 * Format percentage change
 * Example: formatPercentage(5.67) => "+5.67%"
 */
export function formatPercentage(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

/**
 * Format with explicit currency label (for mixed-currency views)
 * Example: formatWithLabel(1234.56, 'INR') => "₹1,234.56 INR"
 */
export function formatWithLabel(value: number, currency: CurrencyCode): string {
  const formatted = formatPrice(value, currency)
  const config = CURRENCY_CONFIGS[currency]
  return `${formatted} ${config.name}`
}

/**
 * Get currency symbol only
 */
export function getCurrencySymbol(currency: CurrencyCode): string {
  return CURRENCY_CONFIGS[currency].symbol
}

/**
 * Get currency name
 */
export function getCurrencyName(currency: CurrencyCode): string {
  return CURRENCY_CONFIGS[currency].name
}

/**
 * Format plain number without currency
 * Example: formatNumber(1234.56, 'INR') => "1,234.56"
 */
export function formatNumber(value: number, currency: CurrencyCode = 'USD'): string {
  const config = CURRENCY_CONFIGS[currency]
  
  const formatter = new Intl.NumberFormat(config.locale, {
    minimumFractionDigits: config.decimalPlaces,
    maximumFractionDigits: config.decimalPlaces
  })
  
  return formatter.format(value)
}

/**
 * Get color class for percentage change
 */
export function getChangeColor(value: number): string {
  if (value > 0) return 'text-green-600'
  if (value < 0) return 'text-red-600'
  return 'text-gray-600'
}
