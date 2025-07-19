import { Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Button, Box } from '@mui/material'
import Home from './pages/Home.jsx'
import Documents from './pages/Documents.jsx'
import ChatPage from './pages/Chat.jsx'
import PersistentChat from './components/PersistentChat.jsx'
import Login from './Login.jsx'
import Register from './Register.jsx'
import AdminDashboard from './admin/AdminDashboard.jsx'
import './App.css'

export default function App() {
  const token = localStorage.getItem('token')

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          <Button color="inherit" component={Link} to="/documents">Documents</Button>
          <Button color="inherit" component={Link} to="/chat">Chat</Button>
          {token && <Button color="inherit" component={Link} to="/admin">Admin</Button>}
          <Button color="inherit" component={Link} to="/login">Login</Button>
          <Button color="inherit" component={Link} to="/register">Register</Button>
        </Toolbar>
      </AppBar>
      <Box sx={{ display: 'flex' }}>
        <Box component="main" sx={{ flexGrow: 1, p: 2, mr: '320px' }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </Box>
        <PersistentChat />
      </Box>
    </>
  )
}
