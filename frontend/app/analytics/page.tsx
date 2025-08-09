'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { CostChart } from '@/components/analytics/CostChart'
import { SourceChart } from '@/components/analytics/SourceChart'
import { VolumeChart } from '@/components/analytics/VolumeChart'
import { 
  TrendingUp,
  DollarSign,
  Rss,
  Clock,
  Target,
  Download,
  RefreshCw
} from 'lucide-react'
import { formatCurrency, formatNumber } from '@/lib/utils'

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            System performance metrics and intelligence insights
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select defaultValue="30d">
            <SelectTrigger className="w-[120px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Performance Indicators */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Processing Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(0.565)}</div>
            <p className="text-xs text-muted-foreground">
              152 articles processed
            </p>
            <Badge variant="outline" className="text-xs mt-2">
              $0.0037 per article
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processing Efficiency</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">94.7%</div>
            <p className="text-xs text-muted-foreground">
              Success rate (30 days)
            </p>
            <Badge variant="default" className="text-xs mt-2 bg-green-100 text-green-800">
              Excellent
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Response Time</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.2s</div>
            <p className="text-xs text-muted-foreground">
              API response average
            </p>
            <Badge variant="outline" className="text-xs mt-2">
              Under 2s target
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Content Quality Score</CardTitle>
            <Target className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">83.2%</div>
            <p className="text-xs text-muted-foreground">
              Average relevance score
            </p>
            <Badge variant="default" className="text-xs mt-2 bg-purple-100 text-purple-800">
              High Quality
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Cost Tracking</CardTitle>
            <CardDescription>
              Processing costs over time with projections
            </CardDescription>
          </CardHeader>
          <CardContent>
            <CostChart />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Source Performance</CardTitle>
            <CardDescription>
              Article volume by news source
            </CardDescription>
          </CardHeader>
          <CardContent>
            <SourceChart />
          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Processing Volume</CardTitle>
            <CardDescription>
              Articles processed per day with trend analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            <VolumeChart />
          </CardContent>
        </Card>
      </div>

      {/* Detailed Metrics */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Rss className="h-5 w-5" />
              Source Analysis
            </CardTitle>
            <CardDescription>
              Performance metrics by news source
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: "TechCrunch", articles: 24, relevance: 89, tier: "Tier 1" },
                { name: "Ars Technica", articles: 18, relevance: 85, tier: "Tier 1" },
                { name: "The Verge", articles: 22, relevance: 82, tier: "Tier 1" },
                { name: "Wired", articles: 16, relevance: 88, tier: "Tier 1" },
                { name: "MIT Tech Review", articles: 12, relevance: 92, tier: "Tier 1" },
              ].map((source, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div>
                      <div className="font-medium text-sm">{source.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {source.articles} articles
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      variant={source.tier === "Tier 1" ? "default" : "secondary"}
                      className="text-xs"
                    >
                      {source.tier}
                    </Badge>
                    <Badge 
                      variant={source.relevance > 85 ? "default" : "secondary"}
                      className="text-xs"
                    >
                      {source.relevance}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
            <CardDescription>
              Real-time system monitoring and alerts
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">API Uptime</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium">99.8%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Database Performance</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium">Optimal</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Processing Queue</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span className="text-sm font-medium">3 pending</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Error Rate</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium">0.02%</span>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Memory Usage</span>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-sm font-medium">68%</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}