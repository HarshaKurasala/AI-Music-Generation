import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot, ExternalLink, Trash2 } from 'lucide-react'
import GenerateMusicForm from '../components/GenerateMusicForm'
import MusicPlayer from '../components/MusicPlayer'
import { deleteGeneratedFiles, getGeneratedFiles, getTrainedModelInfo } from '../services/api'

export default function MusicGenerator() {
  const [result, setResult] = useState(null)
  const [generatedFiles, setGeneratedFiles] = useState([])
  const [selectedFiles, setSelectedFiles] = useState([])
  const [deleting, setDeleting] = useState(false)
  const [error, setError] = useState(null)
  const [trainedModelInfo, setTrainedModelInfo] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    loadGeneratedFiles()
    loadTrainedModelInfo()
  }, [])

  const loadGeneratedFiles = async () => {
    try {
      const res = await getGeneratedFiles()
      setGeneratedFiles(res.data.files || [])
      setError(null)
    } catch (err) {
      console.error('Failed to load generated files:', err)
      setError(err.message)
    }
  }

  const loadTrainedModelInfo = async () => {
    try {
      const res = await getTrainedModelInfo()
      setTrainedModelInfo(res.data)
    } catch (err) {
      console.error('Failed to load trained model info:', err)
    }
  }

  const handleGenerated = (data) => {
    setResult(data)
    loadGeneratedFiles()
    loadTrainedModelInfo()
  }

  const toggleFileSelection = (file) => {
    setSelectedFiles(prev =>
      prev.includes(file) ? prev.filter(f => f !== file) : [...prev, file]
    )
  }

  const toggleAllFiles = () => {
    setSelectedFiles(prev => prev.length === generatedFiles.length ? [] : [...generatedFiles])
  }

  const handleDeleteFiles = async () => {
    if (selectedFiles.length === 0) {
      setError('Please select files to delete')
      return
    }

    if (!confirm(`Delete ${selectedFiles.length} file(s)?`)) {
      return
    }

    setDeleting(true)
    setError(null)
    try {
      await deleteGeneratedFiles(selectedFiles)
      setSelectedFiles([])
      await loadGeneratedFiles()
    } catch (err) {
      setError(err.message)
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Music Composer</h1>
        <p className="text-gray-700 mt-2">Shape a trained LSTM melody into a key-aware, humanized MIDI composition.</p>
      </div>

      {trainedModelInfo && (
        <div className={`rounded-md p-4 border ${trainedModelInfo.trained_at ? 'border-blue-300 bg-blue-50' : 'border-gray-300 bg-gray-100'}`}>
          <div className="flex items-center gap-2 mb-2">
            <Bot size={20} className={trainedModelInfo.trained_at ? 'text-blue-700' : 'text-gray-500'} />
            <h3 className="text-lg font-semibold text-gray-900">
              {trainedModelInfo.trained_at ? 'Trained Model Ready' : 'No Trained Model'}
            </h3>
          </div>
          {trainedModelInfo.trained_at ? (
            <div className="space-y-2 text-sm">
              <div className="text-gray-800">
                <span className="text-gray-700">Trained on:</span>{' '}
                {Array.isArray(trainedModelInfo.files)
                  ? trainedModelInfo.files.join(', ')
                  : 'All dataset files'}
              </div>
              <div className="text-xs text-gray-700">
                {new Date(trainedModelInfo.trained_at).toLocaleString()}
              </div>
            </div>
          ) : (
            <p className="text-sm text-gray-700">
              Train a model on the Training Dashboard to generate music.
            </p>
          )}
        </div>
      )}

      <GenerateMusicForm onGenerated={handleGenerated} />

      {result && (
        <div className="space-y-4">
          <MusicPlayer src={result.stream_url} filename={result.filename} />
          <button onClick={() => navigate('/results')} className="btn-secondary w-full gap-2">
            View All Generated Files
            <ExternalLink size={16} />
          </button>
        </div>
      )}

      {generatedFiles.length > 0 && (
        <div className="bg-white rounded-md p-6 space-y-4 border border-gray-300">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <Trash2 size={20} className="text-gray-600" />
              Manage Generated Files
            </h2>
            <span className="text-sm text-gray-700">
              {selectedFiles.length} selected
            </span>
          </div>

          {error && (
            <div className="bg-red-100 border border-red-300 rounded p-3 text-red-800 text-sm">
              {error}
            </div>
          )}

          <div className="space-y-3 max-h-60 overflow-y-auto">
            <div className="flex items-center gap-3 pb-2 border-b border-gray-300">
              <input
                type="checkbox"
                checked={selectedFiles.length === generatedFiles.length && generatedFiles.length > 0}
                onChange={toggleAllFiles}
                className="w-4 h-4 cursor-pointer"
              />
              <button
                onClick={toggleAllFiles}
                className="text-sm text-gray-700 hover:text-gray-900"
              >
                {selectedFiles.length === generatedFiles.length ? 'Deselect All' : 'Select All'}
              </button>
              <span className="text-xs text-gray-600 ml-auto">
                {generatedFiles.length} file{generatedFiles.length !== 1 ? 's' : ''}
              </span>
            </div>

            {generatedFiles.map(file => (
              <div key={file} className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded">
                <input
                  type="checkbox"
                  checked={selectedFiles.includes(file)}
                  onChange={() => toggleFileSelection(file)}
                  className="w-4 h-4 cursor-pointer"
                />
                <span className="text-sm text-gray-800 flex-1 truncate">{file}</span>
              </div>
            ))}
          </div>

          <button
            onClick={handleDeleteFiles}
            disabled={selectedFiles.length === 0 || deleting}
            className={`w-full py-2 rounded font-medium transition ${
              selectedFiles.length === 0 || deleting
                ? 'bg-red-900 text-red-300 cursor-not-allowed opacity-50'
                : 'bg-red-600 hover:bg-red-700 text-white cursor-pointer'
            }`}
          >
            {deleting ? 'Deleting...' : `Delete Selected (${selectedFiles.length})`}
          </button>
        </div>
      )}
    </div>
  )
}
