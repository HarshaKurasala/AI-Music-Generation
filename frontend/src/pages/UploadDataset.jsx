import { useEffect, useState } from 'react'
import { FileMusic, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import FileUploader from '../components/FileUploader'
import ConfirmDialog from '../components/ConfirmDialog'
import { deleteDatasetFiles, getDatasetInfo } from '../services/api'

export default function UploadDataset() {
  const [info, setInfo] = useState({ files: [], count: 0 })
  const [deletingFile, setDeletingFile] = useState(null)
  const [pendingDelete, setPendingDelete] = useState(null)

  const refresh = () => getDatasetInfo().then(r => setInfo(r.data))

  useEffect(() => { refresh() }, [])

  const handleDelete = async (file) => {
    setPendingDelete(file)
  }

  const confirmDelete = async () => {
    if (!pendingDelete) return

    setDeletingFile(pendingDelete)
    try {
      const { data } = await deleteDatasetFiles([pendingDelete])
      toast.success(data.message)
      setPendingDelete(null)
      await refresh()
    } catch (e) {
      toast.error(e.message)
    } finally {
      setDeletingFile(null)
    }
  }

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
              <li key={i} className="flex items-center gap-3 rounded-md border border-gray-200 px-3 py-2 text-sm text-gray-700">
                <FileMusic size={14} className="text-blue-600 shrink-0" />
                <span className="min-w-0 flex-1 truncate">{f}</span>
                <button
                  type="button"
                  onClick={() => handleDelete(f)}
                  disabled={deletingFile === f}
                  className="inline-flex h-8 w-8 items-center justify-center rounded text-gray-500 transition hover:bg-red-50 hover:text-red-600 disabled:cursor-not-allowed disabled:opacity-50"
                  title={`Delete ${f}`}
                  aria-label={`Delete ${f}`}
                >
                  <Trash2 size={15} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Delete dataset file?"
        message={pendingDelete ? `"${pendingDelete}" will be removed from the training dataset.` : ''}
        loading={Boolean(deletingFile)}
        onCancel={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
      />
    </div>
  )
}
