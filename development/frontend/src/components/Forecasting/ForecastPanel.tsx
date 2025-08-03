import { useState } from 'react'
import { ChartBarIcon, SparklesIcon } from '@heroicons/react/24/outline'

export default function ForecastPanel() {
  const [generating, setGenerating] = useState(false)

  const handleGenerateForecast = async () => {
    setGenerating(true)
    // Simulate API call
    setTimeout(() => {
      setGenerating(false)
    }, 3000)
  }

  return (
    <div className="space-y-4" data-testid="forecast-panel">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <SparklesIcon className="w-5 h-5 text-primary-600" />
          <span className="font-medium">AI Forecast</span>
        </div>
        <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full">
          95% Confidence
        </span>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Next 7 Days</span>
          <span className="font-semibold text-success-600">+$45,230</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Next 30 Days</span>
          <span className="font-semibold text-success-600">+$156,780</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Next 90 Days</span>
          <span className="font-semibold text-primary-600">+$425,690</span>
        </div>
      </div>

      <button
        onClick={handleGenerateForecast}
        disabled={generating}
        className="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
      >
        {generating ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white" />
            <span>Generating...</span>
          </>
        ) : (
          <>
            <ChartBarIcon className="w-4 h-4" />
            <span>Generate New Forecast</span>
          </>
        )}
      </button>

      <div className="text-xs text-gray-500 text-center">
        Last updated: {new Date().toLocaleDateString()}
      </div>
    </div>
  )
}
