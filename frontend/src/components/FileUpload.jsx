import { useState } from 'react'
import { Box, Button, Typography, LinearProgress } from '@mui/material'
import { uploadFile } from '../api.js'

export default function FileUpload() {
  const [file, setFile] = useState(null)
  const [status, setStatus] = useState('')
  const [progress, setProgress] = useState(null)

  async function handleUpload(e) {
    e.preventDefault()
    if (!file) return
    try {
      const res = await uploadFile(file, false, p => setProgress(p))
      setStatus(`Uploaded ${res.document_id}`)
    } catch (err) {
      setStatus(`Upload failed: ${err.message}`)
    } finally {
      setProgress(null)
    }
  }

  return (
    <Box component="form" onSubmit={handleUpload} sx={{ mb: 2 }}>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <Button type="submit" variant="contained" sx={{ ml: 1 }} disabled={progress !== null}>
        Upload
      </Button>
      {progress !== null && (
        <Box sx={{ width: '100%', ml: 1, mr: 1 }}>
          <LinearProgress variant="determinate" value={progress} />
        </Box>
      )}
      <Typography variant="body2" sx={{ ml: 1 }}>
        {status}
      </Typography>
    </Box>
  )
}
