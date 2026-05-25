import { Music2 } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="border-t border-gray-300 mt-20 py-8">
      <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row items-center justify-between gap-4 text-gray-700 text-sm">
        <div className="flex items-center gap-2">
          <Music2 size={16} className="text-blue-600" />
          <span>MusicAI — LSTM-powered music generation</span>
        </div>
        <span>Built with FastAPI · TensorFlow · React</span>
      </div>
    </footer>
  )
}
