'use client'

import { useQuery } from '@tanstack/react-query'

async function fetchRecentArticleCount(): Promise<{ count: number; date: string }> {
  try {
    // First, get the most recent article to find the latest date
    const recentResponse = await fetch('/api/articles?page=0&limit=1')
    if (!recentResponse.ok) {
      throw new Error(`HTTP ${recentResponse.status}`)
    }
    const recentResult = await recentResponse.json()
    
    if (!recentResult.articles?.[0]) {
      return { count: 0, date: 'today' }
    }
    
    // Get the date of the most recent article
    const mostRecentDate = recentResult.articles[0].published_at.split('T')[0]
    const nextDay = new Date(mostRecentDate)
    nextDay.setDate(nextDay.getDate() + 1)
    const nextDayStr = nextDay.toISOString().split('T')[0]
    
    // Count articles from that date
    const countResponse = await fetch(`/api/articles?start_date=${mostRecentDate}&end_date=${nextDayStr}&page=0&limit=1`)
    if (!countResponse.ok) {
      throw new Error(`HTTP ${countResponse.status}`)
    }
    const countResult = await countResponse.json()
    
    // Check if this is actually today
    const today = new Date().toISOString().split('T')[0]
    const isToday = mostRecentDate === today
    const dateLabel = isToday ? 'today' : 'latest'
    
    return { 
      count: countResult.pagination?.total || 0,
      date: dateLabel
    }
  } catch (error) {
    console.error('Error fetching recent article count:', error)
    return { count: 0, date: 'today' }
  }
}

export function useTodayArticleCount() {
  const { data = { count: 0, date: 'today' }, isLoading } = useQuery({
    queryKey: ['recent-article-count'],
    queryFn: fetchRecentArticleCount,
    staleTime: 2 * 60 * 1000, // Cache for 2 minutes (more frequent updates)
    enabled: typeof window !== 'undefined', // Only run client-side
  })

  return {
    count: data.count,
    isLoading,
    dateLabel: data.date,
  }
}