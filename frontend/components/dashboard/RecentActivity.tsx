'use client'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDate, getTimeAgo } from '@/lib/utils'
import { ExternalLink, FileText, Newspaper } from 'lucide-react'

export function RecentActivity() {
  const { data: articlesData, isLoading: loadingArticles } = useQuery({
    queryKey: ['recent-articles'],
    queryFn: async () => {
      const response = await fetch('/api/articles?limit=5')
      if (!response.ok) {
        throw new Error('Failed to fetch articles')
      }
      return response.json()
    },
    refetchInterval: 60000,
  })

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Newspaper className="h-5 w-5" />
              Latest Articles
            </CardTitle>
            <CardDescription>
              Latest AI-analyzed articles
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/articles">View All</Link>
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingArticles ? (
            [...Array(3)].map((_, i) => (
              <div key={i} className="space-y-2 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/4"></div>
              </div>
            ))
          ) : articlesData?.articles?.length ? (
            articlesData.articles.map((article) => (
              <div key={article.id} className="border-l-2 border-l-blue-500 pl-4 space-y-2">
                <div>
                  <h4 className="font-medium text-sm leading-tight line-clamp-2">
                    {article.title}
                  </h4>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {article.sources?.name || 'Unknown Source'}
                    </Badge>
                    <Badge 
                      variant={article.relevance_score > 0.8 ? 'default' : 'secondary'}
                      className="text-xs"
                    >
                      {Math.round((article.relevance_score || 0) * 100)}%
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {getTimeAgo(article.created_at)}
                  </p>
                  {article.summary && (
                    <p className="text-xs text-gray-600 line-clamp-2 mt-1">
                      {article.summary}
                    </p>
                  )}
                </div>
                {article.url && (
                  <Link 
                    href={article.url} 
                    target="_blank"
                    className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800"
                  >
                    Read article <ExternalLink className="h-3 w-3" />
                  </Link>
                )}
              </div>
            ))
          ) : (
            <p className="text-sm text-gray-500">No articles found</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Recent Reports
            </CardTitle>
            <CardDescription>
              Recently generated reports
            </CardDescription>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/reports">View All</Link>
          </Button>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="border-l-2 border-l-green-500 pl-4 space-y-2">
            <div>
              <h4 className="font-medium text-sm">Daily AI Intelligence Brief - {formatDate(new Date())}</h4>
              <div className="flex items-center gap-2 mt-1">
                <Badge variant="outline" className="text-xs">daily</Badge>
                <Badge variant="default" className="text-xs bg-green-100 text-green-800">delivered</Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {articlesData?.articles?.length || 0} articles
              </p>
            </div>
          </div>
          <div className="text-center py-4">
            <p className="text-sm text-gray-500">Report system coming soon...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
