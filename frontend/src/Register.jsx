import { useState } from 'react'
import { Box, TextField, Button, Typography } from '@mui/material'
import { registerUser } from './api.js'
import { useNavigate } from 'react-router-dom'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await registerUser({ username, email, password })
      navigate('/login')
    } catch (err) {
      alert(err.message)
    }
  }

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 4, mx: 'auto', maxWidth: 400, display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Typography variant="h5">Register</Typography>
      <TextField label="Username" value={username} onChange={e => setUsername(e.target.value)} required />
      <TextField label="Email" type="email" value={email} onChange={e => setEmail(e.target.value)} required />
      <TextField label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
      <Button type="submit" variant="contained">Register</Button>
    </Box>
  )
}
