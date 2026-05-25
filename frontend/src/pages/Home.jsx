import { Link } from 'react-router-dom'
import { Music2, Upload, Cpu, Wand2, Download } from 'lucide-react'

const steps = [
  { icon: Upload, title: 'Upload MIDI', desc: 'Upload your MIDI dataset files to train the AI model.', to: '/upload', color: 'text-blue-600' },
  { icon: Cpu, title: 'Train Model', desc: 'Train the LSTM neural network on your music patterns.', to: '/train', color: 'text-green-600' },
  { icon: Wand2, title: 'Generate Music', desc: 'Generate new music sequences with custom parameters.', to: '/generate', color: 'text-purple-600' },
  { icon: Download, title: 'Download', desc: 'Download and play your AI-generated MIDI compositions.', to: '/results', color: 'text-red-600' },
]

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-20 text-center">
      {/* Hero */}
      <div className="mb-16 space-y-6 max-w-3xl">
        <div className="inline-flex items-center gap-2 bg-blue-100 border border-blue-300 rounded-full px-4 py-1.5 text-blue-700 text-sm">
          <Music2 size={14} />
          AI-Powered Music Generation
        </div>
        <h1 className="text-5xl md:text-6xl font-bold text-blue-900 leading-tight">
          Compose Music with AI
        </h1>
        <p className="text-gray-700 text-lg max-w-xl mx-auto">
          Upload MIDI files, train an LSTM neural network on music patterns, and generate original compositions in seconds.
        </p>
        <div className="flex flex-wrap gap-3 justify-center">
          <Link to="/upload" className="btn-primary">Get Started</Link>
          <Link to="/generate" className="btn-secondary">Generate Music</Link>
        </div>
      </div>

      {/* Steps */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 max-w-5xl w-full">
        {steps.map(({ icon: Icon, title, desc, to, color }, i) => (
          <Link key={i} to={to} className="card hover:border-blue-300 transition-all group text-left space-y-3">
            <div className={`w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center ${color}`}>
              <Icon size={20} />
            </div>
            <div>
              <p className="font-semibold text-gray-800 group-hover:text-gray-900 transition-colors">{title}</p>
              <p className="text-sm text-gray-600 mt-1">{desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}
