import { useState } from 'react'
import { uploadFile } from '../api.js'

export default function FileUpload() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('')

  async function handleUpload(e) {
    e.preventDefault()
    if (!file) return
    try {
      const res = await uploadFile(file)
      setStatus(`Uploaded ${res.document_id}`)
    } catch (err) {
      setStatus(err.toString())
    }
  }

  return (
    <form onSubmit={handleUpload} style={{ marginBottom: '1rem' }}>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <button type="submit">Upload</button>
      <span>{status}</span>
    </form>
  )
}
