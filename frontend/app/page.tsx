import { Suspense } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { MetricsGrid } from '@/components/dashboard/MetricsGrid'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { CostChart } from '@/components/analytics/CostChart'
import { SourceChart } from '@/components/analytics/SourceChart'
import { VolumeChart } from '@/components/analytics/VolumeChart'
import { StatusIndicator } from '@/components/dashboard/StatusIndicator'

export default function HomePage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">
            AI News Intelligence Dashboard
          </h1>
          <StatusIndicator />
        </div>
        
        <Suspense fallback={<div>Loading metrics...</div>}>
          <MetricsGrid />
        </Suspense>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Suspense fallback={<div>Loading recent articles...</div>}>
            <RecentActivity type="articles" title="Latest Articles" />
          </Suspense>
          <Suspense fallback={<div>Loading recent reports...</div>}>
            <RecentActivity type="reports" title="Recent Reports" />
          </Suspense>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Suspense fallback={<div>Loading cost chart...</div>}>
            <CostChart />
          </Suspense>
          <Suspense fallback={<div>Loading source chart...</div>}>
            <SourceChart />
          </Suspense>
          <Suspense fallback={<div>Loading volume chart...</div>}>
            <VolumeChart />
          </Suspense>
        </div>
      </div>
    </DashboardLayout>
  )
}