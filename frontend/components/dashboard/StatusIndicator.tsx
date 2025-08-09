'use client'

import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  CheckCircle, 
  AlertCircle, 
  XCircle, 
  Clock,
  Play,
  Pause
} from 'lucide-react'

interface SystemStatus {
  overall: 'operational' | 'degraded' | 'outage' | 'maintenance'
  pipeline: {
    status: 'running' | 'stopped' | 'error'
    lastRun: string
    nextRun: string
  }
  services: {
    database: 'healthy' | 'slow' | 'down'
    rssFeeds: 'healthy' | 'partial' | 'down'
    aiAnalysis: 'healthy' | 'slow' | 'down'
    reporting: 'healthy' | 'slow' | 'down'
  }
}

async function fetchSystemStatus(): Promise<SystemStatus> {
  // TODO: Replace with actual API call
  return {
    overall: 'operational',
    pipeline: {
      status: 'running',
      lastRun: '2024-01-08T10:30:00Z',
      nextRun: '2024-01-08T11:00:00Z'
    },
    services: {
      database: 'healthy',
      rssFeeds: 'healthy', 
      aiAnalysis: 'healthy',
      reporting: 'healthy'
    }
  }
}

function getStatusIcon(status: string) {
  switch (status) {
    case 'operational':
    case 'healthy':
    case 'running':
      return <CheckCircle className="h-4 w-4 text-green-500" />
    case 'degraded':
    case 'slow':
    case 'partial':
      return <AlertCircle className="h-4 w-4 text-yellow-500" />
    case 'outage':
    case 'down':
    case 'error':
      return <XCircle className="h-4 w-4 text-red-500" />
    case 'maintenance':
    case 'stopped':
      return <Clock className="h-4 w-4 text-blue-500" />
    default:
      return <Clock className="h-4 w-4 text-gray-500" />
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'operational':
    case 'healthy':
    case 'running':
      return 'text-green-700 bg-green-100'
    case 'degraded':
    case 'slow':
    case 'partial':
      return 'text-yellow-700 bg-yellow-100'
    case 'outage':
    case 'down':
    case 'error':
      return 'text-red-700 bg-red-100'
    case 'maintenance':
    case 'stopped':
      return 'text-blue-700 bg-blue-100'
    default:
      return 'text-gray-700 bg-gray-100'
  }
}

export function StatusIndicator() {
  const { data: status, isLoading, error } = useQuery({
    queryKey: ['system-status'],
    queryFn: fetchSystemStatus,
    refetchInterval: 15000, // Refresh every 15 seconds
  })

  if (isLoading) {
    return (
      <div className="flex items-center space-x-3">
        <div className="w-4 h-4 bg-gray-300 rounded-full animate-pulse"></div>
        <span className="text-sm text-gray-500">Loading status...</span>
      </div>
    )
  }

  if (error || !status) {
    return (
      <div className="flex items-center space-x-2">
        <XCircle className="h-4 w-4 text-red-500" />
        <span className="text-sm text-red-600">Status unavailable</span>
      </div>
    )
  }

  return (
    <div className="flex items-center space-x-4">
      {/* Overall Status */}
      <div className="flex items-center space-x-2">
        {getStatusIcon(status.overall)}
        <Badge className={getStatusColor(status.overall)}>
          {status.overall.charAt(0).toUpperCase() + status.overall.slice(1)}
        </Badge>
      </div>

      {/* Pipeline Controls */}
      <div className="flex items-center space-x-2">
        <div className="flex items-center space-x-1">
          {getStatusIcon(status.pipeline.status)}
          <span className="text-sm text-gray-700">Pipeline</span>
        </div>
        
        <div className="flex space-x-1">
          <Button size="sm" variant="outline" className="h-8 px-2">
            {status.pipeline.status === 'running' ? (
              <Pause className="h-3 w-3" />
            ) : (
              <Play className="h-3 w-3" />
            )}
          </Button>
        </div>
      </div>

      {/* Service Status Summary */}
      <div className="hidden md:flex items-center space-x-2">
        <span className="text-xs text-gray-500">Services:</span>
        {Object.entries(status.services).map(([service, serviceStatus]) => (
          <div key={service} className="flex items-center space-x-1">
            {getStatusIcon(serviceStatus)}
            <span className="text-xs text-gray-600 capitalize">
              {service.replace(/([A-Z])/g, ' $1').toLowerCase()}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}