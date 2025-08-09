'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { 
  Rss,
  Search,
  Plus,
  Settings,
  CheckCircle,
  AlertCircle,
  XCircle,
  TrendingUp,
  Clock,
  ExternalLink
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

interface NewsSource {
  id: number
  name: string
  url: string
  tier: 'Tier 1' | 'Tier 2' | 'Tier 3'
  status: 'active' | 'inactive' | 'error'
  articles_count: number
  last_fetched: string
  avg_relevance: number
  enabled: boolean
  description?: string
}

const mockSources: NewsSource[] = [
  {
    id: 1,
    name: "TechCrunch",
    url: "https://techcrunch.com/feed/",
    tier: "Tier 1",
    status: "active",
    articles_count: 24,
    last_fetched: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    avg_relevance: 89,
    enabled: true,
    description: "Leading technology news and startup coverage"
  },
  {
    id: 2,
    name: "Ars Technica",
    url: "https://feeds.arstechnica.com/arstechnica/index",
    tier: "Tier 1", 
    status: "active",
    articles_count: 18,
    last_fetched: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
    avg_relevance: 85,
    enabled: true,
    description: "In-depth technology analysis and reviews"
  },
  {
    id: 3,
    name: "The Verge",
    url: "https://www.theverge.com/rss/index.xml",
    tier: "Tier 1",
    status: "active", 
    articles_count: 22,
    last_fetched: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    avg_relevance: 82,
    enabled: true,
    description: "Technology, science, art, and culture coverage"
  },
  {
    id: 4,
    name: "Wired",
    url: "https://www.wired.com/feed/rss",
    tier: "Tier 1",
    status: "error",
    articles_count: 16,
    last_fetched: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
    avg_relevance: 88,
    enabled: true,
    description: "Future-focused technology and culture"
  },
  {
    id: 5,
    name: "MIT Technology Review",
    url: "https://www.technologyreview.com/feed/",
    tier: "Tier 1",
    status: "active",
    articles_count: 12,
    last_fetched: new Date(Date.now() - 45 * 60 * 1000).toISOString(),
    avg_relevance: 92,
    enabled: true,
    description: "Emerging technology and innovation insights"
  },
  {
    id: 6,
    name: "Hacker News",
    url: "https://feeds.feedburner.com/hn/frontpage",
    tier: "Tier 2",
    status: "active",
    articles_count: 8,
    last_fetched: new Date(Date.now() - 20 * 60 * 1000).toISOString(),
    avg_relevance: 76,
    enabled: true,
    description: "Tech community discussions and news"
  },
  {
    id: 7,
    name: "ZDNet",
    url: "https://www.zdnet.com/news/rss.xml",
    tier: "Tier 2",
    status: "inactive",
    articles_count: 14,
    last_fetched: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
    avg_relevance: 71,
    enabled: false,
    description: "Business technology news and analysis"
  }
]

function getStatusIcon(status: NewsSource['status']) {
  switch (status) {
    case 'active':
      return <CheckCircle className="h-4 w-4 text-green-600" />
    case 'error':
      return <XCircle className="h-4 w-4 text-red-600" />
    case 'inactive':
      return <AlertCircle className="h-4 w-4 text-gray-400" />
  }
}

function getStatusColor(status: NewsSource['status']) {
  switch (status) {
    case 'active':
      return 'bg-green-100 text-green-800'
    case 'error':
      return 'bg-red-100 text-red-800'
    case 'inactive':
      return 'bg-gray-100 text-gray-800'
  }
}

function getTierColor(tier: NewsSource['tier']) {
  switch (tier) {
    case 'Tier 1':
      return 'bg-blue-100 text-blue-800'
    case 'Tier 2':
      return 'bg-purple-100 text-purple-800'
    case 'Tier 3':
      return 'bg-gray-100 text-gray-800'
  }
}

export default function SourcesPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">News Sources</h1>
          <p className="text-muted-foreground">
            Manage RSS feeds and news sources for AI analysis
          </p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Source
        </Button>
      </div>

      {/* Search and Summary */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search news sources..."
            className="pl-9"
          />
        </div>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>{mockSources.filter(s => s.status === 'active').length} Active</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span>{mockSources.filter(s => s.status === 'error').length} Errors</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
            <span>{mockSources.filter(s => s.status === 'inactive').length} Inactive</span>
          </div>
        </div>
      </div>

      {/* Sources Grid */}
      <div className="grid gap-6">
        {mockSources.map((source) => (
          <Card key={source.id}>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Rss className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {source.name}
                      {getStatusIcon(source.status)}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-2">
                      <span>{source.description}</span>
                      <Button variant="ghost" size="sm" className="h-auto p-0">
                        <ExternalLink className="h-3 w-3" />
                      </Button>
                    </CardDescription>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Switch
                    checked={source.enabled}
                    disabled={source.status === 'error'}
                  />
                  <Button variant="ghost" size="sm">
                    <Settings className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Status</span>
                    <Badge className={`text-xs ${getStatusColor(source.status)}`}>
                      {source.status}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Tier</span>
                    <Badge className={`text-xs ${getTierColor(source.tier)}`}>
                      {source.tier}
                    </Badge>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Articles</span>
                    <span className="text-sm font-medium">{source.articles_count}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Relevance</span>
                    <div className="flex items-center gap-1">
                      <span className="text-sm font-medium">{source.avg_relevance}%</span>
                      {source.avg_relevance >= 85 && (
                        <TrendingUp className="h-3 w-3 text-green-600" />
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Last Fetch</span>
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span className="text-sm font-medium">
                        {(() => {
                          const diff = Date.now() - new Date(source.last_fetched).getTime()
                          const hours = Math.floor(diff / (1000 * 60 * 60))
                          const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
                          
                          if (hours > 0) {
                            return `${hours}h ago`
                          } else {
                            return `${minutes}m ago`
                          }
                        })()}
                      </span>
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {source.url}
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2">
                  <Button variant="outline" size="sm">
                    Test Feed
                  </Button>
                  <Button variant="outline" size="sm">
                    View Articles
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Source Statistics */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Source Health</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {Math.round((mockSources.filter(s => s.status === 'active').length / mockSources.length) * 100)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {mockSources.filter(s => s.status === 'active').length} of {mockSources.length} sources operational
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Average Quality</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {Math.round(mockSources.reduce((acc, s) => acc + s.avg_relevance, 0) / mockSources.length)}%
            </div>
            <p className="text-xs text-muted-foreground">
              Content relevance across all sources
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Total Articles</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">
              {mockSources.reduce((acc, s) => acc + s.articles_count, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Articles processed this month
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}