import { useState } from 'react'
import { Guitar, Music, Piano, Sliders, Sparkles, Waves } from 'lucide-react'
import toast from 'react-hot-toast'
import { generateMusic } from '../services/api'

const INSTRUMENTS = [
  { id: 'piano', label: 'Piano', icon: Piano },
  { id: 'guitar', label: 'Guitar', icon: Guitar },
  { id: 'violin', label: 'Violin', icon: Waves },
  { id: 'flute', label: 'Flute', icon: Waves },
  { id: 'trumpet', label: 'Trumpet', icon: Music },
  { id: 'organ', label: 'Organ', icon: Piano },
]

const STYLES = [
  { id: 'cinematic', label: 'Cinematic', detail: 'wide chords, dramatic phrasing' },
  { id: 'ambient', label: 'Ambient', detail: 'slow, spacious, atmospheric' },
  { id: 'classical', label: 'Classical', detail: 'balanced, melodic movement' },
  { id: 'jazz', label: 'Jazz', detail: 'sevenths, swing, color tones' },
  { id: 'electronic', label: 'Electronic', detail: 'tight pulse, minor color' },
]

const KEYS = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'Bb', 'Eb', 'F#']

export default function GenerateMusicForm({ onGenerated }) {
  const [form, setForm] = useState({
    num_notes: 160,
    temperature: 0.9,
    instrument: 'piano',
    style: 'cinematic',
    key: 'C',
    tempo: 92,
    density: 0.75,
    harmony: true,
  })
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
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-blue-700 font-semibold">
          <Sliders size={18} />
          <span>Advanced Composition Studio</span>
        </div>
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-500">LSTM + arrangement engine</span>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Composition Style</label>
        <div className="grid gap-2 sm:grid-cols-2">
          {STYLES.map(style => (
            <button
              key={style.id}
              type="button"
              onClick={() => set('style', style.id)}
              className={`rounded-md border p-3 text-left transition ${
                form.style === style.id
                  ? 'border-blue-600 bg-blue-50 text-blue-950'
                  : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <span className="block text-sm font-semibold">{style.label}</span>
              <span className="block text-xs text-gray-500">{style.detail}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Key</label>
          <select
            value={form.key}
            onChange={e => set('key', e.target.value)}
            className="input-field"
          >
            {KEYS.map(key => <option key={key} value={key}>{key}</option>)}
          </select>
        </div>

        <label className="flex items-center justify-between gap-3 rounded-md border border-gray-300 bg-white px-4 py-3">
          <span>
            <span className="block text-sm font-medium text-gray-800">Harmony Layer</span>
            <span className="block text-xs text-gray-500">Adds chord voicings around the generated melody</span>
          </span>
          <input
            type="checkbox"
            checked={form.harmony}
            onChange={e => set('harmony', e.target.checked)}
            className="h-5 w-5 accent-blue-600"
          />
        </label>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Number of Notes: <span className="text-gray-950">{form.num_notes}</span></label>
        <input
          type="range" min={20} max={500} step={10}
          value={form.num_notes}
          onChange={e => set('num_notes', Number(e.target.value))}
          className="w-full accent-blue-600"
        />
        <div className="flex justify-between text-xs text-gray-600"><span>20</span><span>500</span></div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">
          Creativity: <span className="text-gray-950">{form.temperature.toFixed(1)}</span>
          <span className="text-gray-600 ml-2">(lower = conservative, higher = creative)</span>
        </label>
        <input
          type="range" min={0.1} max={2.0} step={0.1}
          value={form.temperature}
          onChange={e => set('temperature', Number(e.target.value))}
          className="w-full accent-blue-600"
        />
        <div className="flex justify-between text-xs text-gray-600"><span>0.1</span><span>2.0</span></div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Tempo: <span className="text-gray-950">{form.tempo} BPM</span></label>
          <input
            type="range" min={55} max={170} step={1}
            value={form.tempo}
            onChange={e => set('tempo', Number(e.target.value))}
            className="w-full accent-blue-600"
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium text-gray-700">Density: <span className="text-gray-950">{Math.round(form.density * 100)}%</span></label>
          <input
            type="range" min={0.2} max={1} step={0.05}
            value={form.density}
            onChange={e => set('density', Number(e.target.value))}
            className="w-full accent-blue-600"
          />
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Instrument</label>
        <div className="grid grid-cols-3 gap-2">
          {INSTRUMENTS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => set('instrument', id)}
              className={`flex min-h-12 items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors ${
                form.instrument === id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              <Icon size={16} />
              {label}
            </button>
          ))}
        </div>
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full flex items-center justify-center gap-2">
        <Sparkles size={18} />
        {loading ? 'Composing...' : 'Generate Advanced Music'}
      </button>
    </form>
  )
}
