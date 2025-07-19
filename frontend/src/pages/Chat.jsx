import { useOutletContext } from 'react-router-dom'
import ChatView from '../components/ChatView.jsx'
import WorkspaceSelector from '../components/WorkspaceSelector.jsx'
import { Container, Stack, Typography } from '@mui/material'

export default function ChatPage() {
  const { workspace, setWorkspace } = useOutletContext()

  return (
    <Container sx={{ mt: 2 }}>
      <Stack spacing={2}>
        <WorkspaceSelector onChange={setWorkspace} />
        {workspace ? (
          <ChatView key={workspace.id} />
        ) : (
          <Typography>Select a workspace</Typography>
        )}
      </Stack>
    </Container>
  )
}

