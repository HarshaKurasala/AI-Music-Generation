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
    idle: 'text-gray-400',
    preparing: 'text-yellow-400',
    training: 'text-blue-400',
    completed: 'text-green-400',
    error: 'text-red-400',
  }[state] || 'text-gray-400'

  return (
    <div className="space-y-6">
      {/* Status bar */}
      <div className="card space-y-3">
        <div className="flex items-center justify-between">
          <span className={`font-semibold capitalize ${stateColor}`}>{state}</span>
          <span className="text-sm text-gray-400">{epoch} / {total_epochs} epochs</span>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-2">
          <div
            className="bg-violet-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
        <p className="text-sm text-gray-400">{message}</p>
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="card">
          <h3 className="text-sm font-semibold text-gray-300 mb-4">Training Metrics</h3>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="epoch" stroke="#6b7280" tick={{ fontSize: 11 }} />
              <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: '#1f2937', border: '1px solid #374151', borderRadius: 8 }}
                labelStyle={{ color: '#e5e7eb' }}
              />
              <Legend />
              <Line type="monotone" dataKey="loss" stroke="#8b5cf6" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="accuracy" stroke="#10b981" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
