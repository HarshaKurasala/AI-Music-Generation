import { useCallback, useState } from 'react'
import { UploadCloud, X, FileMusic } from 'lucide-react'
import toast from 'react-hot-toast'
import { uploadMidi } from '../services/api'

// FileUploader component - handles MIDI file selection and upload
// Provides drag-and-drop and click-to-upload interface
export default function FileUploader({ onUploadSuccess }) {
  const [files, setFiles] = useState([])
  const [dragging, setDragging] = useState(false)
  const [loading, setLoading] = useState(false)

  // Add files to selected files list
  // Validates file types and prevents duplicates
  const addFiles = (incoming) => {
    const midi = Array.from(incoming).filter(f => f.name.match(/\.midi?$/i))
    if (midi.length === 0) return toast.error('Only .mid / .midi files accepted')
    setFiles(prev => {
      const names = new Set(prev.map(f => f.name))
      return [...prev, ...midi.filter(f => !names.has(f.name))]
    })
  }

  // Handle drag over event
  // Sets dragging state when files are dragged over drop zone
  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    addFiles(e.dataTransfer.files)
  }, [])

  // Handle upload button click
  // Sends selected files to backend
  const handleUpload = async () => {
    if (!files.length) return toast.error('Add at least one MIDI file')
    setLoading(true)
    try {
      const { data } = await uploadMidi(files)
      toast.success(data.message)
      setFiles([])
      onUploadSuccess?.(data)
    } catch (e) {
      toast.error(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-colors ${
          dragging ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-blue-500'
        }`}
        onClick={() => document.getElementById('midi-input').click()}
      >
        <UploadCloud size={40} className="mx-auto mb-3 text-blue-600" />
        <p className="text-gray-700 font-medium">Drag & drop MIDI files here</p>
        <p className="text-gray-600 text-sm mt-1">or click to browse</p>
        <input
          id="midi-input"
          type="file"
          accept=".mid,.midi"
          multiple
          className="hidden"
          onChange={e => addFiles(e.target.files)}
        />
      </div>

      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((f, i) => (
            <li key={i} className="flex items-center justify-between glass rounded-lg px-4 py-2.5">
              <div className="flex items-center gap-2 text-sm text-gray-700">
                <FileMusic size={16} className="text-blue-600" />
                {f.name}
                <span className="text-gray-600">({(f.size / 1024).toFixed(1)} KB)</span>
              </div>
              <button onClick={() => setFiles(prev => prev.filter((_, j) => j !== i))}>
                <X size={16} className="text-gray-600 hover:text-red-500" />
              </button>
            </li>
          ))}
        </ul>
      )}

      <button onClick={handleUpload} disabled={loading || !files.length} className="btn-primary w-full">
        {loading ? 'Uploading...' : `Upload ${files.length || ''} File${files.length !== 1 ? 's' : ''}`}
      </button>
    </div>
  )
}
