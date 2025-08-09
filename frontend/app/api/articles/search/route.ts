import { NextRequest, NextResponse } from 'next/server'
import { createServerSupabase } from '@/lib/supabase'
import { cookies } from 'next/headers'

export async function POST(request: NextRequest) {
  try {
    const { query, searchType = 'text', limit = 20 } = await request.json()
    
    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      )
    }

    const supabase = createServerSupabase(cookies)

    if (searchType === 'semantic') {
      // TODO: Implement semantic search with OpenAI embeddings
      // For now, fall back to text search
      console.log('Semantic search requested but not yet implemented, falling back to text search')
    }

    // Full-text search implementation
    const { data: articles, error } = await supabase
      .from('articles')
      .select(`
        *,
        source:news_sources(
          id,
          name,
          tier,
          category
        )
      `)
      .or(`title.ilike.%${query}%,content.ilike.%${query}%,summary.ilike.%${query}%`)
      .eq('processed', true)
      .order('relevance_score', { ascending: false })
      .limit(limit)

    if (error) {
      console.error('Search error:', error)
      return NextResponse.json(
        { error: 'Search failed' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      data: articles || [],
      searchType,
      query,
      count: articles?.length || 0
    })

  } catch (error) {
    console.error('Search API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}