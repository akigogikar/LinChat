import { Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Button, Box } from '@mui/material'
import { useState } from 'react'
import logo from './assets/logo.svg'

import AppLayout from './components/AppLayout.jsx'
import Onboarding from './components/Onboarding.jsx'
import PersistentChat from './components/PersistentChat.jsx'
import Footer from './components/Footer.jsx'

import Home from './pages/Home.jsx'
import Documents from './pages/Documents.jsx'
// Route used to mistakenly import from "ChatPage.jsx"; ensure path matches filename
import ChatPage from './pages/Chat.jsx'
import AdminDashboard from './admin/AdminDashboard.jsx'
import Login from './Login.jsx'
import Register from './Register.jsx'
import WorkspacePage from './pages/Workspace.jsx'
import Privacy from './pages/Privacy.jsx'
import About from './pages/About.jsx'
import Contact from './pages/Contact.jsx'

import './App.css'

export default function App() {
  const token = localStorage.getItem('token')
  const [showOnboarding, setShowOnboarding] = useState(
    localStorage.getItem('showOnboarding') === 'true'
  )

  const handleCloseOnboarding = () => {
    localStorage.setItem('onboardingSeen', 'true')
    localStorage.setItem('showOnboarding', 'false')
    setShowOnboarding(false)
  }

  return (
    <>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Box component="img" src={logo} alt="LinChat" sx={{ height: 32, mr: 2 }} />
          <Button color="inherit" component={Link} to="/">Home</Button>
          <Button color="inherit" component={Link} to="/documents">Documents</Button>
          <Button color="inherit" component={Link} to="/chat">Chat</Button>
          <Button color="inherit" component={Link} to="/workspace">Workspace</Button>
          {token && <Button color="inherit" component={Link} to="/admin">Admin</Button>}
          <Button color="inherit" component={Link} to="/login">Login</Button>
          <Button color="inherit" component={Link} to="/register">Register</Button>
        </Toolbar>
      </AppBar>

      <Box sx={{ display: 'flex' }}>
        <Box component="main" sx={{ flexGrow: 1, p: 2, mr: '320px' }}>
          <Routes>
            <Route path="/" element={<AppLayout />}>
              <Route index element={<Home />} />
              <Route path="documents" element={<Documents />} />
              <Route path="chat" element={<ChatPage />} />
              <Route path="workspace" element={<WorkspacePage />} />
              <Route path="admin" element={<AdminDashboard />} />
              <Route path="login" element={<Login />} />
              <Route path="register" element={<Register />} />
              <Route path="privacy" element={<Privacy />} />
              <Route path="about" element={<About />} />
              <Route path="contact" element={<Contact />} />
            </Route>
          </Routes>
        </Box>

        <PersistentChat />
      </Box>

      <Footer />

      <Onboarding open={showOnboarding} onClose={handleCloseOnboarding} />
    </>
  )
}
