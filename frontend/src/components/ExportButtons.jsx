import { useState } from 'react'
import { Box, Button, Link } from '@mui/material'
import { exportPdf } from '../api.js'

export default function ExportButtons({ content }) {
  const [url, setUrl] = useState(null)

  async function handlePdf() {
    try {
      const link = await exportPdf(content)
      setUrl(link)
    } catch (err) {
      alert(err)
    }
  }

  return (
    <Box sx={{ mt: 2 }}>
      <Button variant="contained" onClick={handlePdf}>
        Export PDF
      </Button>
      {url && (
        <Link href={url} download="output.pdf" sx={{ ml: 1 }}>
          Download
        </Link>
      )}
    </Box>
  )
}
