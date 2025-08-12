'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { useArticleCount } from '@/hooks/useArticleCount'
import { useReportCount } from '@/hooks/useReportCount'
import { 
  BarChart3, 
  FileText, 
  Home, 
  Newspaper, 
  Settings, 
  Rss,
  TrendingUp
} from 'lucide-react'

interface SidebarProps {
  mobile?: boolean
  onNavigate?: () => void
}

export function Sidebar({ mobile = false, onNavigate }: SidebarProps) {
  const pathname = usePathname()
  const { displayCount } = useArticleCount()
  const { displayCount: reportDisplayCount } = useReportCount()

  const navItems = [
    {
      name: 'Dashboard',
      href: '/',
      icon: Home,
      description: 'System overview and metrics'
    },
    {
      name: 'Articles',
      href: '/articles',
      icon: Newspaper,
      description: `${displayCount} AI-analyzed articles`
    },
    {
      name: 'Reports',
      href: '/reports',
      icon: FileText,
      description: `${reportDisplayCount} comprehensive reports`
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      description: 'Performance and cost metrics'
    },
    {
      name: 'Sources',
      href: '/sources',
      icon: Rss,
      description: 'RSS feed management'
    },
    {
      name: 'Settings',
      href: '/settings',
      icon: Settings,
      description: 'System configuration'
    }
  ]

  return (
    <div className={cn(
      "flex flex-col bg-white border-r border-gray-200",
      mobile ? "h-full" : "h-screen w-64"
    )}>
      {/* Logo/Header */}
      <div className="p-6 border-b border-gray-200">
        <Link 
          href="/" 
          className="flex items-center space-x-2"
          onClick={onNavigate}
        >
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-lg font-semibold text-gray-900">
              AI News
            </h1>
            <p className="text-xs text-gray-500">Intelligence Dashboard</p>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || 
            (item.href !== '/' && pathname.startsWith(item.href))
          
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={onNavigate}
              className={cn(
                "group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors",
                isActive
                  ? "bg-blue-50 text-blue-700 border border-blue-200"
                  : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
              )}
            >
              <item.icon
                className={cn(
                  "mr-3 h-5 w-5",
                  isActive ? "text-blue-500" : "text-gray-400 group-hover:text-gray-500"
                )}
              />
              <div className="flex flex-col">
                <span>{item.name}</span>
                {!mobile && (
                  <span className="text-xs text-gray-500 group-hover:text-gray-400">
                    {item.description}
                  </span>
                )}
              </div>
            </Link>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-xs text-gray-600 mb-1">System Status</p>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-xs text-gray-700">All systems operational</span>
          </div>
        </div>
      </div>
    </div>
  )
}