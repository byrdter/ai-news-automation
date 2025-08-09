import { NextRequest, NextResponse } from 'next/server'
import { createServerSupabase } from '@/lib/supabase'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '0')
    const limit = parseInt(searchParams.get('limit') || '20')
    const category = searchParams.get('category')
    const source = searchParams.get('source')
    const minRelevance = parseFloat(searchParams.get('minRelevance') || '0')
    
    const supabase = createServerSupabase(cookies)
    
    // Build query
    let query = supabase
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
      .eq('processed', true)
      .order('published_at', { ascending: false })
      .range(page * limit, (page + 1) * limit - 1)

    // Apply filters
    if (category) {
      query = query.contains('categories', [category])
    }
    
    if (source) {
      query = query.eq('source.name', source)
    }
    
    if (minRelevance > 0) {
      query = query.gte('relevance_score', minRelevance)
    }

    const { data: articles, error, count } = await query

    if (error) {
      console.error('Database error:', error)
      return NextResponse.json(
        { error: 'Failed to fetch articles' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      articles: articles || [],
      pagination: {
        page,
        limit,
        total: count || 0,
        hasMore: (articles?.length || 0) === limit
      }
    })

  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}