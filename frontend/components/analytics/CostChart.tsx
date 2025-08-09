'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { formatCurrency } from '@/lib/utils'
import { DollarSign } from 'lucide-react'

interface CostData {
  date: string
  cost: number
  cumulativeCost: number
  budget: number
}

async function fetchCostData(): Promise<CostData[]> {
  // TODO: Replace with actual API call
  const data: CostData[] = []
  const now = new Date()
  
  for (let i = 29; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    
    // Simulate realistic cost data
    const dailyCost = Math.random() * 0.05 + 0.01 // $0.01-$0.06 per day
    const cumulativeCost = data.length > 0 
      ? data[data.length - 1].cumulativeCost + dailyCost
      : dailyCost
    
    data.push({
      date: date.toISOString().split('T')[0],
      cost: dailyCost,
      cumulativeCost,
      budget: 3.33 // $100/month = ~$3.33/day
    })
  }
  
  return data
}

export function CostChart() {
  const { data: costData, isLoading, error } = useQuery({
    queryKey: ['cost-data'],
    queryFn: fetchCostData,
    refetchInterval: 300000, // Refresh every 5 minutes
  })

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="h-5 w-5" />
            <span>Daily Cost Analysis</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] flex items-center justify-center">
            <div className="text-gray-500">Loading cost data...</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !costData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <DollarSign className="h-5 w-5" />
            <span>Daily Cost Analysis</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[200px] flex items-center justify-center">
            <div className="text-red-600">Failed to load cost data</div>
          </div>
        </CardContent>
      </Card>
    )
  }

  const totalCost = costData[costData.length - 1]?.cumulativeCost || 0
  const avgDailyCost = totalCost / costData.length
  const monthlyProjection = avgDailyCost * 30

  return (
    <Card className="col-span-1 lg:col-span-2">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <DollarSign className="h-5 w-5" />
          <span>Daily Cost Analysis</span>
        </CardTitle>
        <CardDescription>
          API usage costs over the last 30 days (Target: &lt;$3.33/day)
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4 grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {formatCurrency(totalCost)}
            </div>
            <div className="text-gray-500">Total (30d)</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {formatCurrency(avgDailyCost)}
            </div>
            <div className="text-gray-500">Avg/Day</div>
          </div>
          <div className="text-center">
            <div className={`text-2xl font-bold ${monthlyProjection > 100 ? 'text-red-600' : 'text-green-600'}`}>
              {formatCurrency(monthlyProjection)}
            </div>
            <div className="text-gray-500">Monthly Est.</div>
          </div>
        </div>

        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={costData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="date" 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            />
            <YAxis 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => `$${value.toFixed(3)}`}
            />
            <Tooltip 
              formatter={(value: number) => [formatCurrency(value), 'Cost']}
              labelFormatter={(label) => new Date(label).toLocaleDateString('en-US', { 
                month: 'short', 
                day: 'numeric',
                year: 'numeric'
              })}
            />
            <Line 
              type="monotone" 
              dataKey="cost" 
              stroke="#3b82f6" 
              strokeWidth={2}
              dot={{ fill: '#3b82f6', strokeWidth: 2, r: 3 }}
              activeDot={{ r: 5 }}
            />
          </LineChart>
        </ResponsiveContainer>

        <div className="mt-4 text-xs text-gray-500 text-center">
          Staying well under $100/month budget • Cost per article: ~$0.0037
        </div>
      </CardContent>
    </Card>
  )
}