import { useEffect, useState } from 'react'
import { FileMusic, RefreshCw, Trash2 } from 'lucide-react'
import MusicPlayer from '../components/MusicPlayer'
import { getGeneratedFiles, deleteGeneratedFiles } from '../services/api'

export default function Results() {
  const [files, setFiles] = useState([])
  const [selected, setSelected] = useState(null)
  const [loading, setLoading] = useState(false)
  const [deleting, setDeleting] = useState(null)
  const [error, setError] = useState(null)

  const refresh = async () => {
    setLoading(true)
    try {
      const { data } = await getGeneratedFiles()
      setFiles(data.files)
      if (data.files.length > 0 && !selected) setSelected(data.files[0])
      setError(null)
    } catch (err) {
      setError(err.message)
    }
    setLoading(false)
  }

  const handleDelete = async (filename) => {
    if (!confirm(`Delete ${filename}?`)) return

    setDeleting(filename)
    setError(null)
    try {
      await deleteGeneratedFiles([filename])
      if (selected === filename) setSelected(null)
      await refresh()
    } catch (err) {
      setError(err.message)
    } finally {
      setDeleting(null)
    }
  }

  useEffect(() => { refresh() }, [])

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Generated Music</h1>
          <p className="text-gray-700 mt-1">All your AI-generated MIDI compositions.</p>
        </div>
        <button onClick={refresh} disabled={loading} className="btn-secondary flex items-center gap-2">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {files.length === 0 ? (
        <div className="card text-center py-16 text-gray-700">
          <FileMusic size={40} className="mx-auto mb-3 opacity-30" />
          <p>No generated files yet. Go to the Generator page to create music.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {error && (
            <div className="bg-red-100 border border-red-300 rounded-lg p-3 text-red-800 text-sm">
              {error}
            </div>
          )}

          {/* Select Dropdown */}
          <div className="card">
            <label className="block text-sm text-gray-700 mb-2">Select File to Play</label>
            <select
              value={selected || ''}
              onChange={(e) => setSelected(e.target.value)}
              className="w-full bg-white border border-gray-300 rounded-lg px-4 py-2 text-gray-900 focus:outline-none focus:border-blue-500 transition-colors"
            >
              <option value="">-- Choose a file --</option>
              {files.map((f) => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>

          {/* File Grid with List and Player */}
          <div className="grid md:grid-cols-3 gap-6">
            {/* File list */}
            <div className="md:col-span-1 space-y-2">
              {files.map((f, i) => (
                <div key={i} className={`rounded-xl overflow-hidden transition-colors ${
                  selected === f ? 'bg-blue-500 text-white' : 'glass hover:bg-gray-100'
                }`}>
                  <div className="flex items-center gap-2 p-3">
                    <button
                      onClick={() => setSelected(f)}
                      className="flex-1 text-left flex items-center gap-2 min-w-0"
                    >
                      <FileMusic size={14} className="shrink-0" />
                      <span className={`truncate text-sm ${selected === f ? 'text-white' : 'text-gray-800'}`}>
                        {f}
                      </span>
                    </button>
                    <button
                      onClick={() => handleDelete(f)}
                      disabled={deleting === f}
                      className={`p-1.5 rounded transition shrink-0 ${
                        deleting === f
                          ? 'text-gray-500 cursor-not-allowed'
                          : 'text-red-400 hover:bg-red-900/30 hover:text-red-300'
                      }`}
                      title="Delete file"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Player */}
            <div className="md:col-span-2">
              {selected && (
                <MusicPlayer
                  src={`/generated_music/${selected}`}
                  filename={selected}
                />
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
