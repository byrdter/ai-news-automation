'use client'

import { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { 
  Plus, 
  Settings, 
  Rss, 
  BarChart3, 
  AlertCircle, 
  CheckCircle,
  Clock,
  ExternalLink,
  Trash2,
  Edit
} from 'lucide-react'
import Link from 'next/link'

interface NewsSource {
  id: string
  name: string
  url: string
  tier: 1 | 2 | 3
  category: string
  is_active: boolean
  last_fetch: string
  articles_count: number
  success_rate: number
  avg_relevance: number
  status: 'healthy' | 'warning' | 'error'
}

export default function SourcesPage() {
  const [sources, setSources] = useState<NewsSource[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTier, setSelectedTier] = useState<'all' | '1' | '2' | '3'>('all')

  useEffect(() => {
    fetchSources()
  }, [])

  const fetchSources = async () => {
    try {
      // AI-focused sources configured in the system
      const mockSources: NewsSource[] = [
        {
          id: '1',
          name: 'OpenAI Blog',
          url: 'https://openai.com/blog/rss/',
          tier: 1,
          category: 'AI Research',
          is_active: true,
          last_fetch: '2025-08-10T15:30:00Z',
          articles_count: 55,
          success_rate: 98.5,
          avg_relevance: 0.95,
          status: 'healthy'
        },
        {
          id: '2',
          name: 'MIT AI News',
          url: 'https://news.mit.edu/topic/artificial-intelligence2-rss.xml',
          tier: 1,
          category: 'AI Research',
          is_active: true,
          last_fetch: '2025-08-10T15:25:00Z',
          articles_count: 50,
          success_rate: 96.2,
          avg_relevance: 0.92,
          status: 'healthy'
        },
        {
          id: '3',
          name: 'TechCrunch AI',
          url: 'https://techcrunch.com/category/artificial-intelligence/feed/',
          tier: 1,
          category: 'AI Industry News',
          is_active: true,
          last_fetch: '2025-08-10T15:28:00Z',
          articles_count: 38,
          success_rate: 94.8,
          avg_relevance: 0.88,
          status: 'healthy'
        },
        {
          id: '4',
          name: 'MarkTechPost',
          url: 'https://www.marktechpost.com/feed/',
          tier: 2,
          category: 'AI Research & Industry',
          is_active: true,
          last_fetch: '2025-08-10T15:22:00Z',
          articles_count: 20,
          success_rate: 91.1,
          avg_relevance: 0.85,
          status: 'healthy'
        },
        {
          id: '5',
          name: 'NVIDIA AI Blog',
          url: 'https://blogs.nvidia.com/feed/',
          tier: 1,
          category: 'AI Hardware & Research',
          is_active: true,
          last_fetch: '2025-08-10T18:45:00Z',
          articles_count: 19,
          success_rate: 93.3,
          avg_relevance: 0.90,
          status: 'healthy'
        },
        {
          id: '6',
          name: 'DeepMind Blog',
          url: 'https://deepmind.com/blog/feed/basic/',
          tier: 1,
          category: 'AI Research',
          is_active: true,
          last_fetch: '2025-08-10T15:20:00Z',
          articles_count: 10,
          success_rate: 95.5,
          avg_relevance: 0.94,
          status: 'healthy'
        },
        {
          id: '7',
          name: 'BAIR Blog',
          url: 'https://bair.berkeley.edu/blog/feed.xml',
          tier: 1,
          category: 'AI Research',
          is_active: true,
          last_fetch: '2025-08-10T15:20:00Z',
          articles_count: 10,
          success_rate: 92.5,
          avg_relevance: 0.91,
          status: 'healthy'
        },
        {
          id: '8',
          name: 'Analytics Vidhya',
          url: 'https://www.analyticsvidhya.com/feed/',
          tier: 3,
          category: 'AI Education & Tutorials',
          is_active: true,
          last_fetch: '2025-08-10T15:20:00Z',
          articles_count: 10,
          success_rate: 89.5,
          avg_relevance: 0.82,
          status: 'healthy'
        }
      ]
      
      setSources(mockSources)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching sources:', error)
      setLoading(false)
    }
  }

  const filteredSources = selectedTier === 'all' 
    ? sources 
    : sources.filter(s => s.tier.toString() === selectedTier)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600'
      case 'warning': return 'text-yellow-600'
      case 'error': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-4 w-4" />
      case 'warning': return <AlertCircle className="h-4 w-4" />
      case 'error': return <AlertCircle className="h-4 w-4" />
      default: return <Clock className="h-4 w-4" />
    }
  }

  const getTierBadgeVariant = (tier: number) => {
    switch (tier) {
      case 1: return 'default'
      case 2: return 'secondary'
      case 3: return 'outline'
      default: return 'outline'
    }
  }

  const formatLastFetch = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    
    if (diffHours < 1) return 'Just now'
    if (diffHours < 24) return `${diffHours}h ago`
    return date.toLocaleDateString()
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">News Sources</h1>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-100 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-3 bg-gray-100 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-100 rounded w-2/3"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">News Sources</h1>
          <p className="text-gray-600">Manage RSS feeds and content sources</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Source
        </Button>
      </div>

      <Tabs defaultValue="all" onValueChange={(value) => setSelectedTier(value as any)}>
        <div className="flex justify-between items-center">
          <TabsList>
            <TabsTrigger value="all">All Sources</TabsTrigger>
            <TabsTrigger value="1">Tier 1</TabsTrigger>
            <TabsTrigger value="2">Tier 2</TabsTrigger>
            <TabsTrigger value="3">Tier 3</TabsTrigger>
          </TabsList>
          
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </Button>
            <Button variant="outline" size="sm">
              <BarChart3 className="h-4 w-4 mr-2" />
              Analytics
            </Button>
          </div>
        </div>

        <TabsContent value={selectedTier} className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSources.map((source) => (
              <Card key={source.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div className="flex items-center gap-2">
                      <Badge variant={getTierBadgeVariant(source.tier)}>
                        Tier {source.tier}
                      </Badge>
                      <div className={`flex items-center gap-1 ${getStatusColor(source.status)}`}>
                        {getStatusIcon(source.status)}
                        <span className="text-xs font-medium capitalize">{source.status}</span>
                      </div>
                    </div>
                    <Switch checked={source.is_active} />
                  </div>
                  
                  <div className="space-y-1">
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Rss className="h-4 w-4" />
                      {source.name}
                    </CardTitle>
                    <CardDescription className="text-sm">
                      {source.category}
                    </CardDescription>
                  </div>
                </CardHeader>
                
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                      <ExternalLink className="h-3 w-3" />
                      <Link href={source.url} target="_blank" className="hover:underline truncate">
                        {new URL(source.url).hostname}
                      </Link>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-600">Articles:</span>
                        <span className="font-semibold ml-1">{source.articles_count}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Success:</span>
                        <span className="font-semibold ml-1">{source.success_rate}%</span>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-600">Relevance:</span>
                        <span className="font-semibold ml-1">{Math.round(source.avg_relevance * 100)}%</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Last fetch:</span>
                        <span className="font-semibold ml-1">{formatLastFetch(source.last_fetch)}</span>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center pt-3 border-t">
                      <Button variant="outline" size="sm">
                        <Edit className="h-3 w-3 mr-1" />
                        Edit
                      </Button>
                      <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredSources.length === 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Rss className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No {selectedTier !== 'all' ? `Tier ${selectedTier}` : ''} sources configured</p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{sources.length}</p>
            <p className="text-xs text-gray-500">
              {sources.filter(s => s.is_active).length} active
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Articles</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {sources.reduce((sum, s) => sum + s.articles_count, 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Avg Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {(sources.reduce((sum, s) => sum + s.success_rate, 0) / sources.length).toFixed(1)}%
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Avg Relevance</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {Math.round(sources.reduce((sum, s) => sum + s.avg_relevance, 0) / sources.length * 100)}%
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
    </DashboardLayout>
  )
}