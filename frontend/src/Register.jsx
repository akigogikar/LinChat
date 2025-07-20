import { useState } from 'react'
import {
  Box,
  TextField,
  Button,
  Typography,
  Container,
  Paper,
  Stack,
  Link,
} from '@mui/material'
import { registerUser } from './api.js'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import logo from './assets/logo.svg'

export default function Register() {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    const fieldErrors = {}
    if (!username) fieldErrors.username = 'Username required'
    if (!email) fieldErrors.email = 'Email required'
    if (!password) fieldErrors.password = 'Password required'
    setErrors(fieldErrors)
    if (Object.keys(fieldErrors).length > 0) return
    try {
      await registerUser({ username, email, password })
      navigate('/login')
    } catch (err) {
      setErrors({ password: err.message })
    }
  }

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper sx={{ p: 4 }}>
        <Stack spacing={2} component="form" onSubmit={handleSubmit}>
          <Box sx={{ textAlign: 'center' }}>
            <Box component="img" src={logo} alt="LinChat" sx={{ height: 48, mb: 1 }} />
            <Typography variant="h5">Create an Account</Typography>
          </Box>
          <TextField
            label="Username"
            value={username}
            onChange={e => setUsername(e.target.value)}
            error={Boolean(errors.username)}
            helperText={errors.username}
            required
          />
          <TextField
            label="Email"
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            error={Boolean(errors.email)}
            helperText={errors.email}
            required
          />
          <TextField
            label="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            error={Boolean(errors.password)}
            helperText={errors.password}
            required
          />
          <Button type="submit" variant="contained" sx={{ width: { xs: '100%', sm: '50%' }, alignSelf: 'center' }}>
            Register
          </Button>
          <Box sx={{ textAlign: 'center' }}>
            <Link component={RouterLink} to="/login" underline="hover">
              Already have an account? Login
            </Link>
          </Box>
        </Stack>
      </Paper>
    </Container>
  )
}
