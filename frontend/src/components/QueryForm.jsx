import { useState } from 'react'
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
    <div>
      <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
        <input
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          placeholder="Ask a question"
          style={{ width: '60%' }}
        />
        <button type="submit">Send</button>
      </form>
      {renderAnswer()}
      {citation && (
        <div style={{ border: '1px solid #ccc', padding: '0.5rem', marginTop: '1rem' }}>
          <strong>Citation:</strong> {citation.text}
        </div>
      )}
    </div>
  )
}
