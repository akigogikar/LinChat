import { useState } from 'react'
import { Box, LinearProgress, Snackbar } from '@mui/material'
import { DropzoneArea } from 'react-mui-dropzone'
import { uploadFile } from '../api.js'

export default function UploadDropzone({ onUploaded }) {
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  async function handleChange(files) {
    if (!files || files.length === 0) return
    for (const file of files) {
      setUploading(true)
      try {
        await uploadFile(file)
        setMessage(`Uploaded ${file.name}`)
        if (onUploaded) onUploaded()
      } catch (err) {
        setMessage(err.toString())
      } finally {
        setUploading(false)
      }
    }
  }

  return (
    <Box sx={{ mb: 2 }}>
      <DropzoneArea onChange={handleChange} showPreviewsInDropzone filesLimit={5} />
      {uploading && <LinearProgress sx={{ mt: 1 }} />}
      <Snackbar open={!!message} autoHideDuration={2000} onClose={() => setMessage('')} message={message} />
    </Box>
  )
}
