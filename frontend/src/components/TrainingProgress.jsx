import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function TrainingProgress({ status }) {
  const { state, epoch, total_epochs, loss = [], accuracy = [], message } = status

  const chartData = loss.map((l, i) => ({
    epoch: i + 1,
    loss: l,
    accuracy: accuracy[i] ?? 0,
  }))

  const pct = total_epochs > 0 ? Math.round((epoch / total_epochs) * 100) : 0

  const stateColor = {
    idle: 'text-gray-700',
    preparing: 'text-yellow-700',
    training: 'text-blue-700',
    completed: 'text-green-700',
    error: 'text-red-700',
  }[state] || 'text-gray-700'

  return (
    <div className="space-y-6">
      {/* Status bar */}
      <div className="card space-y-3">
        <div className="flex items-center justify-between">
          <span className={`font-semibold capitalize ${stateColor}`}>{state}</span>
          <span className="text-sm text-gray-600">{epoch} / {total_epochs} epochs</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-sm text-gray-600">{message}</p>
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-800 mb-4">Training Metrics</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="epoch" stroke="#6b7280" tick={{ fontSize: 11 }} />
              <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#ffffff', border: '1px solid #d1d5db', borderRadius: 6 }}
                labelStyle={{ color: '#111827' }}
              />
              <Legend />
              <Line type="monotone" dataKey="loss" stroke="#2563eb" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="accuracy" stroke="#10b981" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
