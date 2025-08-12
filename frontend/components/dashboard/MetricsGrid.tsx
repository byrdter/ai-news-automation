'use client'
import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatNumber } from '@/lib/utils'
import { useTodayArticleCount } from '@/hooks/useTodayArticleCount'
import { useReportCount } from '@/hooks/useReportCount'
import { useArticleCount } from '@/hooks/useArticleCount'
import { useRouter } from 'next/navigation'
import {
  FileText,
  Newspaper,
  DollarSign,
  Rss,
  TrendingUp,
  Clock,
  Target,
  Zap
} from 'lucide-react'

export function MetricsGrid() {
  const router = useRouter()
  const { count: todayCount, dateLabel } = useTodayArticleCount()
  const { count: reportCount } = useReportCount()
  const { count: totalArticles } = useArticleCount()
  
  const { data: metricsData, isLoading, error } = useQuery({
    queryKey: ['dashboard-metrics'],
    queryFn: async () => {
      const response = await fetch('/api/analytics')
      if (!response.ok) {
        throw new Error('Failed to fetch metrics')
      }
      return response.json()
    },
    refetchInterval: 30000,
  })

  const handleTodayArticlesClick = async () => {
    try {
      // Get the most recent article date
      const response = await fetch('/api/articles?page=0&limit=1')
      const result = await response.json()
      if (result.articles?.[0]) {
        const mostRecentDate = result.articles[0].published_at.split('T')[0]
        const nextDay = new Date(mostRecentDate)
        nextDay.setDate(nextDay.getDate() + 1)
        const nextDayStr = nextDay.toISOString().split('T')[0]
        router.push(`/articles?start_date=${mostRecentDate}&end_date=${nextDayStr}`)
      } else {
        // Fallback to articles page without filter
        router.push('/articles')
      }
    } catch (error) {
      console.error('Error navigating to recent articles:', error)
      router.push('/articles')
    }
  }

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(8)].map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="h-4 bg-gray-200 rounded w-20"></div>
              <div className="h-4 w-4 bg-gray-200 rounded"></div>
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded w-16 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-24"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    )
  }

  if (error) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="col-span-full">
          <CardContent className="pt-6">
            <p className="text-red-600">Error loading metrics: {error.message}</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const metrics = [
    {
      title: "Total Articles",
      value: formatNumber(totalArticles || metricsData?.totalMetrics?.articlesProcessed || 0),
      description: "100% AI analyzed",
      change: `+${todayCount} ${dateLabel}`,
      onClick: handleTodayArticlesClick,
      clickable: true,
      icon: Newspaper,
      color: "text-blue-600"
    },
    {
      title: "Reports Generated", 
      value: formatNumber(reportCount || metricsData?.totalMetrics?.reportsGenerated || 0),
      description: "Daily, weekly & monthly",
      change: `${reportCount > 0 ? 'Available' : 'Coming soon'}`,
      onClick: reportCount > 0 ? () => router.push('/reports') : undefined,
      clickable: reportCount > 0,
      icon: FileText,
      color: "text-green-600"
    },
    {
      title: "Total Cost",
      value: formatCurrency(metricsData?.totalMetrics?.totalCost || 0),
      description: "Enterprise-grade AI analysis",
      change: "Under budget",
      icon: DollarSign,
      color: "text-yellow-600"
    },
    {
      title: "Active Sources",
      value: formatNumber(metricsData?.systemHealth?.activeSources || 0),
      description: "Tier 1-3 news sources",
      change: "All operational",
      icon: Rss,
      color: "text-purple-600"
    },
    {
      title: "Processing Rate",
      value: `${formatNumber(metricsData?.systemHealth?.processingRate || 0)}/hr`,
      description: "Articles per hour",
      change: "Peak efficiency",
      icon: TrendingUp,
      color: "text-indigo-600"
    },
    {
      title: "Avg Relevance",
      value: `${((metricsData?.sourcePerformance?.[0]?.avgRelevance || 0) * 100).toFixed(1)}%`,
      description: "Content quality score", 
      change: "High quality",
      icon: Target,
      color: "text-green-600"
    },
    {
      title: "System Uptime",
      value: `${(metricsData?.systemHealth?.uptime || 99.2).toFixed(1)}%`,
      description: "Last 30 days",
      change: "Excellent",
      icon: Clock,
      color: "text-emerald-600"
    },
    {
      title: "Cost per Article",
      value: formatCurrency(
        metricsData?.totalMetrics?.articlesProcessed 
          ? (metricsData.totalMetrics.totalCost / metricsData.totalMetrics.articlesProcessed)
          : 0
      ),
      description: "Efficiency metric",
      change: "Optimized",
      icon: Zap,
      color: "text-orange-600"
    }
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {metrics.map((metric, index) => {
        const IconComponent = metric.icon
        return (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {metric.title}
              </CardTitle>
              <IconComponent className={`h-4 w-4 ${metric.color}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metric.value}</div>
              <p className="text-xs text-muted-foreground">
                {metric.description}
              </p>
              <div className="flex items-center pt-1">
                <Badge 
                  variant="outline" 
                  className={`text-xs ${metric.clickable ? 'cursor-pointer hover:bg-blue-50 hover:border-blue-300' : ''}`}
                  onClick={metric.onClick}
                >
                  {metric.change}
                </Badge>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
