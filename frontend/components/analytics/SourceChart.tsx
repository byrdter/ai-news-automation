'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { Rss } from 'lucide-react'

interface SourcePerformance {
  name: string
  tier: number
  articles: number
  avgRelevance: number
  avgQuality: number
  successRate: number
}

async function fetchSourcePerformance(): Promise<SourcePerformance[]> {
  // TODO: Replace with actual API call
  return [
    {
      name: 'OpenAI Blog',
      tier: 1,
      articles: 24,
      avgRelevance: 0.94,
      avgQuality: 0.91,
      successRate: 100
    },
    {
      name: 'DeepMind Blog',
      tier: 1,
      articles: 18,
      avgRelevance: 0.92,
      avgQuality: 0.89,
      successRate: 100
    },
    {
      name: 'Google AI Blog',
      tier: 1,
      articles: 22,
      avgRelevance: 0.89,
      avgQuality: 0.87,
      successRate: 95.5
    },
    {
      name: 'MIT AI News',
      tier: 2,
      articles: 16,
      avgRelevance: 0.86,
      avgQuality: 0.84,
      successRate: 93.8
    },
    {
      name: 'TechCrunch AI',
      tier: 2,
      articles: 28,
      avgRelevance: 0.79,
      avgQuality: 0.76,
      successRate: 89.3
    },
    {
      name: 'NVIDIA Blog',
      tier: 2,
      articles: 14,
      avgRelevance: 0.82,
      avgQuality: 0.80,
      successRate: 92.9
    },
    {
      name: 'VentureBeat AI',
      tier: 3,
      articles: 31,
      avgRelevance: 0.74,
      avgQuality: 0.71,
      successRate: 87.1
    }
  ]
}

function getTierColor(tier: number) {
  switch (tier) {
    case 1: return 'text-green-700 bg-green-100'
    case 2: return 'text-blue-700 bg-blue-100'
    case 3: return 'text-yellow-700 bg-yellow-100'
    default: return 'text-gray-700 bg-gray-100'
  }
}

export function SourceChart() {
  const { data: sourceData, isLoading, error } = useQuery({
    queryKey: ['source-performance'],
    queryFn: fetchSourcePerformance,
    refetchInterval: 300000, // Refresh every 5 minutes
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Rss className="h-5 w-5" />
            <span>Source Performance</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <div className="text-gray-500">Loading source data...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !sourceData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Rss className="h-5 w-5" />
            <span>Source Performance</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center">
            <div className="text-red-600">Failed to load source data</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Rss className="h-5 w-5" />
          <span>Source Performance</span>
        </CardTitle>
        <CardDescription>
          Article quality and relevance by news source
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {sourceData.map((source) => (
            <div key={source.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="font-medium text-sm">{source.name}</span>
                  <Badge variant="outline" className={`text-xs ${getTierColor(source.tier)}`}>
                    Tier {source.tier}
                  </Badge>
                </div>
                <div className="flex items-center space-x-3 text-xs text-gray-500">
                  <span>{source.articles} articles</span>
                  <span>{source.successRate.toFixed(1)}% uptime</span>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Relevance Score Bar */}
                <div className="flex-1">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Relevance</span>
                    <span className="font-medium">{(source.avgRelevance * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${source.avgRelevance * 100}%` }}
                    />
                  </div>
                </div>

                {/* Quality Score Bar */}
                <div className="flex-1">
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-gray-500">Quality</span>
                    <span className="font-medium">{(source.avgQuality * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${source.avgQuality * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            Tier 1: Premium sources • Tier 2: High-quality • Tier 3: Broad coverage
          </div>
        </div>
      </CardContent>
    </Card>
  )
}