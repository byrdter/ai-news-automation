import { NextRequest, NextResponse } from 'next/server'
import { createServerSupabase } from '@/lib/supabase'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '0')
    const limit = parseInt(searchParams.get('limit') || '20')
    
    // Parse filter parameters exactly as specified
    const categoriesParam = searchParams.get('categories')
    const categories = categoriesParam ? categoriesParam.split(',').filter(Boolean) : []
    
    const sourcesParam = searchParams.get('sources') 
    const sources = sourcesParam ? sourcesParam.split(',').filter(Boolean) : []
    
    const sourceTier = searchParams.get('sourceTier') ? parseInt(searchParams.get('sourceTier')!) : null
    
    const minRelevance = parseFloat(searchParams.get('min_relevance') || '0')
    const search = searchParams.get('search') || ''
    const startDate = searchParams.get('start_date')
    const endDate = searchParams.get('end_date')

    // Debug logging as requested
    console.log('API Received params:', {
      categories,
      sources,
      sourceTier,
      minRelevance,
      startDate,
      endDate,
      search,
      page,
      limit
    })
    
    const supabase = createServerSupabase(cookies)
    
    // Build base query with proper JOIN for source information
    let query = supabase
      .from('articles')
      .select(`
        *,
        news_sources!inner(
          id,
          name,
          tier,
          category
        )
      `, { count: 'exact' })
      .order('published_at', { ascending: false })

    // Apply category filtering using PostgreSQL JSON array filtering
    if (categories.length > 0) {
      // Use Supabase contains method for JSON array filtering
      // This implements the PostgreSQL @> operator for JSON arrays
      if (categories.length === 1) {
        // Single category: articles.categories @> '["CategoryName"]'::jsonb
        query = query.contains('categories', [categories[0]])
        console.log('Applied single category filter:', categories[0])
      } else {
        // Multiple categories with OR logic
        const orConditions = categories.map(cat => `categories.cs.{${cat}}`).join(',')
        query = query.or(orConditions)
        console.log('Applied multiple category filter (OR):', categories)
      }
    }
    
    // Apply source tier filtering
    if (sourceTier !== null) {
      query = query.eq('news_sources.tier', sourceTier)
      console.log('Applied source tier filter:', sourceTier)
    }
    
    // Apply specific source name filtering
    if (sources.length > 0) {
      query = query.in('news_sources.name', sources)
      console.log('Applied source name filter:', sources)
    }
    
    // Apply relevance score filtering
    if (minRelevance > 0) {
      query = query.gte('relevance_score', minRelevance)
      console.log('Applied relevance filter:', minRelevance)
    }
    
    // Apply search filter
    if (search) {
      query = query.or(`title.ilike.%${search}%,content.ilike.%${search}%`)
      console.log('Applied search filter:', search)
    }
    
    // Apply date range filtering
    if (startDate) {
      query = query.gte('published_at', startDate)
      console.log('Applied start date filter:', startDate)
    }
    if (endDate) {
      query = query.lte('published_at', endDate)  
      console.log('Applied end date filter:', endDate)
    }

    // Apply pagination
    query = query.range(page * limit, (page + 1) * limit - 1)

    const { data: articles, error, count } = await query

    // Log actual database query results
    console.log('Database query result count:', articles?.length || 0)
    console.log('Total count from database:', count)

    if (error) {
      console.error('Database error:', error)
      return NextResponse.json(
        { error: 'Failed to fetch articles' },
        { status: 500 }
      )
    }

    // Transform articles to match expected format
    const transformedArticles = (articles || []).map(article => ({
      ...article,
      source: article.news_sources // Flatten the nested source data
    }))

    const response = {
      articles: transformedArticles,
      hasMore: (articles?.length || 0) === limit,
      pagination: {
        page,
        limit,
        total: count || 0,
        totalPages: Math.ceil((count || 0) / limit)
      }
    }

    console.log('API Response summary:', {
      articlesReturned: transformedArticles.length,
      totalInDatabase: count,
      hasMore: response.hasMore,
      page,
      filtersApplied: {
        categories: categories.length > 0 ? categories : 'none',
        sourceTier: sourceTier || 'none', 
        sources: sources.length > 0 ? sources : 'none',
        minRelevance: minRelevance > 0 ? minRelevance : 'none',
        search: search || 'none',
        dateRange: (startDate || endDate) ? `${startDate} to ${endDate}` : 'none'
      }
    })

    return NextResponse.json(response)

  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}