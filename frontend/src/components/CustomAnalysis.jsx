import { useState } from 'react'
import { Box, Button, CircularProgress, Stack, TextField } from '@mui/material'
import { customAnalysis } from '../api.js'

export default function CustomAnalysis() {
  const [file, setFile] = useState(null)
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState(null)
  const [chart, setChart] = useState(null)
  const [progress, setProgress] = useState(null)

  async function handleRun(e) {
    e.preventDefault()
    if (!file || !prompt) return
    try {
      const res = await customAnalysis(prompt, file, p => setProgress(p))
      setResult(res.data)
      setChart(res.chart)
    } catch (err) {
      setResult(`Analysis failed: ${err.message}`)
    } finally {
      setProgress(null)
    }
  }

  return (
    <Box>
      <Stack
        component="form"
        onSubmit={handleRun}
        spacing={1}
        direction={{ xs: 'column', sm: 'row' }}
        sx={{ mb: 2 }}
      >
        <input
          type="file"
          aria-label="choose file for analysis"
          onChange={e => setFile(e.target.files[0])}
        />
        <TextField
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Analysis prompt"
          size="small"
        />
        <Button type="submit" variant="contained" disabled={progress !== null} aria-label="run custom analysis">
          Run
        </Button>
        {progress !== null && (
          <Box sx={{ ml: 1 }}>
            <CircularProgress variant="determinate" value={progress} />
          </Box>
        )}
      </Stack>

      {chart && <img src={`data:image/png;base64,${chart}`} alt="chart" />}
      {result && Array.isArray(result) && <pre>{JSON.stringify(result, null, 2)}</pre>}
      {result && typeof result === 'string' && !Array.isArray(result) && <div>{result}</div>}
    </Box>
  )
}
