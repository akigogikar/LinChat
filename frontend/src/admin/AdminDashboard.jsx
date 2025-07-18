import { useEffect, useState } from 'react'
import { TextField, Button, Box } from '@mui/material'
import UserTable from './UserTable.jsx'
import AuditLogTable from './AuditLogTable.jsx'
import { getAdminData, setApiKey } from '../api.js'

export default function AdminDashboard() {
  const [data, setData] = useState({ users: [], logs: [], key: '', model: '' })
  const [key, setKey] = useState('')
  const [model, setModel] = useState('')

  useEffect(() => {
    getAdminData().then(d => {
      setData(d)
      setKey(d.key)
      setModel(d.model)
    })
  }, [])

  const handleSave = async e => {
    e.preventDefault()
    await setApiKey(key, model)
  }

  return (
    <Box sx={{maxWidth:600, margin:'auto', padding:2}}>
      <h2>Admin Dashboard</h2>
      <form onSubmit={handleSave} style={{marginBottom:'1rem'}}>
        <TextField label="API Key" value={key} onChange={e=>setKey(e.target.value)} fullWidth margin="normal" />
        <TextField label="Model" value={model} onChange={e=>setModel(e.target.value)} fullWidth margin="normal" />
        <Button type="submit" variant="contained">Save</Button>
      </form>
      <UserTable users={data.users} />
      <AuditLogTable logs={data.logs} />
    </Box>
  )
}
