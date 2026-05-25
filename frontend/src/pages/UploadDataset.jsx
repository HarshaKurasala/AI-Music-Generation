import { useEffect, useState } from 'react'
import { FileMusic, Trash2 } from 'lucide-react'
import FileUploader from '../components/FileUploader'
import { getDatasetInfo } from '../services/api'

export default function UploadDataset() {
  const [info, setInfo] = useState({ files: [], count: 0 })

  const refresh = () => getDatasetInfo().then(r => setInfo(r.data))

  useEffect(() => { refresh() }, [])

  return (
    <div className="max-w-2xl mx-auto px-4 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Upload MIDI Dataset</h1>
        <p className="text-gray-600 mt-2">Upload .mid or .midi files to build your training dataset.</p>
      </div>

      <FileUploader onUploadSuccess={refresh} />

      {/* Dataset summary */}
      <div className="card space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold text-gray-800">Dataset Files</h2>
          <span className="text-sm text-blue-600">{info.count} file{info.count !== 1 ? 's' : ''}</span>
        </div>
        {info.files.length === 0 ? (
          <p className="text-gray-600 text-sm">No files uploaded yet.</p>
        ) : (
          <ul className="space-y-2 max-h-64 overflow-y-auto">
            {info.files.map((f, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                <FileMusic size={14} className="text-blue-600 shrink-0" />
                {f}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
