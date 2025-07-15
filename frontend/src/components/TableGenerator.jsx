import { useState } from 'react'
import { generateTable } from '../api.js'

export default function TableGenerator() {
  const [prompt, setPrompt] = useState('')
  const [table, setTable] = useState(null)

  async function handleGen(e) {
    e.preventDefault()
    try {
      const res = await generateTable(prompt)
      setTable(res)
    } catch (err) {
      setTable({ error: err.toString() })
    }
  }

  function renderTable() {
    if (!table) return null
    if (table.error) return <div>{table.error}</div>
    return (
      <table border="1">
        <thead>
          <tr>
            {table.columns.map(col => <th key={col}>{col}</th>)}
          </tr>
        </thead>
        <tbody>
          {table.rows.map((row, idx) => (
            <tr key={idx}>{row.map((cell, i) => <td key={i}>{cell}</td>)}</tr>
          ))}
        </tbody>
      </table>
    )
  }

  return (
    <div>
      <form onSubmit={handleGen} style={{ marginBottom: '1rem' }}>
        <input value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Table prompt" />
        <button type="submit">Generate Table</button>
      </form>
      {renderTable()}
    </div>
  )
}
