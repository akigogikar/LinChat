import { useEffect, useState } from 'react'
import { Box, Button, List, ListItem, ListItemText } from '@mui/material'
import { API_BASE, getWorkspaces } from '../api.js'

export default function WorkspacePage() {
  const [workspaces, setWorkspaces] = useState([])

  useEffect(() => {
    getWorkspaces().then(res => setWorkspaces(res.workspaces || []))
  }, [])

  const handleCopy = id => {
    navigator.clipboard.writeText(`${window.location.origin}/workspace/${id}`)
  }

  return (
    <Box sx={{ mt: 2 }}>
      <h2>Workspaces</h2>
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
    </Box>
  )
}
