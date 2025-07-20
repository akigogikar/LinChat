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
import { loginUser } from './api.js'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import logo from './assets/logo.svg'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    const fieldErrors = {}
    if (!username) fieldErrors.username = 'Username required'
    if (!password) fieldErrors.password = 'Password required'
    setErrors(fieldErrors)
    if (Object.keys(fieldErrors).length > 0) return
    try {
      const data = await loginUser(username, password)
      if (data.access_token) {
        localStorage.setItem('token', data.access_token)
        if (!localStorage.getItem('onboardingSeen')) {
          localStorage.setItem('showOnboarding', 'true')
        } else {
          localStorage.setItem('showOnboarding', 'false')
        }
      }
      navigate('/')
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
            <Typography variant="h5">Login to LinChat</Typography>
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
            label="Password"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            error={Boolean(errors.password)}
            helperText={errors.password}
            required
          />
          <Button type="submit" variant="contained" sx={{ width: { xs: '100%', sm: '50%' }, alignSelf: 'center' }}>
            Login
          </Button>
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Link component={RouterLink} to="/forgot-password" underline="hover">
              Forgot password?
            </Link>
            <Link component={RouterLink} to="/register" underline="hover">
              Create an account
            </Link>
          </Box>
        </Stack>
      </Paper>
    </Container>
  )
}
