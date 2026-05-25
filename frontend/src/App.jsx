import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Home from './pages/Home'
import UploadDataset from './pages/UploadDataset'
import TrainingDashboard from './pages/TrainingDashboard'
import MusicGenerator from './pages/MusicGenerator'
import Results from './pages/Results'

// Main App component - sets up routing and global UI elements
// Configures all application routes and displays navigation/footer on all pages
export default function App() {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: '#1f2937', color: '#f9fafb', border: '1px solid #374151' }
        }}
      />
      <Navbar />
      <main className="pt-16 min-h-screen">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/upload" element={<UploadDataset />} />
          <Route path="/train" element={<TrainingDashboard />} />
          <Route path="/generate" element={<MusicGenerator />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </main>
      <Footer />
    </BrowserRouter>
  )
}
