import { useEffect, useState } from 'react'
import { TextField, Button, Box, Snackbar } from '@mui/material'
import UserTable from './UserTable.jsx'
import AuditLogTable from './AuditLogTable.jsx'
import WorkspaceTable from './WorkspaceTable.jsx'
import { getAdminData, setApiKey, inviteUser, resetPassword, createWorkspace, deleteWorkspace } from '../api.js'

export default function AdminDashboard() {
  const [data, setData] = useState({ users: [], logs: [], has_key: false, model: '', workspaces: [] })
  const [key, setKey] = useState('')
  const [model, setModel] = useState('')
  const [saved, setSaved] = useState(false)
  const [inviteEmail, setInviteEmail] = useState('')
  const [workspaceName, setWorkspaceName] = useState('')
  const [filter, setFilter] = useState('')

  useEffect(() => {
    getAdminData().then(d => {
      setData(d)
      setKey(d.has_key ? '********' : '')
      setModel(d.model)
    })
  }, [])

  const handleSave = async e => {
    e.preventDefault()
    await setApiKey(key, model)
    setSaved(true)
  }

  const handleInvite = async e => {
    e.preventDefault()
    const res = await inviteUser(inviteEmail)
    alert(`Password: ${res.password}`)
    setInviteEmail('')
    const updated = await getAdminData()
    setData(updated)
  }

  const handleReset = async id => {
    const res = await resetPassword(id)
    alert(`New password: ${res.password}`)
  }

  const handleCreateWs = async e => {
    e.preventDefault()
    const ws = await createWorkspace(workspaceName)
    setData(d => ({ ...d, workspaces: [...d.workspaces, ws] }))
    setWorkspaceName('')
  }

  const handleDeleteWs = async id => {
    await deleteWorkspace(id)
    setData(d => ({ ...d, workspaces: d.workspaces.filter(w => w.id !== id) }))
  }

  const filteredLogs = data.logs.filter(l =>
    l.action.toLowerCase().includes(filter.toLowerCase()) || String(l.user_id).includes(filter)
  )

  return (
    <Box sx={{maxWidth:600, margin:'auto', padding:2}}>
      <h2>Admin Dashboard</h2>
      <form onSubmit={handleSave} style={{marginBottom:'1rem'}}>
        <TextField label="API Key" value={key} onChange={e=>setKey(e.target.value)} fullWidth margin="normal" />
        <TextField label="Model" value={model} onChange={e=>setModel(e.target.value)} fullWidth margin="normal" />
        <Button type="submit" variant="contained">Save</Button>
      </form>
      <form onSubmit={handleInvite} style={{marginBottom:'1rem'}}>
        <TextField label="Invite Email" value={inviteEmail} onChange={e=>setInviteEmail(e.target.value)} fullWidth margin="normal" />
        <Button type="submit" variant="contained">Invite</Button>
      </form>
      <form onSubmit={handleCreateWs} style={{marginBottom:'1rem'}}>
        <TextField label="New Workspace" value={workspaceName} onChange={e=>setWorkspaceName(e.target.value)} fullWidth margin="normal" />
        <Button type="submit" variant="contained">Create</Button>
      </form>
      <UserTable users={data.users} onReset={handleReset} />
      <WorkspaceTable workspaces={data.workspaces} onDelete={handleDeleteWs} />
      <TextField label="Filter logs" value={filter} onChange={e=>setFilter(e.target.value)} fullWidth margin="normal" />
      <AuditLogTable logs={filteredLogs} />
      <Snackbar open={saved} autoHideDuration={2000} onClose={()=>setSaved(false)} message="Saved" />
    </Box>
  )
}
