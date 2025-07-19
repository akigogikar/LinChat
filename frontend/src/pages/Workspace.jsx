import { useEffect, useState } from 'react'
import {
  Container, Box, TextField, Button, Typography,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, List, ListItem, ListItemText
} from '@mui/material'
import WorkspaceSelector from '../components/WorkspaceSelector.jsx'
import AuditLogTable from '../admin/AuditLogTable.jsx'
import { API_BASE, getWorkspaces, getAdminData, inviteUser, assignWorkspace } from '../api.js'

export default function WorkspacePage() {
  // For simple public list
  const [workspaces, setWorkspaces] = useState([])

  // For admin/team view
  const [data, setData] = useState({ users: [], workspaces: [], logs: [] })
  const [workspace, setWorkspace] = useState(null)
  const [inviteEmail, setInviteEmail] = useState('')

  useEffect(() => {
    getWorkspaces().then(res => setWorkspaces(res.workspaces || []))
    loadAdmin()
  }, [])

  async function loadAdmin() {
    const d = await getAdminData()
    setData(d)
  }

  async function handleInvite(e) {
    e.preventDefault()
    if (!workspace) return
    const res = await inviteUser(inviteEmail, workspace)
    alert(`Password: ${res.password}`)
    setInviteEmail('')
    loadAdmin()
  }

  async function handleAssign(userId, teamId) {
    await assignWorkspace(userId, teamId)
    loadAdmin()
  }

  const members = data.users.filter(u => u.team_id === workspace)

  const handleCopy = id => {
    navigator.clipboard.writeText(`${window.location.origin}/workspace/${id}`)
  }

  return (
    <Container sx={{ mt: 2 }}>
      <Typography variant="h5" sx={{ mb: 2 }}>Workspaces</Typography>
      {/* Public list of workspaces with Copy Link */}
      <List>
        {workspaces.map(ws => (
          <ListItem
            key={ws.id}
            secondaryAction={
              <Button size="small" onClick={() => handleCopy(ws.id)}>
                Copy Link
              </Button>
            }
          >
            <ListItemText primary={ws.name} />
          </ListItem>
        ))}
      </List>

      {/* Divider if you want */}
      <Box sx={{ my: 3 }} />

      {/* Admin/team management area */}
      <WorkspaceSelector onChange={setWorkspace} />
      {workspace && (
        <>
          <Box component="form" onSubmit={handleInvite} sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField label="Invite Email" value={inviteEmail} onChange={e => setInviteEmail(e.target.value)} size="small" />
            <Button type="submit" variant="contained">Invite</Button>
          </Box>
          <Typography variant="h6">Members</Typography>
          <TableContainer component={Paper} sx={{ mb: 2 }}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Email</TableCell>
                  <TableCell>Workspace</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {members.map(m => (
                  <TableRow key={m.id}>
                    <TableCell>{m.email}</TableCell>
                    <TableCell>
                      <select value={m.team_id || ''} onChange={e => handleAssign(m.id, e.target.value)}>
                        <option value="">None</option>
                        {data.workspaces.map(ws => (
                          <option key={ws.id} value={ws.id}>{ws.name}</option>
                        ))}
                      </select>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Typography variant="h6">Activity</Typography>
          <AuditLogTable logs={data.logs} />
        </>
      )}
    </Container>
  )
}
