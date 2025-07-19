import FileUpload from '../components/FileUpload.jsx'
import QueryForm from '../components/QueryForm.jsx'
import TableGenerator from '../components/TableGenerator.jsx'
import ChartUploader from '../components/ChartUploader.jsx'
import ExportButtons from '../components/ExportButtons.jsx'
import { useState } from 'react'
import { Stack } from '@mui/material'

export default function Home() {
  const [lastAnswer, setLastAnswer] = useState('')

  return (
    <Stack spacing={2}>
      <h1>LinChat Frontend</h1>
      <FileUpload />
      <QueryForm onAnswer={setLastAnswer} />
      <TableGenerator />
      <ChartUploader />
      <ExportButtons content={lastAnswer} />
    </Stack>
  )
}
