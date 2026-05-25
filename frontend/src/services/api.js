import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000,
})

api.interceptors.response.use(
  res => res,
  err => {
    const msg = err.response?.data?.detail || err.message || 'Request failed'
    return Promise.reject(new Error(typeof msg === 'string' ? msg : JSON.stringify(msg)))
  }
)

// Upload MIDI files to backend
// Sends files as multipart form data
export const uploadMidi = (files) => {
  const form = new FormData()
  files.forEach(f => form.append('files', f))
  return api.post('/upload-midi', form)
}

// Get information about uploaded MIDI files
// Returns list of files and count
export const getDatasetInfo = () => api.get('/dataset-info')

// Start model training with specified parameters
// Schedules training as background task
export const trainModel = (config) => api.post('/train-model', config)

// Get current training status and progress
// Returns epoch, loss, accuracy, and status message
export const getTrainingStatus = () => api.get('/training-status')

// Reset training state for recovery
// Resets training flag and status
export const resetTraining = () => api.post('/reset-training')

// Generate new music with specified parameters
// Creates new MIDI composition
export const generateMusic = (params) => api.post('/generate-music', params)

// Get list of generated music files
// Returns all generated MIDI files
export const getGeneratedFiles = () => api.get('/generated-files')

// Delete specified generated music files
// Removes files from server
export const deleteGeneratedFiles = (files) => api.post('/delete-generated-files', { files })

// Get information about trained model
// Returns model metadata
export const getTrainedModelInfo = () => api.get('/trained-model-info')

// Check if API is running
// Health check endpoint
export const healthCheck = () => api.get('/health')

export default api
