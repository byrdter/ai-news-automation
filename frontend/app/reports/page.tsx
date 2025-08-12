'use client'

import { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CalendarIcon, DownloadIcon, FileTextIcon, TrendingUpIcon } from 'lucide-react'
import Link from 'next/link'

interface Report {
  id: string
  type: 'daily' | 'weekly' | 'monthly'
  title: string
  created_at: string
  article_count: number
  key_topics: string[]
  sentiment_score: number
  status: 'complete' | 'processing' | 'failed'
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedType, setSelectedType] = useState<'all' | 'daily' | 'weekly' | 'monthly'>('all')

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      // For now, use mock data until API endpoint is ready
      const mockReports: Report[] = [
        {
          id: '1',
          type: 'daily',
          title: 'Daily Intelligence Brief - August 7, 2025',
          created_at: '2025-08-07T06:00:00Z',
          article_count: 152,
          key_topics: ['AI Agents', 'Airbnb', 'Tech Industry', 'Machine Learning'],
          sentiment_score: 0.65,
          status: 'complete'
        },
        {
          id: '2',
          type: 'weekly',
          title: 'Weekly Analysis Report - Week 32',
          created_at: '2025-08-04T06:00:00Z',
          article_count: 847,
          key_topics: ['AI Development', 'Market Trends', 'Startup Funding', 'Cloud Computing'],
          sentiment_score: 0.72,
          status: 'complete'
        },
        {
          id: '3',
          type: 'monthly',
          title: 'Monthly Strategic Overview - July 2025',
          created_at: '2025-08-01T06:00:00Z',
          article_count: 3421,
          key_topics: ['Industry Analysis', 'Tech Innovations', 'Market Growth', 'AI Ethics'],
          sentiment_score: 0.68,
          status: 'complete'
        },
        {
          id: '4',
          type: 'daily',
          title: 'Daily Intelligence Brief - August 6, 2025',
          created_at: '2025-08-06T06:00:00Z',
          article_count: 143,
          key_topics: ['Cybersecurity', 'Data Privacy', 'Tech Regulation'],
          sentiment_score: 0.61,
          status: 'complete'
        }
      ]
      
      setReports(mockReports)
      setLoading(false)
    } catch (error) {
      console.error('Error fetching reports:', error)
      setLoading(false)
    }
  }

  const filteredReports = selectedType === 'all' 
    ? reports 
    : reports.filter(r => r.type === selectedType)

  const getSentimentColor = (score: number) => {
    if (score >= 0.7) return 'text-green-600'
    if (score >= 0.4) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getSentimentLabel = (score: number) => {
    if (score >= 0.7) return 'Positive'
    if (score >= 0.4) return 'Neutral'
    return 'Negative'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">Intelligence Reports</h1>
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
        <h1 className="text-3xl font-bold">Intelligence Reports</h1>
        <Button>
          <FileTextIcon className="mr-2 h-4 w-4" />
          Generate New Report
        </Button>
      </div>

      <Tabs defaultValue="all" onValueChange={(value) => setSelectedType(value as any)}>
        <TabsList>
          <TabsTrigger value="all">All Reports</TabsTrigger>
          <TabsTrigger value="daily">Daily</TabsTrigger>
          <TabsTrigger value="weekly">Weekly</TabsTrigger>
          <TabsTrigger value="monthly">Monthly</TabsTrigger>
        </TabsList>

        <TabsContent value={selectedType} className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredReports.map((report) => (
              <Card key={report.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <Badge variant={report.type === 'daily' ? 'default' : report.type === 'weekly' ? 'secondary' : 'outline'}>
                      {report.type.charAt(0).toUpperCase() + report.type.slice(1)}
                    </Badge>
                    {report.status === 'complete' && (
                      <Button size="sm" variant="ghost">
                        <DownloadIcon className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  <CardTitle className="text-lg mt-2">
                    <Link href={`/reports/${report.id}/articles`} className="hover:underline">
                      {report.title}
                    </Link>
                  </CardTitle>
                  <CardDescription className="flex items-center gap-2">
                    <CalendarIcon className="h-3 w-3" />
                    {formatDate(report.created_at)}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Articles Analyzed</span>
                      <span className="font-semibold">{report.article_count.toLocaleString()}</span>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">Sentiment</span>
                      <span className={`font-semibold ${getSentimentColor(report.sentiment_score)}`}>
                        <TrendingUpIcon className="inline h-3 w-3 mr-1" />
                        {getSentimentLabel(report.sentiment_score)}
                      </span>
                    </div>

                    <div>
                      <span className="text-sm text-gray-600">Key Topics</span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {report.key_topics.slice(0, 3).map((topic, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {topic}
                          </Badge>
                        ))}
                        {report.key_topics.length > 3 && (
                          <Badge variant="outline" className="text-xs">
                            +{report.key_topics.length - 3}
                          </Badge>
                        )}
                      </div>
                    </div>

                    <div className="pt-3 border-t">
                      <Link href={`/reports/${report.id}/articles`}>
                        <Button variant="outline" size="sm" className="w-full">
                          View Full Report
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredReports.length === 0 && (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <FileTextIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No {selectedType !== 'all' ? selectedType : ''} reports available</p>
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Total Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{reports.length}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Articles Analyzed</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {reports.reduce((sum, r) => sum + r.article_count, 0).toLocaleString()}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Avg Sentiment</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">
              {(reports.reduce((sum, r) => sum + r.sentiment_score, 0) / reports.length).toFixed(2)}
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Latest Report</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">
              {reports[0] ? formatDate(reports[0].created_at).split(',')[0] : 'N/A'}
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
    </DashboardLayout>
  )
}