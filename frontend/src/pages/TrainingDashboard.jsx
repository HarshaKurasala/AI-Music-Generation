import { useEffect, useRef, useState } from 'react'
import { Cpu, AlertCircle, RotateCcw } from 'lucide-react'
import toast from 'react-hot-toast'
import TrainingProgress from '../components/TrainingProgress'
import { trainModel, getTrainingStatus, getDatasetInfo, resetTraining } from '../services/api'

const DEFAULT_CONFIG = { epochs: 50, batch_size: 64, seq_length: 50 }

export default function TrainingDashboard() {
  const [config, setConfig] = useState(DEFAULT_CONFIG)
  const [status, setStatus] = useState({ state: 'idle', epoch: 0, total_epochs: 0, loss: [], accuracy: [], message: '' })
  const [datasetCount, setDatasetCount] = useState(null)
  const [datasetLoading, setDatasetLoading] = useState(true)
  const [midiFiles, setMidiFiles] = useState([])
  const [selectedFiles, setSelectedFiles] = useState([])
  const pollRef = useRef(null)
  const terminalStateRef = useRef(null)

  const set = (k, v) => setConfig(prev => ({ ...prev, [k]: v }))
  const isActiveTrainingState = (state) => state === 'training' || state === 'preparing'

  const toggleFileSelection = (file) => {
    setSelectedFiles(prev =>
      prev.includes(file)
        ? prev.filter(f => f !== file)
        : [...prev, file]
    )
  }

  const toggleAllFiles = () => {
    if (selectedFiles.length === midiFiles.length) {
      setSelectedFiles([])
    } else {
      setSelectedFiles(midiFiles)
    }
  }

  useEffect(() => {
    const checkDataset = async () => {
      try {
        const { data } = await getDatasetInfo()
        setDatasetCount(data.count)
        setMidiFiles(data.files || [])
        setSelectedFiles(prev => prev.filter(file => (data.files || []).includes(file)))
      } catch (_) {}
      finally {
        setDatasetLoading(false)
      }
    }
    checkDataset()
    const interval = setInterval(checkDataset, 5000)
    return () => clearInterval(interval)
  }, [])

  const stopPolling = () => {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }

  const applyTrainingStatus = (data, notify = false) => {
    setStatus(data)

    if (data.state === 'completed' || data.state === 'error') {
      stopPolling()

      if (notify && terminalStateRef.current !== data.state) {
        terminalStateRef.current = data.state
        if (data.state === 'completed') toast.success('Training complete!')
        else toast.error('Training failed: ' + data.message)
      }
    } else if (isActiveTrainingState(data.state)) {
      terminalStateRef.current = null
    }
  }

  const fetchTrainingStatus = async (notify = false) => {
    try {
      const { data } = await getTrainingStatus()
      applyTrainingStatus(data, notify)
      return data
    } catch (_) {
      return null
    }
  }

  const startPolling = () => {
    stopPolling()
    pollRef.current = setInterval(async () => {
      await fetchTrainingStatus(true)
    }, 2000)
  }

  useEffect(() => {
    const syncTraining = async () => {
      const data = await fetchTrainingStatus(false)
      if (data && isActiveTrainingState(data.state)) {
        startPolling()
      }
    }

    syncTraining()
    return stopPolling
  }, [])

  const handleTrain = async () => {
    if (datasetCount === 0) {
      toast.error('No MIDI files uploaded. Please go to Upload page first.')
      return
    }
    if (selectedFiles.length === 0) {
      toast.error('Please select at least one MIDI file to train.')
      return
    }
    try {
      await trainModel({ ...config, files: selectedFiles })
      setStatus({
        state: 'preparing',
        epoch: 0,
        total_epochs: config.epochs,
        loss: [],
        accuracy: [],
        message: 'Training started. Preparing dataset...'
      })
      toast.success('Training started!')
      await fetchTrainingStatus(false)
      startPolling()
    } catch (e) {
      toast.error(e.message)
    }
  }

  const handleReset = async () => {
    try {
      await resetTraining()
      stopPolling()
      setStatus({ state: 'idle', epoch: 0, total_epochs: 0, loss: [], accuracy: [], message: 'Training reset' })
      toast.success('Training state reset successfully')
    } catch (e) {
      toast.error('Failed to reset: ' + e.message)
    }
  }

  const resetConfig = () => {
    setConfig(DEFAULT_CONFIG)
    toast.success('Model configuration reset')
  }

  const isRunning = status.state === 'training' || status.state === 'preparing'

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Training Dashboard</h1>
        <p className="text-gray-600 mt-2">Configure and train the LSTM model on your MIDI dataset.</p>
      </div>

      {datasetLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
          <p className="text-blue-800 text-sm">Checking uploaded MIDI files...</p>
        </div>
      )}

      {!datasetLoading && datasetCount === 0 && (
        <div className="bg-orange-100 border border-orange-400 rounded-xl p-4 flex items-start gap-3">
          <AlertCircle size={20} className="text-orange-600 shrink-0 mt-0.5" />
          <div>
            <p className="text-orange-800 font-medium">No MIDI files uploaded</p>
            <p className="text-orange-700 text-sm mt-1">Upload at least one MIDI file on the <a href="/upload" className="underline hover:no-underline">Upload page</a> to start training.</p>
          </div>
        </div>
      )}

      {!datasetLoading && datasetCount > 0 && (
        <div className="bg-green-100 border border-green-400 rounded-xl p-4">
          <p className="text-green-800 text-sm"><span className="font-semibold">{datasetCount}</span> MIDI file{datasetCount !== 1 ? 's' : ''} ready for training</p>
        </div>
      )}

      {/* MIDI File Selection */}
      {!datasetLoading && midiFiles.length > 0 && (
        <div className="card space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-800">Select MIDI Files to Train</h3>
            <button
              type="button"
              onClick={toggleAllFiles}
              className="text-xs px-2 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 rounded transition-colors"
            >
              {selectedFiles.length === midiFiles.length ? 'Deselect All' : 'Select All'}
            </button>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {midiFiles.map((file) => (
              <label key={file} className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                <input
                  type="checkbox"
                  checked={selectedFiles.includes(file)}
                  onChange={() => toggleFileSelection(file)}
                  className="w-4 h-4 accent-blue-500"
                />
                <span className="text-sm text-gray-800 truncate">{file}</span>
              </label>
            ))}
          </div>
          <p className="text-xs text-gray-600">{selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''} selected</p>
        </div>
      )}

      {/* Config */}
      <div className="card space-y-5">
        <div className="flex items-center justify-between gap-3">
          <h2 className="font-semibold text-gray-800 flex items-center gap-2"><Cpu size={16} className="text-blue-600" /> Model Configuration</h2>
          <button
            type="button"
            onClick={resetConfig}
            disabled={isRunning}
            className="inline-flex items-center gap-1.5 rounded-md border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <RotateCcw size={14} />
            Reset
          </button>
        </div>

        {[
          { key: 'epochs', label: 'Epochs', min: 1, max: 500 },
          { key: 'batch_size', label: 'Batch Size', min: 8, max: 256 },
          { key: 'seq_length', label: 'Sequence Length', min: 10, max: 200 },
        ].map(({ key, label, min, max }) => (
          <div key={key} className="space-y-1">
            <label className="text-sm text-gray-700">{label}: <span className="text-gray-900">{config[key]}</span></label>
            <input
              type="range" min={min} max={max}
              value={config[key]}
              onChange={e => set(key, Number(e.target.value))}
              className="w-full accent-blue-500"
            />
          </div>
        ))}

        <button onClick={handleTrain} disabled={isRunning || datasetLoading || datasetCount === 0} className="btn-primary w-full">
          {isRunning ? 'Training in progress...' : 'Start Training'}
        </button>

        {status.state === 'error' && (
          <button onClick={handleReset} className="btn-secondary w-full flex items-center justify-center gap-2">
            <RotateCcw size={16} /> Reset Training State
          </button>
        )}
      </div>

      <TrainingProgress status={status} />
    </div>
  )
}
