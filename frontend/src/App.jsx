
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { AppBar, Toolbar, Button } from '@mui/material'
import Home from './pages/Home.jsx'
import Documents from './pages/Documents.jsx'
import Login from './Login.jsx'
import Register from './Register.jsx'
import AdminDashboard from './admin/AdminDashboard.jsx'
import './App.css'

export default function App() {
  const token = localStorage.getItem('token')


function Documents() {
  const [lastAnswer, setLastAnswer] = useState('')
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
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </Router>

  )
}
