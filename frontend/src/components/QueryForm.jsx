import { useState } from 'react'
import { Box, Button, TextField, Paper, Typography } from '@mui/material'
import { queryLLM, getCitation } from '../api.js'

export default function QueryForm({ onAnswer }) {
  const [prompt, setPrompt] = useState('')
  const [answer, setAnswer] = useState('')
  const [reqId, setReqId] = useState(null)
  const [citation, setCitation] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    try {
      const res = await queryLLM(prompt)
      setAnswer(res.response)
      setReqId(res.request_id)
      if (onAnswer) onAnswer(res.response)
    } catch (err) {
      setAnswer(err.toString())
    }
  }

  async function handleCitation(cid) {
    if (!reqId) return
    const data = await getCitation(reqId, cid)
    setCitation(data)
  }

  function renderAnswer() {
    if (!answer) return null
    const html = { __html: answer }
    return (
      <div
        dangerouslySetInnerHTML={html}
        onClick={e => {
          if (e.target.tagName === 'A') {
            e.preventDefault()
            const cid = e.target.textContent.replace(/\[|\]/g, '')
            handleCitation(cid)
          }
        }}
      />
    )
  }

  return (
    <Box>
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ mb: 2, display: 'flex', gap: 1 }}
      >
        <TextField
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Ask a question"
          fullWidth
          size="small"
        />
        <Button type="submit" variant="contained">
          Send
        </Button>
      </Box>
      {renderAnswer()}
      {citation && (
        <Paper sx={{ p: 1, mt: 2 }}>
          <Typography variant="subtitle2" component="span">
            Citation:
          </Typography>{' '}
          {citation.text}
        </Paper>
      )}
    </Box>
  )
}
