import { useState } from 'react'
import { Box, Button, CircularProgress } from '@mui/material'
import { analyzeFile } from '../api.js'

export default function ChartUploader() {
  const [file, setFile] = useState(null)
  const [chart, setChart] = useState(null)
  const [stats, setStats] = useState(null)
  const [progress, setProgress] = useState(null)

  async function handleAnalyze(e) {
    e.preventDefault()
    if (!file) return
    try {
      const res = await analyzeFile(file, p => setProgress(p))
      setStats(res.data)
      setChart(res.chart)
    } catch (err) {
      setStats(`Analysis failed: ${err.message}`)
    } finally {
      setProgress(null)
    }
  }

  return (
    <Box>
      <Box component="form" onSubmit={handleAnalyze} sx={{ mb: 2 }}>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
        <Button type="submit" variant="contained" sx={{ ml: 1 }} disabled={progress !== null}>
          Analyze
        </Button>
        {progress !== null && (
          <Box sx={{ ml: 1 }}>
            <CircularProgress variant="determinate" value={progress} />
          </Box>
        )}
      </Box>
      {chart && <img src={`data:image/png;base64,${chart}`} alt="chart" />}
      {stats && Array.isArray(stats) && (
        <pre>{JSON.stringify(stats, null, 2)}</pre>
      )}
      {typeof stats === 'string' && !Array.isArray(stats) && <div>{stats}</div>}
    </Box>
  )
}
