interface TransactionListProps {
  limit?: number
}

export default function TransactionList({ limit = 10 }: TransactionListProps) {
  const mockTransactions = [
    { id: '1', date: '2025-08-03', description: 'Client Payment - ABC Corp', amount: 15000, type: 'income' },
    { id: '2', date: '2025-08-02', description: 'Office Rent', amount: -3500, type: 'expense' },
    { id: '3', date: '2025-08-02', description: 'Software Subscription', amount: -299, type: 'expense' },
    { id: '4', date: '2025-08-01', description: 'Service Revenue', amount: 8500, type: 'income' },
    { id: '5', date: '2025-08-01', description: 'Marketing Campaign', amount: -1200, type: 'expense' },
  ].slice(0, limit)

  return (
    <div className="space-y-3" data-testid="transaction-list">
      {mockTransactions.map((transaction) => (
        <div key={transaction.id} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg">
          <div className="flex-1">
            <p className="font-medium text-gray-900">{transaction.description}</p>
            <p className="text-sm text-gray-500">{transaction.date}</p>
          </div>
          <div className={`font-semibold ${
            transaction.amount > 0 ? 'text-success-600' : 'text-danger-600'
          }`}>
            {transaction.amount > 0 ? '+' : ''}${Math.abs(transaction.amount).toLocaleString()}
          </div>
        </div>
      ))}
      
      {limit && mockTransactions.length >= limit && (
        <div className="text-center pt-3">
          <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
            View All Transactions
          </button>
        </div>
      )}
    </div>
  )
}
