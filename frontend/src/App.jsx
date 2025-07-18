import { useState } from 'react'
import { Container, Typography } from '@mui/material'
import FileUpload from './components/FileUpload.jsx'
import QueryForm from './components/QueryForm.jsx'
import TableGenerator from './components/TableGenerator.jsx'
import ChartUploader from './components/ChartUploader.jsx'
import ExportButtons from './components/ExportButtons.jsx'

import Login from './Login.jsx'
import Register from './Register.jsx'
import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Button } from '@mui/material'
import './App.css'

function Home() {
  return <h2>Home</h2>
}

function Documents() {
  const [lastAnswer, setLastAnswer] = useState('')
  return (
    <Container className="App">
      <Typography variant="h4" gutterBottom>
        LinChat Frontend
      </Typography>
    <div style={{ padding: '1rem' }}>
      <h2>Documents</h2>
      <FileUpload />
      <QueryForm onAnswer={setLastAnswer} />
      <TableGenerator />
      <ChartUploader />
      <ExportButtons content={lastAnswer} />
    </Container>
  )
}

function Admin() {
  return <h2>Admin</h2>
}

function App() {
  const token = localStorage.getItem('token')

  return (
    <Router>
      <AppBar position="static">
        <Toolbar>
          <Button color="inherit" component={Link} to="/">Home</Button>
          <Button color="inherit" component={Link} to="/documents">Documents</Button>
          {token && <Button color="inherit" component={Link} to="/admin">Admin</Button>}
          <Button color="inherit" component={Link} to="/login">Login</Button>
          <Button color="inherit" component={Link} to="/register">Register</Button>
        </Toolbar>
      </AppBar>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/documents" element={<Documents />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </Router>
  )
}

export default App
