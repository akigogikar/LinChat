import { useState } from 'react'
import WorkspaceSelector from '../components/WorkspaceSelector.jsx'
import ChatView from '../components/ChatView.jsx'
import { Container, Stack } from '@mui/material'

export default function ChatPage() {
  const [ws, setWs] = useState(null)
  return (
    <Container sx={{ mt: 2 }}>
      <Stack spacing={2}>
        <WorkspaceSelector onChange={setWs} />
        {ws && <ChatView key={ws} />}
      </Stack>
    </Container>
  )
}
