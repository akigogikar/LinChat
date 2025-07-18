import { useState } from 'react'
import { Box, Button, Typography } from '@mui/material'
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
    <Box component="form" onSubmit={handleUpload} sx={{ mb: 2 }}>
      <input type="file" onChange={e => setFile(e.target.files[0])} />
      <Button type="submit" variant="contained" sx={{ ml: 1 }}>
        Upload
      </Button>
      <Typography variant="body2" sx={{ ml: 1 }}>
        {status}
      </Typography>
    </Box>
  )
}
