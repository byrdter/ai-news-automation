'use client'

import { Suspense } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { ArticleList } from '@/components/articles/ArticleList'
import { ArticleFilters } from '@/components/articles/ArticleFilters'
import { ArticleSearch } from '@/components/articles/ArticleSearch'
import { useArticleCount } from '@/hooks/useArticleCount'

export default function ArticlesPage() {
  const { displayCount } = useArticleCount()
  
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Articles</h1>
            <p className="text-gray-600 mt-1">
              {displayCount} AI-analyzed articles with semantic search and filtering
            </p>
          </div>
        </div>

        <div className="flex flex-col lg:flex-row gap-6">
          <div className="lg:w-64 space-y-4">
            <Suspense fallback={<div>Loading filters...</div>}>
              <ArticleFilters />
            </Suspense>
          </div>

          <div className="flex-1 space-y-6">
            <Suspense fallback={<div>Loading search...</div>}>
              <ArticleSearch />
            </Suspense>

            <Suspense fallback={<div>Loading articles...</div>}>
              <ArticleList />
            </Suspense>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}