import { useState } from 'react'
import {
  Box,
  Button,
  TextField,
  Paper,
  Typography,
  Link,
  Stack
} from '@mui/material'
import { API_BASE, queryLLM, exportPdf, uploadFile, createChatSession } from '../api.js'
import { useChatSession } from '../ChatContext.jsx'

export default function ChatView() {
  const sessionId = useChatSession()
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([])
  const [pdfUrl, setPdfUrl] = useState(null)

  function handleDragOver(e) {
    e.preventDefault()
  }

  async function handleDrop(e) {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (!file) return
    try {
      const res = await uploadFile(file)
      setMessages(m => [
        ...m,
        { role: 'assistant', content: `Uploaded ${res.document_id}` },
      ])
    } catch (err) {
      setMessages(m => [...m, { role: 'assistant', content: err.toString() }])
    }
  }

  async function handleSend(e) {
    e.preventDefault()
    if (!prompt) return
    setMessages(m => [...m, { role: 'user', content: prompt }])
    try {
      const res = await queryLLM(prompt, sessionId)
      setMessages(m => [...m, { role: 'assistant', content: res.response }])
    } catch (err) {
      setMessages(m => [...m, { role: 'assistant', content: err.toString() }])
    }
    setPrompt('')
  }

  async function handleExport() {
    const text = messages
      .map(m => `**${m.role === 'user' ? 'User' : 'Assistant'}:** ${m.content}`)
      .join('\n\n')
    const link = await exportPdf(text)
    // Immediately download PDF
    const a = document.createElement('a')
    a.href = link
    a.download = 'chat.pdf'
    document.body.appendChild(a)
    a.click()
    a.remove()
    setPdfUrl(link)
  }

  return (
    <Box onDragOver={handleDragOver} onDrop={handleDrop}>
      <Stack
        component="form"
        onSubmit={handleSend}
        spacing={1}
        direction={{ xs: 'column', sm: 'row' }}
        sx={{ mb: 2 }}
      >
        <TextField
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          fullWidth
          size="small"
        />
        <Button type="submit" variant="contained" aria-label="send message">
          Send
        </Button>
      </Stack>

      <Stack role="log" spacing={1}>
        {messages.map((m, idx) => (
          <Paper key={idx} sx={{ p: 1 }}>
            <Typography variant="subtitle2" component="span">
              {m.role === 'user' ? 'User:' : 'Assistant:'}
            </Typography>{' '}
            <span dangerouslySetInnerHTML={{ __html: m.content }} />
          </Paper>
        ))}
      </Stack>

      <Button
        variant="contained"
        onClick={handleExport}
        sx={{ mt: 2 }}
        aria-label="export conversation as PDF"
      >
        Export PDF
      </Button>
      <Button
        variant="outlined"
        href={`${API_BASE}/chat/${sessionId}/export/pdf`}
        target="_blank"
        sx={{ mt: 2, ml: 1 }}
      >
        Share Transcript
      </Button>
      {pdfUrl && (
        <Link href={pdfUrl} download="chat.pdf" sx={{ ml: 1 }}>
          Download
        </Link>
      )}
    </Box>
  )
}
