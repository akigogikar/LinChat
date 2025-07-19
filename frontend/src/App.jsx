import { Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Button } from '@mui/material'
import Home from './pages/Home.jsx'
import Documents from './pages/Documents.jsx'
import ChatPage from './pages/Chat.jsx'
import Privacy from './pages/Privacy.jsx'
import About from './pages/About.jsx'
import Contact from './pages/Contact.jsx'
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
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
      </Routes>
    </>
  )
}
