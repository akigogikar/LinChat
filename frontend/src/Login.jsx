import { useState } from 'react'
import { Box, TextField, Button, Typography } from '@mui/material'
import { loginUser } from './api.js'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const data = await loginUser(username, password)
      if (data.access_token) {
        localStorage.setItem('token', data.access_token)
        // trigger onboarding on first login
        if (!localStorage.getItem('onboardingSeen')) {
          localStorage.setItem('showOnboarding', 'true')
        }
      }
      navigate('/')
    } catch (err) {
      alert(err.message)
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4, mx: 'auto', maxWidth: 400, display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Typography variant="h5">Login</Typography>
      <TextField label="Username" value={username} onChange={e => setUsername(e.target.value)} required />
      <TextField label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
      <Button type="submit" variant="contained">Login</Button>
    </Box>
  )
}
