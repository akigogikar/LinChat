import { useState } from 'react'
import { Box, LinearProgress, Snackbar } from '@mui/material'
import { DropzoneArea } from 'react-mui-dropzone'
import { uploadFile } from '../api.js'

export default function UploadDropzone({ onUploaded }) {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(null)
  const [message, setMessage] = useState('')

  async function handleChange(files) {
    if (!files || files.length === 0) return
    for (const file of files) {
      setUploading(true)
      setProgress(0)
      try {
        await uploadFile(file, false, p => setProgress(p))
        setMessage(`Uploaded ${file.name}`)
        if (onUploaded) onUploaded()
      } catch (err) {
        setMessage(err.toString())
      } finally {
        setUploading(false)
        setProgress(null)
      }
    }
  }

  return (
    <Box sx={{ mb: 2 }}>
      <DropzoneArea onChange={handleChange} showPreviewsInDropzone filesLimit={5} />
      {uploading && (
        <LinearProgress sx={{ mt: 1 }} variant="determinate" value={progress || 0} />
      )}
      <Snackbar open={!!message} autoHideDuration={2000} onClose={() => setMessage('')} message={message} />
    </Box>
  )
}
