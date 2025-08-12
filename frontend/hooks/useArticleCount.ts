'use client'

import { useQuery } from '@tanstack/react-query'

async function fetchArticleCount(): Promise<number> {
  try {
    const response = await fetch('/api/articles?page=0&limit=1')
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    const result = await response.json()
    return result.pagination?.total || 0
  } catch (error) {
    console.error('Error fetching article count:', error)
    return 0
  }
}

export function useArticleCount() {
  const { data: count = 0, isLoading } = useQuery({
    queryKey: ['article-count'],
    queryFn: fetchArticleCount,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    enabled: typeof window !== 'undefined', // Only run client-side
  })

  return {
    count,
    isLoading,
    displayCount: count > 0 ? `${count}+` : '0+' // No hardcoded fallback
  }
}