import { useState } from 'react'
import { Box, Button, Stack } from '@mui/material'
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
        <Button type="submit" variant="contained" aria-label="analyze file">
          Analyze
        </Button>
      </Stack>
      {chart && <img src={`data:image/png;base64,${chart}`} alt="chart" />}
      {stats && Array.isArray(stats) && (
        <pre>{JSON.stringify(stats, null, 2)}</pre>
      )}
      {typeof stats === 'string' && !Array.isArray(stats) && <div>{stats}</div>}
    </Box>
  )
}
