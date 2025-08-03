interface CashFlowChartProps {
  data: any[]
  loading: boolean
}

export default function CashFlowChart({ data, loading }: CashFlowChartProps) {
  if (loading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    )
  }

  return (
    <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
      <div className="text-center">
        <p className="text-gray-600 mb-2">Cash Flow Chart</p>
        <p className="text-sm text-gray-500">Chart.js integration coming soon</p>
        <div className="mt-4 text-xs text-gray-400">
          Data Points: {data.length}
        </div>
      </div>
    </div>
  )
}
