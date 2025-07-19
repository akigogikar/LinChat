import { createContext, useContext, useEffect, useState } from 'react'
import { createChatSession } from './api.js'

const ChatSessionContext = createContext(null)

export function ChatProvider({ children }) {
  const [sessionId, setSessionId] = useState(null)

  useEffect(() => {
    createChatSession().then(res => setSessionId(res.id)).catch(console.error)
  }, [])

  return (
    <ChatSessionContext.Provider value={sessionId}>
      {children}
    </ChatSessionContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useChatSession() {
  return useContext(ChatSessionContext)
}
