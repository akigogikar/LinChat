import { useState } from 'react'
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
    <div>
      <form onSubmit={handleAnalyze} style={{ marginBottom: '1rem' }}>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
        <button type="submit">Analyze</button>
      </form>
      {chart && <img src={`data:image/png;base64,${chart}`} alt="chart" />}
      {stats && Array.isArray(stats) && (
        <pre>{JSON.stringify(stats, null, 2)}</pre>
      )}
      {typeof stats === 'string' && !Array.isArray(stats) && <div>{stats}</div>}
    </div>
  )
}
