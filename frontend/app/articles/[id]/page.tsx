'use client'

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { 
  ArrowLeft,
  ExternalLink, 
  Clock, 
  Target, 
  TrendingUp, 
  Eye,
  Share2,
  Bookmark
} from 'lucide-react'
import { formatDate, getTimeAgo } from '@/lib/utils'
import type { ArticleWithSource } from '@/types/database'

async function fetchArticle(id: string): Promise<ArticleWithSource | null> {
  try {
    const response = await fetch(`/api/articles/${id}`)
    if (!response.ok) {
      if (response.status === 404) return null
      throw new Error(`Failed to fetch article: ${response.status}`)
    }
    return response.json()
  } catch (error) {
    console.error('Error fetching article:', error)
    throw error
  }
}

export default function ArticlePage() {
  const params = useParams()
  const router = useRouter()
  const articleId = params.id as string

  const { data: article, isLoading, error } = useQuery({
    queryKey: ['article', articleId],
    queryFn: () => fetchArticle(articleId),
    enabled: !!articleId
  })

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-100 rounded w-1/2 mb-8"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-100 rounded w-full"></div>
              <div className="h-4 bg-gray-100 rounded w-5/6"></div>
              <div className="h-4 bg-gray-100 rounded w-4/5"></div>
            </div>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !article) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Article Not Found</h1>
            <p className="text-gray-600 mb-4">
              The article you're looking for doesn't exist or may have been removed.
            </p>
            <Button onClick={() => router.back()} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go Back
            </Button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Back Navigation */}
        <div className="flex items-center gap-4">
          <Button onClick={() => router.back()} variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Articles
          </Button>
          <nav className="text-sm text-gray-500">
            Articles / {article.source?.name} / {article.title.slice(0, 50)}...
          </nav>
        </div>

        {/* Article Header */}
        <div className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 leading-tight mb-3">
                {article.title}
              </h1>
              
              <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                <div className="flex items-center gap-1">
                  <span className="font-medium">{article.source?.name}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{getTimeAgo(article.published_at)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Eye className="h-4 w-4" />
                  <span>{article.view_count || 0} views</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2 ml-6">
              <Button variant="outline" size="sm">
                <Bookmark className="h-4 w-4 mr-2" />
                Save
              </Button>
              <Button variant="outline" size="sm">
                <Share2 className="h-4 w-4 mr-2" />
                Share
              </Button>
            </div>
          </div>

          {/* Article Metadata */}
          <div className="flex flex-wrap items-center gap-3">
            <Badge 
              variant={article.relevance_score && article.relevance_score > 0.8 ? 'default' : 'secondary'}
              className="flex items-center gap-1"
            >
              <Target className="h-3 w-3" />
              {Math.round((article.relevance_score || 0) * 100)}% Relevance
            </Badge>
            
            {article.sentiment_score !== null && (
              <Badge 
                variant="outline"
                className={
                  article.sentiment_score > 0.1 
                    ? 'border-green-200 text-green-700' 
                    : article.sentiment_score < -0.1
                    ? 'border-red-200 text-red-700'
                    : 'border-gray-200 text-gray-700'
                }
              >
                <TrendingUp className="h-3 w-3 mr-1" />
                {article.sentiment_score > 0.1 ? 'Positive' : 
                 article.sentiment_score < -0.1 ? 'Negative' : 'Neutral'} Sentiment
              </Badge>
            )}
            
            {article.word_count && (
              <Badge variant="outline">
                {article.word_count.toLocaleString()} words
              </Badge>
            )}
            
            <Badge variant="outline" className="text-green-600">
              {article.analysis_model || 'AI Analyzed'}
            </Badge>
          </div>
        </div>

        <Separator />

        {/* Article Content */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-3">
            <Card>
              <CardHeader>
                <CardTitle>Article Content</CardTitle>
              </CardHeader>
              <CardContent>
                {article.summary && (
                  <div className="mb-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
                    <h3 className="font-semibold text-blue-900 mb-2">AI Summary</h3>
                    <p className="text-blue-800 leading-relaxed">{article.summary}</p>
                  </div>
                )}
                
                {article.content ? (
                  <div className="prose prose-gray max-w-none">
                    <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {article.content}
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p className="mb-4">Full content not available. Click below to read the original article.</p>
                  </div>
                )}
                
                {article.url && (
                  <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                    <Button asChild className="w-full">
                      <a href={article.url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Read Original Article
                      </a>
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Article Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Analysis Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Quality Score</span>
                  <span className="font-medium">
                    {Math.round((article.quality_score || 0) * 100)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Urgency Score</span>
                  <span className="font-medium">
                    {Math.round((article.urgency_score || 0) * 100)}%
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Processing Cost</span>
                  <span className="font-medium">
                    ${(article.analysis_cost_usd || 0).toFixed(4)}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Analyzed</span>
                  <span className="font-medium">
                    {article.analysis_timestamp 
                      ? getTimeAgo(article.analysis_timestamp)
                      : 'Unknown'
                    }
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Categories */}
            {article.categories && article.categories.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Categories</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {article.categories.map((category, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {category}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Keywords */}
            {article.keywords && article.keywords.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Keywords</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {article.keywords.map((keyword, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Source Information */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Source Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="text-sm font-medium">{article.source?.name}</div>
                  <div className="text-xs text-gray-600">
                    Tier {article.source?.tier} Source
                  </div>
                </div>
                <div className="text-sm">
                  <span className="text-gray-600">Category:</span>
                  <span className="ml-2 font-medium">{article.source?.category}</span>
                </div>
                {article.author && (
                  <div className="text-sm">
                    <span className="text-gray-600">Author:</span>
                    <span className="ml-2 font-medium">{article.author}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}