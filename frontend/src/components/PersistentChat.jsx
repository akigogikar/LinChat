import Drawer from '@mui/material/Drawer'
import Box from '@mui/material/Box'
import ChatView from './ChatView.jsx'

const drawerWidth = 320

export default function PersistentChat() {
  return (
    <Drawer
      variant="permanent"
      anchor="right"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box', p: 2 },
      }}
    >
      <Box sx={{ width: '100%' }}>
        <ChatView />
      </Box>
    </Drawer>
  )
}
