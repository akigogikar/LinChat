import { exportPdf } from '../api.js'
import { useState } from 'react'

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
    <div style={{ marginTop: '1rem' }}>
      <button onClick={handlePdf}>Export PDF</button>
      {url && (
        <a href={url} download="output.pdf" style={{ marginLeft: '0.5rem' }}>
          Download
        </a>
      )}
    </div>
  )
}
