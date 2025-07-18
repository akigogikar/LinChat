import { useState } from 'react'
import { Container, Typography } from '@mui/material'
import FileUpload from './components/FileUpload.jsx'
import QueryForm from './components/QueryForm.jsx'
import TableGenerator from './components/TableGenerator.jsx'
import ChartUploader from './components/ChartUploader.jsx'
import ExportButtons from './components/ExportButtons.jsx'
import './App.css'

function App() {
  const [lastAnswer, setLastAnswer] = useState('')

  return (
    <Container className="App">
      <Typography variant="h4" gutterBottom>
        LinChat Frontend
      </Typography>
      <FileUpload />
      <QueryForm onAnswer={setLastAnswer} />
      <TableGenerator />
      <ChartUploader />
      <ExportButtons content={lastAnswer} />
    </Container>
  )
}

export default App
