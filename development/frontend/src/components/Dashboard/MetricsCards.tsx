import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid'

interface MetricsCardsProps {
  loading: boolean
}

export default function MetricsCards({ loading }: MetricsCardsProps) {
  const metrics = [
    {
      title: 'Current Balance',
      value: '$1,234,567',
      change: '+12.3%',
      trend: 'up',
      color: 'text-success-600'
    },
    {
      title: 'Monthly Inflow',
      value: '$456,789',
      change: '+8.2%',
      trend: 'up',
      color: 'text-success-600'
    },
    {
      title: 'Monthly Outflow',
      value: '$234,567',
      change: '-3.1%',
      trend: 'down',
      color: 'text-danger-600'
    },
    {
      title: '30-Day Forecast',
      value: '$1,456,234',
      change: '+15.7%',
      trend: 'up',
      color: 'text-success-600'
    }
  ]

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-300 rounded w-3/4 mb-2" />
            <div className="h-8 bg-gray-300 rounded w-1/2 mb-2" />
            <div className="h-4 bg-gray-300 rounded w-1/4" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6" data-testid="metrics-cards">
      {metrics.map((metric, index) => (
        <div key={index} className="bg-white rounded-lg shadow p-6" data-testid="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">{metric.title}</p>
              <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
            </div>
          </div>
          <div className={`flex items-center mt-2 ${metric.color}`}>
            {metric.trend === 'up' ? (
              <ArrowUpIcon className="w-4 h-4 mr-1" />
            ) : (
              <ArrowDownIcon className="w-4 h-4 mr-1" />
            )}
            <span className="text-sm font-medium">{metric.change}</span>
          </div>
        </div>
      ))}
    </div>
  )
}
