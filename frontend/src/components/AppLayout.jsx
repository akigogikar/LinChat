import { useState } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Box,
  Typography
} from '@mui/material'
import WorkspaceSelector from './WorkspaceSelector.jsx'

const drawerWidth = 200

export default function AppLayout() {
  const [workspace, setWorkspace] = useState(null)

  const pages = [
    { name: 'Home', path: '/' },
    { name: 'Documents', path: '/documents' },
    { name: 'Chat', path: '/chat' },
    { name: 'Admin', path: '/admin' },
    { name: 'Login', path: '/login' },
    { name: 'Register', path: '/register' }
  ]

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: theme => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <WorkspaceSelector onChange={setWorkspace} />
          {workspace && (
            <Typography sx={{ ml: 2 }}>{workspace.name}</Typography>
          )}
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' }
        }}
      >
        <Toolbar />
        <List>
          {pages.map(p => (
            <ListItem key={p.path} disablePadding>
              <ListItemButton
                component={NavLink}
                to={p.path}
                end
                sx={{ '&.active': { bgcolor: 'action.selected' } }}
              >
                <ListItemText primary={p.name} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        <Outlet context={{ workspace }} />
      </Box>
    </Box>
  )
}
