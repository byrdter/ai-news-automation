'use client'

import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  getTimeAgo, 
  truncateText, 
  calculateRelevanceColor, 
  calculateSentimentColor, 
  getSentimentLabel 
} from '@/lib/utils'
import { ExternalLink, Eye, Share2, Clock, TrendingUp } from 'lucide-react'
import type { ArticleWithSource } from '@/types/database'

interface ArticleCardProps {
  article: ArticleWithSource
}

export function ArticleCard({ article }: ArticleCardProps) {
  const getTierColor = (tier: number) => {
    switch (tier) {
      case 1: return 'text-green-700 bg-green-100 border-green-200'
      case 2: return 'text-blue-700 bg-blue-100 border-blue-200'
      case 3: return 'text-yellow-700 bg-yellow-100 border-yellow-200'
      default: return 'text-gray-700 bg-gray-100 border-gray-200'
    }
  }

  return (
    <Card className="group hover:shadow-lg transition-all duration-200 hover:-translate-y-1">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between mb-2">
          <Badge 
            variant="outline" 
            className={`text-xs ${getTierColor(article.source.tier)}`}
          >
            {article.source.name} • Tier {article.source.tier}
          </Badge>
          <div className="flex items-center space-x-1 text-xs text-gray-500">
            <Clock className="h-3 w-3" />
            <span>{getTimeAgo(article.published_at || article.created_at)}</span>
          </div>
        </div>

        <CardTitle className="text-lg leading-tight">
          <Link 
            href={`/articles/${article.id}`}
            className="hover:text-blue-600 transition-colors"
          >
            {truncateText(article.title, 100)}
          </Link>
        </CardTitle>

        {article.author && (
          <CardDescription>By {article.author}</CardDescription>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Summary */}
        {article.summary && (
          <p className="text-sm text-gray-600 leading-relaxed">
            {truncateText(article.summary, 150)}
          </p>
        )}

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="flex items-center justify-between">
            <span className="text-gray-500">Relevance</span>
            <Badge className={calculateRelevanceColor(article.relevance_score)}>
              {(article.relevance_score * 100).toFixed(0)}%
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-500">Sentiment</span>
            <Badge className={calculateSentimentColor(article.sentiment_score)}>
              {getSentimentLabel(article.sentiment_score)}
            </Badge>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-500">Quality</span>
            <div className="w-12 bg-gray-200 rounded-full h-1.5">
              <div 
                className="bg-green-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${article.quality_score * 100}%` }}
              />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-500">Words</span>
            <span className="font-medium">{article.word_count || 'N/A'}</span>
          </div>
        </div>

        {/* Categories */}
        {article.categories && article.categories.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {article.categories.slice(0, 3).map((category) => (
              <Badge 
                key={category} 
                variant="secondary" 
                className="text-xs px-2 py-0.5"
              >
                {category}
              </Badge>
            ))}
            {article.categories.length > 3 && (
              <Badge variant="secondary" className="text-xs px-2 py-0.5">
                +{article.categories.length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Engagement */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div className="flex items-center space-x-3 text-xs text-gray-500">
            <div className="flex items-center space-x-1">
              <Eye className="h-3 w-3" />
              <span>{article.view_count}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Share2 className="h-3 w-3" />
              <span>{article.share_count}</span>
            </div>
            {article.urgency_score > 0.7 && (
              <div className="flex items-center space-x-1 text-red-500">
                <TrendingUp className="h-3 w-3" />
                <span>Urgent</span>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-8 px-2 opacity-0 group-hover:opacity-100 transition-opacity"
              asChild
            >
              <Link href={article.url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="h-3 w-3" />
              </Link>
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}