import { useState } from 'react'
import { Box, Button, Typography, Stack } from '@mui/material'
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
      <Button type="submit" variant="contained" aria-label="upload file">
        Upload
      </Button>
      <Typography variant="body2">{status}</Typography>
    </Stack>
  )
}
