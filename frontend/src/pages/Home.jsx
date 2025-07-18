import FileUpload from '../components/FileUpload.jsx'
import QueryForm from '../components/QueryForm.jsx'
import TableGenerator from '../components/TableGenerator.jsx'
import ChartUploader from '../components/ChartUploader.jsx'
import ExportButtons from '../components/ExportButtons.jsx'
import { useState } from 'react'

export default function Home() {
  const [lastAnswer, setLastAnswer] = useState('')

  return (
    <div>
      <h1>LinChat Frontend</h1>
      <FileUpload />
      <QueryForm onAnswer={setLastAnswer} />
      <TableGenerator />
      <ChartUploader />
      <ExportButtons content={lastAnswer} />
    </div>
  )
}
