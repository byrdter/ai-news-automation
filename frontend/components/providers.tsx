'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () => new QueryClient({
      defaultOptions: {
        queries: {
          // Cache for 5 minutes by default
          staleTime: 5 * 60 * 1000,
          // Keep data in cache for 10 minutes
          gcTime: 10 * 60 * 1000,
          // Retry failed requests 3 times
          retry: 3,
          // Don't refetch on window focus in development
          refetchOnWindowFocus: process.env.NODE_ENV === 'production',
        },
      },
    })
  )

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}