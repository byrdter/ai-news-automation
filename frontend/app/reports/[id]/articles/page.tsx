'use client'

import { useParams, useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  ArrowLeft,
  Search,
  ExternalLink,
  Clock,
  Target,
  TrendingUp,
  Eye,
  FileText
} from 'lucide-react'
import { formatDate, getTimeAgo } from '@/lib/utils'
import type { ArticleWithSource } from '@/types/database'

interface Report {
  id: string
  title: string
  date: string
  articleCount: number
  articles: ArticleWithSource[]
}

// Mock data for report articles - in real app, this would come from API
const mockReportData: Record<string, Report> = {
  '1': {
    id: '1',
    title: 'Daily AI Intelligence Brief',
    date: new Date().toISOString(),
    articleCount: 24,
    articles: [
      // Mock article data - in real implementation, fetch from API
      {
        id: 'mock-1',
        title: 'OpenAI Announces GPT-4.5 with Enhanced Reasoning Capabilities',
        url: 'https://openai.com/blog/gpt-4.5-enhanced-reasoning',
        summary: 'OpenAI unveils GPT-4.5, featuring 40% performance improvement in reasoning tasks, extended context length, and enhanced factual accuracy.',
        published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        relevance_score: 0.94,
        sentiment_score: 0.15,
        quality_score: 0.91,
        urgency_score: 0.75,
        view_count: 1247,
        word_count: 1250,
        author: 'OpenAI Team',
        categories: ['AI Research', 'Language Models', 'OpenAI'],
        keywords: ['GPT-4.5', 'reasoning', 'AI', 'language model'],
        source_id: '1',
        content: null,
        processing_stage: 'summarized',
        processing_errors: null,
        entities: { companies: ['OpenAI'], people: ['Sam Altman'], technologies: ['GPT-4'] },
        topics: ['Artificial Intelligence', 'Machine Learning'],
        title_embedding: null,
        content_embedding: null,
        share_count: 89,
        external_engagement: null,
        content_hash: 'abc123',
        duplicate_of_id: null,
        analysis_model: 'gpt-4o-mini',
        analysis_cost_usd: 0.0034,
        analysis_timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
        processed: true,
        sources: {
          id: '1',
          name: 'OpenAI Blog',
          url: 'https://openai.com/blog/',
          rss_feed_url: 'https://openai.com/blog/rss.xml',
          tier: 1,
          category: 'AI Research',
          active: true,
          fetch_interval: 3600,
          max_articles_per_fetch: 50,
          last_fetched_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          last_successful_fetch_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          consecutive_failures: 0,
          total_articles_fetched: 24,
          metadata_json: null,
          created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
        }
      },
      {
        id: 'mock-2',
        title: 'Google Accelerates Gemini Pro Enterprise Rollout Across Fortune 500',
        url: 'https://blog.google/technology/ai/gemini-pro-enterprise',
        summary: 'Google announces Gemini Pro availability for all Fortune 500 companies with specialized deployment support and industry-specific fine-tuning.',
        published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        relevance_score: 0.92,
        sentiment_score: 0.22,
        quality_score: 0.89,
        urgency_score: 0.82,
        view_count: 892,
        word_count: 1450,
        author: 'Google AI Team',
        categories: ['Enterprise AI', 'Google', 'Gemini'],
        keywords: ['Gemini Pro', 'enterprise', 'Fortune 500', 'Google'],
        source_id: '2',
        content: null,
        processing_stage: 'summarized',
        processing_errors: null,
        entities: { companies: ['Google'], technologies: ['Gemini Pro'] },
        topics: ['Artificial Intelligence', 'Enterprise Technology'],
        title_embedding: null,
        content_embedding: null,
        share_count: 156,
        external_engagement: null,
        content_hash: 'def456',
        duplicate_of_id: null,
        analysis_model: 'gpt-4o-mini',
        analysis_cost_usd: 0.0041,
        analysis_timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
        processed: true,
        sources: {
          id: '2',
          name: 'Google AI Blog',
          url: 'https://blog.google/technology/ai/',
          rss_feed_url: 'https://blog.google/technology/ai/rss.xml',
          tier: 1,
          category: 'AI Research',
          active: true,
          fetch_interval: 3600,
          max_articles_per_fetch: 50,
          last_fetched_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          last_successful_fetch_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
          consecutive_failures: 0,
          total_articles_fetched: 18,
          metadata_json: null,
          created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
        }
      },
      {
        id: 'mock-3',
        title: 'Congressional AI Regulation Bill Advances Through Committee',
        url: 'https://congress.gov/bill/ai-transparency-act',
        summary: 'House Energy and Commerce Committee approves bipartisan legislation requiring algorithmic transparency for AI systems with significant user interactions.',
        published_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        relevance_score: 0.88,
        sentiment_score: -0.05,
        quality_score: 0.87,
        urgency_score: 0.91,
        view_count: 634,
        word_count: 980,
        author: 'Congressional Reporter',
        categories: ['AI Policy', 'Regulation', 'Congress'],
        keywords: ['AI regulation', 'transparency', 'committee', 'bipartisan'],
        source_id: '3',
        content: null,
        processing_stage: 'summarized',
        processing_errors: null,
        entities: { organizations: ['House Energy and Commerce Committee'], topics: ['AI Regulation'] },
        topics: ['AI Policy', 'Government'],
        title_embedding: null,
        content_embedding: null,
        share_count: 203,
        external_engagement: null,
        content_hash: 'ghi789',
        duplicate_of_id: null,
        analysis_model: 'gpt-4o-mini',
        analysis_cost_usd: 0.0028,
        analysis_timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        updated_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
        processed: true,
        sources: {
          id: '3',
          name: 'TechCrunch',
          url: 'https://techcrunch.com',
          rss_feed_url: 'https://techcrunch.com/feed/',
          tier: 1,
          category: 'Tech News',
          active: true,
          fetch_interval: 1800,
          max_articles_per_fetch: 100,
          last_fetched_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          last_successful_fetch_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
          consecutive_failures: 0,
          total_articles_fetched: 67,
          metadata_json: null,
          created_at: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
          updated_at: new Date(Date.now() - 30 * 60 * 1000).toISOString()
        }
      }
    ]
  }
}

