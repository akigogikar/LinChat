import { useState } from 'react'
import {
  Box,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Stack,
} from '@mui/material'
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
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              {table.columns.map(col => (
                <TableCell key={col}>{col}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {table.rows.map((row, idx) => (
              <TableRow key={idx}>
                {row.map((cell, i) => (
                  <TableCell key={i}>{cell}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    )
  }

  return (
    <Box>
      <Stack
        component="form"
        onSubmit={handleGen}
        spacing={1}
        direction={{ xs: 'column', sm: 'row' }}
        sx={{ mb: 2 }}
      >
        <TextField
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Table prompt"
          size="small"
        />
        <Button type="submit" variant="contained" aria-label="generate table">
          Generate Table
        </Button>
      </Stack>
      {renderTable()}
    </Box>
  )
}
