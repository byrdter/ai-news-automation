'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { debounce } from '@/lib/utils'
import { Search, Sparkles, Filter } from 'lucide-react'

const searchSuggestions = [
  'Large Language Models',
  'GPT-4 improvements',
  'AI safety research',
  'Computer vision breakthroughs',
  'Robotics automation',
  'Machine learning algorithms',
  'Neural network architecture',
  'OpenAI announcements',
  'Google AI research',
  'Autonomous vehicles',
  'AI ethics',
  'Generative AI applications'
]

export function ArticleSearch() {
  const [query, setQuery] = useState('')
  const [searchType, setSearchType] = useState<'text' | 'semantic'>('text')
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = debounce(async (searchQuery: string) => {
    if (!searchQuery.trim()) return
    
    setIsLoading(true)
    try {
      if (searchType === 'semantic') {
        // Use POST endpoint for semantic search
        const response = await fetch('/api/articles/search', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: searchQuery,
            type: 'semantic',
            limit: 20
          })
        })
        
        if (!response.ok) {
          throw new Error(`Semantic search failed: ${response.status}`)
        }
        
        const results = await response.json()
        console.log('Semantic search results:', results)
        
        // Dispatch search results to parent component or global state
        // This would typically update the ArticleList component
        window.dispatchEvent(new CustomEvent('searchResults', {
          detail: {
            type: 'semantic',
            query: searchQuery,
            results: results.articles
          }
        }))
      } else {
        // Text search uses query parameters
        const params = new URLSearchParams({
          search: searchQuery,
          limit: '20'
        })
        
        const response = await fetch(`/api/articles?${params}`)
        
        if (!response.ok) {
          throw new Error(`Text search failed: ${response.status}`)
        }
        
        const results = await response.json()
        console.log('Text search results:', results)
        
        // Dispatch search results to parent component
        window.dispatchEvent(new CustomEvent('searchResults', {
          detail: {
            type: 'text',
            query: searchQuery,
            results: results.articles
          }
        }))
      }
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setIsLoading(false)
    }
  }, 500)

  const handleInputChange = (value: string) => {
    setQuery(value)
    handleSearch(value)
  }

  const handleSemanticSearch = async () => {
    if (!query.trim()) return
    
    setSearchType('semantic')
    setIsLoading(true)
    
    try {
      const response = await fetch('/api/articles/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          type: 'semantic',
          limit: 20
        })
      })
      
      if (!response.ok) {
        throw new Error(`Semantic search failed: ${response.status}`)
      }
      
      const results = await response.json()
      console.log('Semantic search results:', results)
      
      // Dispatch search results to parent component
      window.dispatchEvent(new CustomEvent('searchResults', {
        detail: {
          type: 'semantic',
          query: query,
          results: results.articles
        }
      }))
    } catch (error) {
      console.error('Semantic search failed:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Search className="h-5 w-5" />
          <span>Search Articles</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Search Input */}
        <div className="flex space-x-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search by title, content, or keywords..."
              value={query}
              onChange={(e) => handleInputChange(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <Select 
            value={searchType} 
            onValueChange={(value: 'text' | 'semantic') => setSearchType(value)}
          >
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="text">Text</SelectItem>
              <SelectItem value="semantic">Semantic</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Search Type Description */}
        <div className="text-sm text-gray-500 bg-gray-50 rounded-lg p-3">
          {searchType === 'text' ? (
            <div className="flex items-start space-x-2">
              <Filter className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <div>
                <strong>Text Search:</strong> Find articles by exact keyword matches in titles, content, and metadata.
                Fast and precise for specific terms.
              </div>
            </div>
          ) : (
            <div className="flex items-start space-x-2">
              <Sparkles className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <div>
                <strong>Semantic Search:</strong> Find articles by meaning and context using AI embeddings.
                Discovers related content even without exact keyword matches.
              </div>
            </div>
          )}
        </div>

        {/* Semantic Search Button */}
        {searchType === 'semantic' && (
          <Button
            onClick={handleSemanticSearch}
            disabled={!query.trim() || isLoading}
            className="w-full"
            variant="secondary"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            {isLoading ? 'Searching...' : 'Search by Meaning'}
          </Button>
        )}

        {/* Search Suggestions */}
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Popular Searches:</p>
          <div className="flex flex-wrap gap-2">
            {searchSuggestions.slice(0, 8).map((suggestion) => (
              <Badge
                key={suggestion}
                variant="outline"
                className="cursor-pointer hover:bg-blue-50 hover:border-blue-200 text-xs"
                onClick={() => handleInputChange(suggestion)}
              >
                {suggestion}
              </Badge>
            ))}
          </div>
        </div>

        {/* Search Stats */}
        {query && (
          <div className="pt-2 border-t border-gray-200">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>
                {isLoading ? 'Searching...' : `Search: "${query}"`}
              </span>
              <span>
                {searchType === 'semantic' ? 'AI-powered' : 'Text match'}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}