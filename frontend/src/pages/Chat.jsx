import { useOutletContext } from 'react-router-dom'
import ChatView from '../components/ChatView.jsx'
import { Container, Typography } from '@mui/material'

export default function ChatPage() {
  const { workspace } = useOutletContext()

  return (
    <Container sx={{ mt: 2 }}>
      {workspace ? (
        <ChatView key={workspace.id} />
      ) : (
        <Typography>Select a workspace</Typography>
      )}
    </Container>
  )
}
