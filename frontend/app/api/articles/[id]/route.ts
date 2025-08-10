import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/supabase'
import type { ArticleWithSource } from '@/types/database'

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = createClient()
    const articleId = params.id

    console.log('Fetching article with ID:', articleId)

    // Fetch article with source information
    const { data: article, error } = await supabase
      .from('articles')
      .select(`
        *,
        source:news_sources (*)
      `)
      .eq('id', articleId)
      .single()

    if (error) {
      console.error('Supabase error:', error)
      if (error.code === 'PGRST116') {
        return NextResponse.json(
          { error: 'Article not found' },
          { status: 404 }
        )
      }
      throw error
    }

    if (!article) {
      return NextResponse.json(
        { error: 'Article not found' },
        { status: 404 }
      )
    }

    // Transform the data to match our types
    const articleWithSource: ArticleWithSource = {
      ...article,
      sources: article.source // Handle the alias
    }

    console.log('Article fetched successfully:', article.title)

    return NextResponse.json(articleWithSource)

  } catch (error) {
    console.error('Error fetching article:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}