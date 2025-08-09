'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp } from 'lucide-react'

interface VolumeData {
  date: string
  articles: number
  processed: number
  relevant: number
}

async function fetchVolumeData(): Promise<VolumeData[]> {
  // TODO: Replace with actual API call
  const data: VolumeData[] = []
  const now = new Date()
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    
    // Simulate realistic volume data
    const baseVolume = 20 + Math.sin(i / 7) * 5 // Weekly pattern
    const articles = Math.floor(baseVolume + Math.random() * 10)
    const processed = Math.floor(articles * (0.95 + Math.random() * 0.05)) // 95-100% processing rate
    const relevant = Math.floor(processed * (0.6 + Math.random() * 0.3)) // 60-90% relevance
    
    data.push({
      date: date.toISOString().split('T')[0],
      articles,
      processed,
      relevant
    })
  }
  
  return data
}

export function VolumeChart() {
  const { data: volumeData, isLoading, error } = useQuery({
    queryKey: ['volume-data'],
    queryFn: fetchVolumeData,
    refetchInterval: 300000, // Refresh every 5 minutes
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Article Volume</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[250px] flex items-center justify-center">
            <div className="text-gray-500">Loading volume data...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !volumeData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Article Volume</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[250px] flex items-center justify-center">
            <div className="text-red-600">Failed to load volume data</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const totalArticles = volumeData.reduce((sum, day) => sum + day.articles, 0)
  const totalProcessed = volumeData.reduce((sum, day) => sum + day.processed, 0)
  const totalRelevant = volumeData.reduce((sum, day) => sum + day.relevant, 0)
  
  const processingRate = (totalProcessed / totalArticles) * 100
  const relevanceRate = (totalRelevant / totalProcessed) * 100

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <TrendingUp className="h-5 w-5" />
          <span>Article Volume</span>
        </CardTitle>
        <CardDescription>
          Processing trends over the last 30 days
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4 grid grid-cols-3 gap-2 text-sm">
          <div className="text-center">
            <div className="text-lg font-bold text-blue-600">{totalArticles}</div>
            <div className="text-xs text-gray-500">Total Articles</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">{processingRate.toFixed(1)}%</div>
            <div className="text-xs text-gray-500">Processing Rate</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-purple-600">{relevanceRate.toFixed(1)}%</div>
            <div className="text-xs text-gray-500">Relevance Rate</div>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={volumeData}>
            <defs>
              <linearGradient id="colorArticles" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="colorProcessed" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="colorRelevant" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 10 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip 
              formatter={(value: number, name: string) => [value, name.charAt(0).toUpperCase() + name.slice(1)]}
              labelFormatter={(label) => new Date(label).toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                year: 'numeric'
              })}
            />
            <Area
              type="monotone"
              dataKey="articles"
              stackId="1"
              stroke="#3b82f6"
              fill="url(#colorArticles)"
            />
            <Area
              type="monotone"
              dataKey="processed"
              stackId="2"
              stroke="#10b981"
              fill="url(#colorProcessed)"
            />
            <Area
              type="monotone"
              dataKey="relevant"
              stackId="3"
              stroke="#8b5cf6"
              fill="url(#colorRelevant)"
            />
          </AreaChart>
        </ResponsiveContainer>

        <div className="mt-2 flex justify-center space-x-4 text-xs">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span className="text-gray-600">Articles Fetched</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-500 rounded"></div>
            <span className="text-gray-600">Processed</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-purple-500 rounded"></div>
            <span className="text-gray-600">Relevant</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}