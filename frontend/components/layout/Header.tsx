'use client'

import { useState } from 'react'
import { Bell, Search, Menu } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useRouter } from 'next/navigation'

interface HeaderProps {
  onMenuClick?: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const [globalSearch, setGlobalSearch] = useState('')
  const router = useRouter()

  const handleGlobalSearch = (query: string) => {
    setGlobalSearch(query)
    
    if (query.trim()) {
      // Navigate to articles page if not already there
      router.push('/articles')
      
      // Dispatch search event for ArticleList to handle
      setTimeout(() => {
        window.dispatchEvent(new CustomEvent('searchResults', {
          detail: {
            type: 'text',
            query: query,
            results: []
          }
        }))
      }, 100)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleGlobalSearch(globalSearch)
    }
  }

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Mobile menu button */}
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={onMenuClick}
          >
            <Menu className="h-5 w-5" />
          </Button>
          
          {/* Breadcrumbs would go here */}
          <div className="hidden lg:block">
            <nav className="flex items-center space-x-2 text-sm text-gray-500">
              <span>Dashboard</span>
            </nav>
          </div>
        </div>

        {/* Search and actions */}
        <div className="flex items-center space-x-4">
          {/* Global search */}
          <div className="hidden md:block relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search articles, reports..."
              className="pl-10 w-64"
              value={globalSearch}
              onChange={(e) => setGlobalSearch(e.target.value)}
              onKeyPress={handleKeyPress}
            />
          </div>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
              3
            </span>
          </Button>

          {/* User menu would go here */}
          <div className="w-8 h-8 bg-gray-300 rounded-full"></div>
        </div>
      </div>
    </header>
  )
}