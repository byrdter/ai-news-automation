'use client'

import { useState } from 'react'
import { useInfiniteQuery } from '@tanstack/react-query'
import { ArticleCard } from './ArticleCard'
import { Button } from '@/components/ui/button'
import type { ArticleWithSource } from '@/types/database'

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
    }
    if (filters.categories && filters.categories.length > 0) {
      params.set('categories', filters.categories.join(','))
    }
    if (filters.sources && filters.sources.length > 0) {
      params.set('sources', filters.sources.join(','))
    }
    if (filters.dateRange) {
      params.set('start_date', filters.dateRange.start)
      params.set('end_date', filters.dateRange.end)
    }
    if (searchQuery) {
      params.set('search', searchQuery)
    }

    const response = await fetch(`/api/articles?${params}`)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch articles: ${response.status} ${response.statusText}`)
    }

    const result = await response.json()
    
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

  return (
    <div className="space-y-6">
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
      </div>
    </div>
  )
}