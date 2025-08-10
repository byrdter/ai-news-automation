'use client'

import { useState, useEffect } from 'react'
import { useInfiniteQuery, useQueryClient } from '@tanstack/react-query'
import { ArticleCard } from './ArticleCard'
import { Button } from '@/components/ui/button'
import type { ArticleWithSource } from '@/types/database'
import type { FilterState } from './ArticleFilters'

interface ArticleFilters {
  categories?: string[]
  sources?: string[]
  minRelevance?: number
  dateRange?: {
    start: string
    end: string
  }
  searchQuery?: string
}

interface ArticlesResponse {
  data: ArticleWithSource[]
  nextCursor?: number
  hasMore: boolean
}

function convertFilterStateToArticleFilters(filterState: FilterState): ArticleFilters {
  const filters: ArticleFilters = {}
  
  if (filterState.categories && filterState.categories.length > 0) {
    filters.categories = filterState.categories
    console.log('Added categories filter:', filterState.categories)
  }
  
  if (filterState.sources && filterState.sources.length > 0) {
    filters.sources = filterState.sources  
    console.log('Added sources filter:', filterState.sources)
  }
  
  if (filterState.minRelevance && filterState.minRelevance > 0) {
    filters.minRelevance = filterState.minRelevance
    console.log('Added relevance filter:', filterState.minRelevance)
  }
  
  // Convert date range to actual dates
  if (filterState.dateRange && filterState.dateRange !== 'all') {
    const now = new Date()
    const start = new Date()
    
    switch (filterState.dateRange) {
      case '24h':
        start.setDate(now.getDate() - 1)
        break
      case '7d':
        start.setDate(now.getDate() - 7)
        break
      case '30d':
        start.setDate(now.getDate() - 30)
        break
    }
    
    filters.dateRange = {
      start: start.toISOString(),
      end: now.toISOString()
    }
    console.log('Added date range filter:', filterState.dateRange, filters.dateRange)
  }
  
  console.log('Final converted filters:', filters)
  return filters
}

async function fetchArticles(
  page: number = 0,
  filters: ArticleFilters = {},
  searchQuery: string = ''
): Promise<ArticlesResponse> {
  try {
    // Build query parameters
    const params = new URLSearchParams()
    
    // Pagination
    params.set('page', page.toString())
    params.set('limit', '20')
    
    // Filters
    if (filters.minRelevance) {
      params.set('min_relevance', filters.minRelevance.toString())
      console.log('Adding min_relevance param:', filters.minRelevance.toString())
    }
    if (filters.categories && filters.categories.length > 0) {
      params.set('categories', filters.categories.join(','))
      console.log('Adding categories param:', filters.categories.join(','))
    }
    if (filters.sources && filters.sources.length > 0) {
      params.set('sources', filters.sources.join(','))
      console.log('Adding sources param:', filters.sources.join(','))
    }
    if (filters.dateRange) {
      params.set('start_date', filters.dateRange.start)
      params.set('end_date', filters.dateRange.end)
      console.log('Adding date range params:', filters.dateRange)
    }
    if (searchQuery) {
      params.set('search', searchQuery)
      console.log('Adding search param:', searchQuery)
    }

    const url = `/api/articles?${params}`
    console.log('Fetching articles with URL:', url)
    console.log('Full params object:', Object.fromEntries(params))

    const response = await fetch(url)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch articles: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    console.log('API response:', result)
    
    return {
      data: result.articles || [],
      nextCursor: result.hasMore ? page + 1 : undefined,
      hasMore: result.hasMore || false
    }
  } catch (error) {
    console.error('Error fetching articles:', error)
    throw error
  }
}

export function ArticleList() {
  const [filters, setFilters] = useState<ArticleFilters>({})
  const [searchQuery, setSearchQuery] = useState('')
  const queryClient = useQueryClient()

  // Listen for filter changes from ArticleFilters component
  useEffect(() => {
    const handleFiltersChanged = (event: CustomEvent) => {
      const filterState = event.detail as FilterState
      const convertedFilters = convertFilterStateToArticleFilters(filterState)
      console.log('Filter changed:', filterState, 'Converted:', convertedFilters)
      setFilters(convertedFilters)
    }

    const handleSearchResults = (event: CustomEvent) => {
      const { query } = event.detail
      console.log('Search query changed:', query)
      setSearchQuery(query || '')
    }

    window.addEventListener('filtersChanged', handleFiltersChanged as EventListener)
    window.addEventListener('searchResults', handleSearchResults as EventListener)

    return () => {
      window.removeEventListener('filtersChanged', handleFiltersChanged as EventListener)
      window.removeEventListener('searchResults', handleSearchResults as EventListener)
    }
  }, [])

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error
  } = useInfiniteQuery({
    queryKey: ['articles', filters, searchQuery],
    queryFn: ({ pageParam = 0 }) => fetchArticles(pageParam, filters, searchQuery),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: 0,
  })

  // Invalidate and refetch when filters or search change to ensure clean data
  useEffect(() => {
    if (Object.keys(filters).length > 0 || searchQuery) {
      console.log('Invalidating query due to filter/search change')
      queryClient.invalidateQueries({ queryKey: ['articles'] })
    }
  }, [filters, searchQuery, queryClient])

  const articles = data?.pages.flatMap(page => page.data) ?? []

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-100 rounded w-1/2 mb-4"></div>
              <div className="h-3 bg-gray-100 rounded w-full mb-2"></div>
              <div className="h-3 bg-gray-100 rounded w-2/3"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load articles. Please try again.</p>
      </div>
    )
  }

  if (articles.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No articles found matching your criteria.</p>
      </div>
    )
  }

  const hasActiveFilters = 
    Object.keys(filters).length > 0 && 
    (filters.categories?.length || filters.sources?.length || filters.minRelevance || filters.dateRange || searchQuery)

  return (
    <div className="space-y-6">
      {/* Active Filters Indicator */}
      {hasActiveFilters && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-blue-800">
              <strong>Active filters:</strong>
              {filters.categories?.length && (
                <span className="ml-2">Categories: {filters.categories.length}</span>
              )}
              {filters.sources?.length && (
                <span className="ml-2">Sources: {filters.sources.length}</span>
              )}
              {filters.minRelevance && (
                <span className="ml-2">Min Relevance: {Math.round(filters.minRelevance * 100)}%</span>
              )}
              {searchQuery && (
                <span className="ml-2">Search: "{searchQuery}"</span>
              )}
            </div>
            {(isLoading || isFetchingNextPage) && (
              <div className="text-xs text-blue-600">Filtering...</div>
            )}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

      {hasNextPage && (
        <div className="text-center">
          <Button
            onClick={() => fetchNextPage()}
            disabled={isFetchingNextPage}
            variant="outline"
            size="lg"
          >
            {isFetchingNextPage ? 'Loading...' : 'Load More Articles'}
          </Button>
        </div>
      )}

      <div className="text-center text-sm text-gray-500">
        Showing {articles.length} articles
        {hasActiveFilters && (
          <span className="text-blue-600 ml-2">(filtered)</span>
        )}
      </div>
    </div>
  )
}