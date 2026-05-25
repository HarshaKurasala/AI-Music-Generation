import { useEffect, useRef, useState } from 'react'
import { Play, Pause, Download } from 'lucide-react'

export default function MusicPlayer({ src, filename }) {
  const audioRef = useRef(null)
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)

  useEffect(() => {
    setPlaying(false)
    setProgress(0)
  }, [src])

  const toggle = () => {
    if (!audioRef.current) return
    playing ? audioRef.current.pause() : audioRef.current.play()
    setPlaying(!playing)
  }

  const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`

  return (
    <div className="card space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-gray-400 truncate max-w-xs">{filename}</span>
        <a href={src} download={filename} className="btn-secondary flex items-center gap-2 text-sm py-2 px-3">
          <Download size={14} /> Download
        </a>
      </div>

      <audio
        ref={audioRef}
        src={src}
        onTimeUpdate={() => setProgress(audioRef.current?.currentTime || 0)}
        onLoadedMetadata={() => setDuration(audioRef.current?.duration || 0)}
        onEnded={() => setPlaying(false)}
      />

      <div className="flex items-center gap-4">
        <button onClick={toggle} className="w-10 h-10 rounded-full bg-blue-600 hover:bg-blue-500 flex items-center justify-center transition-colors">
          {playing ? <Pause size={18} /> : <Play size={18} />}
        </button>

        <div className="flex-1 space-y-1">
          <input
            type="range"
            min={0}
            max={duration || 1}
            value={progress}
            onChange={e => {
              const t = Number(e.target.value)
              if (audioRef.current) audioRef.current.currentTime = t
              setProgress(t)
            }}
            className="w-full accent-blue-500 cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-700">
            <span>{fmt(progress)}</span>
            <span>{fmt(duration)}</span>
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-600 text-center">
        Note: Browser MIDI playback requires a soundfont. Use the Download button to play in a MIDI player.
      </p>
    </div>
  )
}
