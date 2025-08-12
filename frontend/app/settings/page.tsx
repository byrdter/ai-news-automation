'use client'

import { useState, useEffect } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { useArticleCount } from '@/hooks/useArticleCount'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Slider } from '@/components/ui/slider'
import { Badge } from '@/components/ui/badge'
import { 
  Save, 
  RefreshCw, 
  AlertCircle, 
  Shield, 
  Database, 
  Mail,
  Cpu,
  DollarSign,
  Clock,
  Bell
} from 'lucide-react'

interface Settings {
  // System Settings
  processingEnabled: boolean
  maxArticlesPerDay: number
  processingSchedule: string
  
  // Cost Control
  dailyCostLimit: number
  monthlyBudget: number
  costAlertsEnabled: boolean
  
  // Content Filters
  minRelevanceScore: number
  excludedCategories: string[]
  keywordFilters: string
  
  // Notifications
  emailNotificationsEnabled: boolean
  emailAddress: string
  breakingNewsAlerts: boolean
  dailyReportTime: string
  
  // Performance
  apiTimeout: number
  retryAttempts: number
  cacheEnabled: boolean
  
  // Database
  backupEnabled: boolean
  retentionDays: number
}

export default function SettingsPage() {
  const { count: articleCount } = useArticleCount()
  const [settings, setSettings] = useState<Settings>({
    // System Settings
    processingEnabled: true,
    maxArticlesPerDay: 500,
    processingSchedule: 'hourly',
    
    // Cost Control
    dailyCostLimit: 5.0,
    monthlyBudget: 100.0,
    costAlertsEnabled: true,
    
    // Content Filters
    minRelevanceScore: 0.7,
    excludedCategories: [],
    keywordFilters: '',
    
    // Notifications
    emailNotificationsEnabled: true,
    emailAddress: 'admin@example.com',
    breakingNewsAlerts: true,
    dailyReportTime: '06:00',
    
    // Performance
    apiTimeout: 30,
    retryAttempts: 3,
    cacheEnabled: true,
    
    // Database
    backupEnabled: true,
    retentionDays: 90
  })

  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const handleSave = async () => {
    setSaving(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    } catch (error) {
      console.error('Failed to save settings:', error)
    } finally {
      setSaving(false)
    }
  }

  const updateSetting = (key: keyof Settings, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">System Settings</h1>
          <p className="text-gray-600">Configure your news automation system</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Reset to Defaults
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? (
              <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            {saving ? 'Saving...' : saved ? 'Saved!' : 'Save Changes'}
          </Button>
        </div>
      </div>

      <Tabs defaultValue="system" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="system">System</TabsTrigger>
          <TabsTrigger value="cost">Cost Control</TabsTrigger>
          <TabsTrigger value="content">Content</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="database">Database</TabsTrigger>
        </TabsList>

        {/* System Settings */}
        <TabsContent value="system">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="h-5 w-5" />
                  Processing Configuration
                </CardTitle>
                <CardDescription>
                  Configure how your system processes news articles
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label htmlFor="processing-enabled">Enable Article Processing</Label>
                    <p className="text-sm text-gray-600">
                      Turn on/off automatic article collection and analysis
                    </p>
                  </div>
                  <Switch
                    id="processing-enabled"
                    checked={settings.processingEnabled}
                    onCheckedChange={(checked) => updateSetting('processingEnabled', checked)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="max-articles">Maximum Articles per Day</Label>
                  <Input
                    id="max-articles"
                    type="number"
                    value={settings.maxArticlesPerDay}
                    onChange={(e) => updateSetting('maxArticlesPerDay', parseInt(e.target.value))}
                    min="1"
                    max="10000"
                  />
                  <p className="text-sm text-gray-600">
                    Limit processing to control costs and performance
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="schedule">Processing Schedule</Label>
                  <Select
                    value={settings.processingSchedule}
                    onValueChange={(value) => updateSetting('processingSchedule', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="continuous">Continuous</SelectItem>
                      <SelectItem value="hourly">Every Hour</SelectItem>
                      <SelectItem value="2hours">Every 2 Hours</SelectItem>
                      <SelectItem value="6hours">Every 6 Hours</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Cost Control */}
        <TabsContent value="cost">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="h-5 w-5" />
                  Budget Management
                </CardTitle>
                <CardDescription>
                  Set spending limits and cost alerts
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="daily-limit">Daily Cost Limit ($)</Label>
                    <Input
                      id="daily-limit"
                      type="number"
                      step="0.01"
                      value={settings.dailyCostLimit}
                      onChange={(e) => updateSetting('dailyCostLimit', parseFloat(e.target.value))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="monthly-budget">Monthly Budget ($)</Label>
                    <Input
                      id="monthly-budget"
                      type="number"
                      step="0.01"
                      value={settings.monthlyBudget}
                      onChange={(e) => updateSetting('monthlyBudget', parseFloat(e.target.value))}
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label htmlFor="cost-alerts">Cost Alerts</Label>
                    <p className="text-sm text-gray-600">
                      Get notified when approaching budget limits
                    </p>
                  </div>
                  <Switch
                    id="cost-alerts"
                    checked={settings.costAlertsEnabled}
                    onCheckedChange={(checked) => updateSetting('costAlertsEnabled', checked)}
                  />
                </div>

                <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-yellow-800">Current Usage</h4>
                      <p className="text-sm text-yellow-700 mt-1">
                        Today: $0.37 / ${settings.dailyCostLimit} • Month: $8.45 / ${settings.monthlyBudget}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Content Filters */}
        <TabsContent value="content">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Content Filtering
                </CardTitle>
                <CardDescription>
                  Configure content quality and filtering rules
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-3">
                  <Label>Minimum Relevance Score: {Math.round(settings.minRelevanceScore * 100)}%</Label>
                  <Slider
                    value={[settings.minRelevanceScore]}
                    onValueChange={(values) => updateSetting('minRelevanceScore', values[0])}
                    min={0}
                    max={1}
                    step={0.05}
                    className="w-full"
                  />
                  <p className="text-sm text-gray-600">
                    Articles below this relevance threshold will be filtered out
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="keyword-filters">Keyword Filters</Label>
                  <Textarea
                    id="keyword-filters"
                    placeholder="Enter keywords to filter out, one per line"
                    value={settings.keywordFilters}
                    onChange={(e) => updateSetting('keywordFilters', e.target.value)}
                    rows={4}
                  />
                  <p className="text-sm text-gray-600">
                    Articles containing these keywords will be excluded
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Notifications */}
        <TabsContent value="notifications">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Email Notifications
                </CardTitle>
                <CardDescription>
                  Configure email alerts and reports
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label htmlFor="email-notifications">Enable Email Notifications</Label>
                    <p className="text-sm text-gray-600">
                      Receive reports and alerts via email
                    </p>
                  </div>
                  <Switch
                    id="email-notifications"
                    checked={settings.emailNotificationsEnabled}
                    onCheckedChange={(checked) => updateSetting('emailNotificationsEnabled', checked)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email-address">Email Address</Label>
                  <Input
                    id="email-address"
                    type="email"
                    value={settings.emailAddress}
                    onChange={(e) => updateSetting('emailAddress', e.target.value)}
                    placeholder="your@email.com"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label htmlFor="breaking-news">Breaking News Alerts</Label>
                    <p className="text-sm text-gray-600">
                      Get immediate alerts for breaking news
                    </p>
                  </div>
                  <Switch
                    id="breaking-news"
                    checked={settings.breakingNewsAlerts}
                    onCheckedChange={(checked) => updateSetting('breakingNewsAlerts', checked)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="report-time">Daily Report Time</Label>
                  <Input
                    id="report-time"
                    type="time"
                    value={settings.dailyReportTime}
                    onChange={(e) => updateSetting('dailyReportTime', e.target.value)}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance */}
        <TabsContent value="performance">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Performance Settings
                </CardTitle>
                <CardDescription>
                  Configure timeouts and performance parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="api-timeout">API Timeout (seconds)</Label>
                    <Input
                      id="api-timeout"
                      type="number"
                      value={settings.apiTimeout}
                      onChange={(e) => updateSetting('apiTimeout', parseInt(e.target.value))}
                      min="5"
                      max="300"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="retry-attempts">Retry Attempts</Label>
                    <Input
                      id="retry-attempts"
                      type="number"
                      value={settings.retryAttempts}
                      onChange={(e) => updateSetting('retryAttempts', parseInt(e.target.value))}
                      min="0"
                      max="10"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label htmlFor="cache-enabled">Enable Caching</Label>
                    <p className="text-sm text-gray-600">
                      Cache results to improve performance and reduce costs
                    </p>
                  </div>
                  <Switch
                    id="cache-enabled"
                    checked={settings.cacheEnabled}
                    onCheckedChange={(checked) => updateSetting('cacheEnabled', checked)}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Database */}
        <TabsContent value="database">
          <div className="grid gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Database Settings
                </CardTitle>
                <CardDescription>
                  Configure data retention and backup policies
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label htmlFor="backup-enabled">Automatic Backups</Label>
                    <p className="text-sm text-gray-600">
                      Enable automatic daily database backups
                    </p>
                  </div>
                  <Switch
                    id="backup-enabled"
                    checked={settings.backupEnabled}
                    onCheckedChange={(checked) => updateSetting('backupEnabled', checked)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="retention-days">Data Retention (days)</Label>
                  <Input
                    id="retention-days"
                    type="number"
                    value={settings.retentionDays}
                    onChange={(e) => updateSetting('retentionDays', parseInt(e.target.value))}
                    min="1"
                    max="365"
                  />
                  <p className="text-sm text-gray-600">
                    Articles older than this will be automatically archived
                  </p>
                </div>

                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Database className="h-5 w-5 text-blue-600 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-blue-800">Database Status</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        {articleCount} articles • 8 sources • Last backup: 2 hours ago
                      </p>
                      <div className="flex gap-2 mt-2">
                        <Badge variant="outline" className="text-xs">
                          Healthy
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          2.3MB used
                        </Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
    </DashboardLayout>
  )
}