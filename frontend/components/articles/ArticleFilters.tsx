'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Filter, X } from 'lucide-react'

export interface FilterState {
  categories: string[]
  sources: string[]
  minRelevance: number
  dateRange: 'all' | '24h' | '7d' | '30d'
  tier: 'all' | '1' | '2' | '3'
}

const availableCategories = [
  'AI Research',
  'Language Models', 
  'Computer Vision',
  'Machine Learning',
  'Robotics',
  'AI Safety',
  'Industry News',
  'OpenAI',
  'Google',
  'Microsoft',
  'Anthropic',
  'Startup News',
  'Funding',
  'Product Launch'
]

const availableSources = [
  'OpenAI Blog',
  'DeepMind Blog',
  'Google AI Blog',
  'MIT AI News',
  'TechCrunch AI',
  'VentureBeat AI',
  'NVIDIA Blog',
  'Anthropic News',
  'Stanford HAI',
  'Berkeley AI Research',
  'Hugging Face Blog',
  'AI News'
]

interface Props {
  onFiltersChange?: (filters: FilterState) => void
}

export function ArticleFilters({ onFiltersChange }: Props) {
  const [filters, setFilters] = useState<FilterState>({
    categories: [],
    sources: [],
    minRelevance: 0,
    dateRange: 'all',
    tier: 'all'
  })

  const updateFilter = <K extends keyof FilterState>(
    key: K, 
    value: FilterState[K]
  ) => {
    const newFilters = { ...filters, [key]: value }
    setFilters(newFilters)
    
    // Notify parent component of filter changes
    if (onFiltersChange) {
      onFiltersChange(newFilters)
    }
    
    // Also dispatch a custom event for components that need to listen
    window.dispatchEvent(new CustomEvent('filtersChanged', {
      detail: newFilters
    }))
  }

  // Notify parent of initial filters
  useEffect(() => {
    if (onFiltersChange) {
      onFiltersChange(filters)
    }
  }, [])

  const toggleCategory = (category: string) => {
    updateFilter('categories', 
      filters.categories.includes(category)
        ? filters.categories.filter(c => c !== category)
        : [...filters.categories, category]
    )
  }

  const toggleSource = (source: string) => {
    updateFilter('sources',
      filters.sources.includes(source)
        ? filters.sources.filter(s => s !== source)
        : [...filters.sources, source]
    )
  }

  const clearAllFilters = () => {
    const clearedFilters = {
      categories: [],
      sources: [],
      minRelevance: 0,
      dateRange: 'all' as const,
      tier: 'all' as const
    }
    setFilters(clearedFilters)
    
    // Notify parent component of cleared filters
    if (onFiltersChange) {
      onFiltersChange(clearedFilters)
    }
    
    // Dispatch event for cleared filters
    window.dispatchEvent(new CustomEvent('filtersChanged', {
      detail: clearedFilters
    }))
  }

  const hasActiveFilters = 
    filters.categories.length > 0 || 
    filters.sources.length > 0 || 
    filters.minRelevance > 0 || 
    filters.dateRange !== 'all' ||
    filters.tier !== 'all'

  return (
    <div className="space-y-4">
      {/* Filter Header */}
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg flex items-center space-x-2">
              <Filter className="h-5 w-5" />
              <span>Filters</span>
            </CardTitle>
            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAllFilters}
                className="text-red-600 hover:text-red-700"
              >
                <X className="h-4 w-4 mr-1" />
                Clear All
              </Button>
            )}
          </div>
          <CardDescription>
            Refine your article search
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Date Range */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Published Date</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Select 
            value={filters.dateRange} 
            onValueChange={(value: any) => updateFilter('dateRange', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Time</SelectItem>
              <SelectItem value="24h">Last 24 Hours</SelectItem>
              <SelectItem value="7d">Last 7 Days</SelectItem>
              <SelectItem value="30d">Last 30 Days</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Source Tier */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Source Tier</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <Select 
            value={filters.tier} 
            onValueChange={(value: any) => updateFilter('tier', value)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Tiers</SelectItem>
              <SelectItem value="1">Tier 1 (Premium)</SelectItem>
              <SelectItem value="2">Tier 2 (High Quality)</SelectItem>
              <SelectItem value="3">Tier 3 (Broad Coverage)</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      {/* Relevance Score */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Minimum Relevance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Slider
            value={[filters.minRelevance]}
            onValueChange={([value]) => updateFilter('minRelevance', value)}
            max={1}
            min={0}
            step={0.1}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>0%</span>
            <span className="font-medium">
              {(filters.minRelevance * 100).toFixed(0)}%
            </span>
            <span>100%</span>
          </div>
        </CardContent>
      </Card>

      {/* Categories */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Categories</CardTitle>
          {filters.categories.length > 0 && (
            <CardDescription>
              {filters.categories.length} selected
            </CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex flex-wrap gap-2">
            {availableCategories.map((category) => (
              <Badge
                key={category}
                variant={filters.categories.includes(category) ? "default" : "outline"}
                className="cursor-pointer hover:opacity-80 text-xs"
                onClick={() => toggleCategory(category)}
              >
                {category}
                {filters.categories.includes(category) && (
                  <X className="h-3 w-3 ml-1" />
                )}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Sources */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm">Sources</CardTitle>
          {filters.sources.length > 0 && (
            <CardDescription>
              {filters.sources.length} selected
            </CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="space-y-1">
            {availableSources.map((source) => (
              <Badge
                key={source}
                variant={filters.sources.includes(source) ? "default" : "outline"}
                className="cursor-pointer hover:opacity-80 text-xs w-full justify-between"
                onClick={() => toggleSource(source)}
              >
                <span>{source}</span>
                {filters.sources.includes(source) && (
                  <X className="h-3 w-3" />
                )}
              </Badge>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}