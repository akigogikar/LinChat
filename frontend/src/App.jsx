import FileUpload from './components/FileUpload.jsx'
import QueryForm from './components/QueryForm.jsx'
import TableGenerator from './components/TableGenerator.jsx'
import ChartUploader from './components/ChartUploader.jsx'
import ExportButtons from './components/ExportButtons.jsx'
import { useState } from 'react'
import AdminDashboard from './admin/AdminDashboard.jsx'
import './App.css'

function App() {
  const [lastAnswer, setLastAnswer] = useState('')

  return (
    <div className="App" style={{ padding: '1rem', fontFamily: 'Arial' }}>
      {window.location.pathname === '/admin' ? (
        <AdminDashboard />
      ) : (
        <>
          <h1>LinChat Frontend</h1>
          <FileUpload />
          <QueryForm onAnswer={setLastAnswer} />
          <TableGenerator />
          <ChartUploader />
          <ExportButtons content={lastAnswer} />
        </>
      )}
    </div>
  )
}

export default App
