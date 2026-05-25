import { useState } from 'react'
import { Sliders, Music } from 'lucide-react'
import toast from 'react-hot-toast'
import { generateMusic } from '../services/api'

const INSTRUMENTS = ['piano', 'guitar', 'violin', 'flute', 'trumpet', 'organ']

export default function GenerateMusicForm({ onGenerated }) {
  const [form, setForm] = useState({ num_notes: 100, temperature: 1.0, instrument: 'piano' })
  const [loading, setLoading] = useState(false)

  const set = (k, v) => setForm(prev => ({ ...prev, [k]: v }))

const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await generateMusic(form)
      toast.success('Music generated!')
      onGenerated?.(data)
    } catch (err) {
      const errorMsg = err.message || 'Generation failed'
      if (errorMsg.includes('not found') || errorMsg.includes('train')) {
        toast.error('Model not trained yet. Please train the model first on the Training page.')
      } else {
        toast.error(errorMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card space-y-6">
      <div className="flex items-center gap-2 text-blue-600 font-semibold">
        <Sliders size={18} />
        <span>Generation Settings</span>
      </div>

      {/* Notes */}
      <div className="space-y-2">
        <label className="text-sm text-gray-400">Number of Notes: <span className="text-white">{form.num_notes}</span></label>
        <input
          type="range" min={20} max={500} step={10}
          value={form.num_notes}
          onChange={e => set('num_notes', Number(e.target.value))}
          className="w-full accent-violet-500"
        />
        <div className="flex justify-between text-xs text-gray-600"><span>20</span><span>500</span></div>
      </div>

      {/* Temperature */}
      <div className="space-y-2">
        <label className="text-sm text-gray-400">
          Temperature: <span className="text-white">{form.temperature.toFixed(1)}</span>
          <span className="text-gray-600 ml-2">(lower = conservative, higher = creative)</span>
        </label>
        <input
          type="range" min={0.1} max={2.0} step={0.1}
          value={form.temperature}
          onChange={e => set('temperature', Number(e.target.value))}
          className="w-full accent-violet-500"
        />
        <div className="flex justify-between text-xs text-gray-600"><span>0.1</span><span>2.0</span></div>
      </div>

      {/* Instrument */}
      <div className="space-y-2">
        <label className="text-sm text-gray-700">Instrument</label>
        <div className="grid grid-cols-3 gap-2">
          {INSTRUMENTS.map(inst => (
            <button
              key={inst}
              type="button"
              onClick={() => set('instrument', inst)}
              className={`py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                form.instrument === inst
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {inst}
            </button>
          ))}
        </div>
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
        <Music size={18} />
        {loading ? 'Generating...' : 'Generate Music'}
      </button>
    </form>
  )
}
