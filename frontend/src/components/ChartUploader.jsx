import { useState } from 'react'
import { Box, Button } from '@mui/material'
import { analyzeFile } from '../api.js'

export default function ChartUploader() {
  const [file, setFile] = useState(null)
  const [chart, setChart] = useState(null)
  const [stats, setStats] = useState(null)

  async function handleAnalyze(e) {
    e.preventDefault()
    if (!file) return
    try {
      const res = await analyzeFile(file)
      setStats(res.data)
      setChart(res.chart)
    } catch (err) {
      setStats(err.toString())
    }
  }

  return (
    <Box>
      <Box component="form" onSubmit={handleAnalyze} sx={{ mb: 2 }}>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
        <Button type="submit" variant="contained" sx={{ ml: 1 }}>
          Analyze
        </Button>
      </Box>
      {chart && <img src={`data:image/png;base64,${chart}`} alt="chart" />}
      {stats && Array.isArray(stats) && (
        <pre>{JSON.stringify(stats, null, 2)}</pre>
      )}
      {typeof stats === 'string' && !Array.isArray(stats) && <div>{stats}</div>}
    </Box>
  )
}
