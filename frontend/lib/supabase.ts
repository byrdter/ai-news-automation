import { createClient } from '@supabase/supabase-js'
import { createClientComponentClient, createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import type { Database } from '@/types/database'

// Environment variables validation
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

// Client-side Supabase client
export const createClientSupabase = () => createClientComponentClient<Database>()

// Server-side Supabase client (for Server Components and API routes)
export const createServerSupabase = (cookies?: () => any) => {
  if (cookies) {
    return createServerComponentClient<Database>({ cookies })
  }
  
  // Fallback for API routes
  return createClient<Database>(supabaseUrl, supabaseAnonKey)
}

// Direct client for utility functions
export const supabase = createClient<Database>(supabaseUrl, supabaseAnonKey)