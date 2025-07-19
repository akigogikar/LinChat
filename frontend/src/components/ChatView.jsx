import { useEffect, useState } from 'react'
import { Box, Button, TextField, Paper, Typography, Link, Stack } from '@mui/material'
import { createChatSession, queryLLM, exportPdf } from '../api.js'

export default function ChatView() {
  const [sessionId, setSessionId] = useState(null)
  const [prompt, setPrompt] = useState('')
  const [messages, setMessages] = useState([])
  const [pdfUrl, setPdfUrl] = useState(null)

  useEffect(() => {
    createChatSession().then(res => setSessionId(res.id))
  }, [])

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
    setPdfUrl(link)
  }

  return (
    <Box>
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
      {pdfUrl && (
        <Link href={pdfUrl} download="chat.pdf" sx={{ ml: 1 }}>
          Download
        </Link>
      )}
    </Box>
  )
}
