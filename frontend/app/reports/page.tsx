'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  FileText,
  Search,
  Download,
  Calendar,
  Filter,
  TrendingUp
} from 'lucide-react'
import { formatDate } from '@/lib/utils'

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
        <p className="text-muted-foreground">
          AI-generated intelligence reports and analysis summaries
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search reports..."
            className="pl-9"
          />
        </div>
        <Button variant="outline" className="sm:w-auto">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
        <Button variant="outline" className="sm:w-auto">
          <Calendar className="h-4 w-4 mr-2" />
          Date Range
        </Button>
      </div>

      {/* Reports Grid */}
      <div className="grid gap-6">
        {/* Daily Report */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5 text-blue-600" />
                  Daily AI Intelligence Brief
                </CardTitle>
                <CardDescription>
                  {formatDate(new Date())} • Generated at 6:00 AM
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="default" className="bg-green-100 text-green-800">
                  Delivered
                </Badge>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export PDF
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">24</div>
                  <div className="text-sm text-blue-600">Articles Analyzed</div>
                </div>
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">3</div>
                  <div className="text-sm text-green-600">High Priority Items</div>
                </div>
                <div className="text-center p-4 bg-purple-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">87%</div>
                  <div className="text-sm text-purple-600">Avg Relevance Score</div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Key Findings</h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• AI regulation discussions gaining momentum in Congress</li>
                  <li>• New breakthrough in quantum computing announced by IBM</li>
                  <li>• Tech industry layoffs continue but at slower pace</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Weekly Report */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  Weekly Trend Analysis
                </CardTitle>
                <CardDescription>
                  Week of {formatDate(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000))} • 156 articles
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary">
                  Processing
                </Badge>
                <Button variant="outline" size="sm" disabled>
                  <Download className="h-4 w-4 mr-2" />
                  Generating...
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-muted-foreground">
              Weekly trend analysis in progress. Report will be available in approximately 15 minutes.
            </div>
          </CardContent>
        </Card>

        {/* Previous Reports */}
        <Card>
          <CardHeader>
            <CardTitle>Report History</CardTitle>
            <CardDescription>
              Previous reports and analysis summaries
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Array.from({ length: 7 }).map((_, i) => {
                const date = new Date(Date.now() - (i + 1) * 24 * 60 * 60 * 1000)
                return (
                  <div key={i} className="flex items-center justify-between py-2 border-b last:border-b-0">
                    <div className="flex items-center gap-3">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <div className="text-sm font-medium">
                          Daily Brief - {formatDate(date)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {15 + i} articles analyzed
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        PDF
                      </Badge>
                      <Button variant="ghost" size="sm">
                        <Download className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}