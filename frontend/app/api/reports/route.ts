import { NextRequest, NextResponse } from 'next/server'
import { createServerSupabase } from '@/lib/supabase'
import { cookies } from 'next/headers'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '0')
    const limit = parseInt(searchParams.get('limit') || '20')
    
    const supabase = createServerSupabase(cookies)
    
    // Query reports table
    const { data: reports, error, count } = await supabase
      .from('reports')
      .select('*', { count: 'exact' })
      .order('created_at', { ascending: false })
      .range(page * limit, (page + 1) * limit - 1)

    if (error) {
      console.error('Database error:', error)
      // If table doesn't exist or other error, return empty result
      return NextResponse.json({
        reports: [],
        hasMore: false,
        pagination: {
          page,
          limit,
          total: 0,
          totalPages: 0
        }
      })
    }

    const response = {
      reports: reports || [],
      hasMore: (reports?.length || 0) === limit,
      pagination: {
        page,
        limit,
        total: count || 0,
        totalPages: Math.ceil((count || 0) / limit)
      }
    }

    return NextResponse.json(response)

  } catch (error) {
    console.error('API error:', error)
    // Return empty result instead of error to prevent frontend issues
    return NextResponse.json({
      reports: [],
      hasMore: false,
      pagination: {
        page: 0,
        limit: 20,
        total: 0,
        totalPages: 0
      }
    })
  }
}