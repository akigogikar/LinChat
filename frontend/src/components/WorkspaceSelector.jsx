import { useEffect, useState } from 'react'
import { FormControl, InputLabel, Select, MenuItem } from '@mui/material'
import { getWorkspaces } from '../api.js'

export default function WorkspaceSelector({ onChange }) {
  const [workspaces, setWorkspaces] = useState([])
  const [value, setValue] = useState('')

  useEffect(() => {
    getWorkspaces().then(res => setWorkspaces(res.workspaces))
  }, [])

  const handleChange = e => {
  const id = e.target.value
  setValue(id)
  const ws = workspaces.find(w => w.id === id)
  if (onChange) onChange(ws)

  return (
    <FormControl fullWidth size="small" sx={{ mb: 2 }}>

      <InputLabel id="ws-label">Workspace</InputLabel>
      <Select labelId="ws-label" value={value} label="Workspace" onChange={handleChange}>
        {workspaces.map(ws => (
          <MenuItem key={ws.id} value={ws.id}>{ws.name}</MenuItem>
        ))}
      </Select>
    </FormControl>
  )
}