export default function ReportArticlesPage() {
  const params = useParams()
  const router = useRouter()
  const reportId = params.id as string

  // In a real app, this would fetch from API
  const { data: reportData, isLoading } = useQuery({
    queryKey: ['report-articles', reportId],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      return mockReportData[reportId] || null
    },
    enabled: !!reportId
  })

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-4 bg-gray-100 rounded w-1/3 mb-8"></div>
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="border rounded-lg p-4">
                  <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-4 bg-gray-100 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-100 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!reportData) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
          <div className="text-center py-12">
            <FileText className="h-12 w-12 mx-auto text-gray-400 mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Report Not Found</h1>
            <p className="text-gray-600 mb-4">
              The report you're looking for doesn't exist or may have been removed.
            </p>
            <Button onClick={() => router.back()} variant="outline">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Reports
            </Button>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button onClick={() => router.back()} variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Reports
          </Button>
          <nav className="text-sm text-gray-500">
            Reports / {reportData.title} / Articles
          </nav>
        </div>

        <div className="space-y-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Articles in {reportData.title}</h1>
            <p className="text-muted-foreground">
              {formatDate(new Date(reportData.date))} • {reportData.articleCount} articles analyzed for this report
            </p>
          </div>

          {/* Search and Summary */}
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search articles in this report..."
                className="pl-9"
              />
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>{reportData.articles.length} articles shown</span>
              <Badge variant="outline">{reportData.title}</Badge>
            </div>
          </div>
        </div>

        {/* Articles Grid */}
        <div className="grid gap-4">
          {reportData.articles.map((article, index) => (
            <Card key={article.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className="text-xs">
                        #{index + 1}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {article.sources.name}
                      </Badge>
                      <Badge 
                        variant={article.relevance_score > 0.8 ? 'default' : 'secondary'}
                        className="text-xs"
                      >
                        {Math.round(article.relevance_score * 100)}% relevance
                      </Badge>
                    </div>

                    <Link 
                      href={`/articles/${article.id}`}
                      className="block group"
                    >
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors mb-2">
                        {article.title}
                      </h3>
                    </Link>

                    <p className="text-gray-600 text-sm mb-3 leading-relaxed">
                      {article.summary}
                    </p>

                    <div className="flex items-center gap-4 text-xs text-gray-500">
                      <div className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        <span>{getTimeAgo(article.published_at)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Eye className="h-3 w-3" />
                        <span>{article.view_count} views</span>
                      </div>
                      {article.word_count && (
                        <span>{article.word_count} words</span>
                      )}
                      {article.author && (
                        <span>by {article.author}</span>
                      )}
                    </div>

                    {/* Categories */}
                    {article.categories && article.categories.length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-3">
                        {article.categories.slice(0, 4).map((category) => (
                          <Badge key={category} variant="secondary" className="text-xs px-2 py-0.5">
                            {category}
                          </Badge>
                        ))}
                        {article.categories.length > 4 && (
                          <Badge variant="secondary" className="text-xs px-2 py-0.5">
                            +{article.categories.length - 4}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex items-start gap-2 ml-4">
                    <Link href={`/articles/${article.id}`}>
                      <Button variant="outline" size="sm">
                        View Details
                      </Button>
                    </Link>
                    <Button variant="ghost" size="sm" asChild>
                      <a href={article.url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Report Actions */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold mb-1">Report Actions</h3>
                <p className="text-sm text-gray-600">
                  These {reportData.articles.length} articles contributed to the analysis and insights in {reportData.title}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Link href={`/reports/${reportId}`}>
                  <Button variant="outline">
                    <FileText className="h-4 w-4 mr-2" />
                    View Full Report
                  </Button>
                </Link>
                <Button>
                  Export Article List
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}