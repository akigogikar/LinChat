import { useState } from 'react'
import { Box, Button, Typography, Stack, LinearProgress } from '@mui/material'

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
<Stack
  component="form"
  onSubmit={handleUpload}
  spacing={1}
  direction={{ xs: 'column', sm: 'row' }}
  sx={{ mb: 2 }}
>
  <input
    type="file"
    aria-label="choose file"
    onChange={e => setFile(e.target.files[0])}
  />
  <Button
    type="submit"
    variant="contained"
    aria-label="upload file"
    disabled={progress !== null}
  >
    Upload
  </Button>
  {progress !== null && (
    <Box sx={{ width: '100%' }}>
      <LinearProgress variant="determinate" value={progress} />
    </Box>
  )}
  <Typography variant="body2">
    {status}
  </Typography>
</Stack>

  )
}
