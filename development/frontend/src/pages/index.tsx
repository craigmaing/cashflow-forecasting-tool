import { useState, useEffect } from 'react'
import Head from 'next/head'
import DashboardLayout from '../components/Layout/DashboardLayout'
import CashFlowChart from '../components/Charts/CashFlowChart'
import MetricsCards from '../components/Dashboard/MetricsCards'
import TransactionList from '../components/Transactions/TransactionList'
import ForecastPanel from '../components/Forecasting/ForecastPanel'

export default function Dashboard() {
  const [cashFlowData, setCashFlowData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Mock data for now
      const mockData = [
        { date: '2025-01-01', inflow: 50000, outflow: 30000, balance: 120000 },
        { date: '2025-01-02', inflow: 45000, outflow: 35000, balance: 130000 },
        { date: '2025-01-03', inflow: 60000, outflow: 40000, balance: 150000 },
      ]
      setCashFlowData(mockData)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
      setLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <Head>
        <title>Cash Flow Dashboard - Forecasting Tool</title>
        <meta name="description" content="Enterprise cash flow forecasting dashboard" />
      </Head>

      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Cash Flow Dashboard</h1>
          <p className="text-gray-600">Monitor and forecast your organization's cash flow</p>
        </div>

        {/* Metrics Cards */}
        <MetricsCards loading={loading} />

        {/* Cash Flow Chart */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Cash Flow Trends</h2>
          <CashFlowChart data={cashFlowData} loading={loading} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Transactions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
            <TransactionList limit={5} />
          </div>

          {/* Forecast Panel */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">AI Forecast</h2>
            <ForecastPanel />
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
