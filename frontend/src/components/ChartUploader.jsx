import { useState } from 'react'
import { Box, Button, Stack, CircularProgress } from '@mui/material'
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
      <Stack
        component="form"
        onSubmit={handleAnalyze}
        spacing={1}
        direction={{ xs: 'column', sm: 'row' }}
        sx={{ mb: 2 }}
      >
        <input
          type="file"
          aria-label="choose file for analysis"
          onChange={e => setFile(e.target.files[0])}
        />
        <Button
          type="submit"
          variant="contained"
          aria-label="analyze file"
          disabled={progress !== null}
        >
          Analyze
        </Button>
        {progress !== null && (
          <Box sx={{ ml: 1 }}>
            <CircularProgress variant="determinate" value={progress} />
          </Box>
        )}
      </Stack>

      {chart && <img src={`data:image/png;base64,${chart}`} alt="chart" />}
      {stats && Array.isArray(stats) && (
        <pre>{JSON.stringify(stats, null, 2)}</pre>
      )}
      {typeof stats === 'string' && !Array.isArray(stats) && <div>{stats}</div>}
    </Box>
  )
}
