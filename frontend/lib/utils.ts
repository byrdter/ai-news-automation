import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(amount)
}

export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function getTimeAgo(date: string | Date): string {
  const now = new Date()
  const then = new Date(date)
  const diffInSeconds = Math.floor((now.getTime() - then.getTime()) / 1000)

  if (diffInSeconds < 60) return 'just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`
  
  return formatDate(date)
}

export function calculateRelevanceColor(score: number): string {
  if (score >= 0.8) return 'text-green-600 bg-green-100'
  if (score >= 0.6) return 'text-yellow-600 bg-yellow-100'
  if (score >= 0.4) return 'text-orange-600 bg-orange-100'
  return 'text-red-600 bg-red-100'
}

export function calculateSentimentColor(score: number): string {
  if (score > 0.1) return 'text-green-600 bg-green-100'
  if (score > -0.1) return 'text-gray-600 bg-gray-100'
  return 'text-red-600 bg-red-100'
}

export function getSentimentLabel(score: number): string {
  if (score > 0.1) return 'Positive'
  if (score > -0.1) return 'Neutral'
  return 'Negative'
}

export function getUrgencyColor(level: string): string {
  switch (level.toLowerCase()) {
    case 'critical': return 'text-red-600 bg-red-100'
    case 'high': return 'text-orange-600 bg-orange-100'
    case 'medium': return 'text-yellow-600 bg-yellow-100'
    case 'low': return 'text-green-600 bg-green-100'
    default: return 'text-gray-600 bg-gray-100'
  }
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}