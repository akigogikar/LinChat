import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home.jsx'
import Documents from './pages/Documents.jsx'
import ChatPage from './pages/Chat.jsx'
import Login from './Login.jsx'
import Register from './Register.jsx'
import AdminDashboard from './admin/AdminDashboard.jsx'
import AppLayout from './components/AppLayout.jsx'
import './App.css'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}> 
        <Route index element={<Home />} />
        <Route path="documents" element={<Documents />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="admin" element={<AdminDashboard />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
      </Route>
    </Routes>
  )
}
