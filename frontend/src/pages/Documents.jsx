import { useEffect, useState } from 'react'
import { Box, Button } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import { API_BASE, getDocuments, deleteDocument, setShared } from '../api.js'

export default function Documents() {
  const [docs, setDocs] = useState([])

  useEffect(() => {
    load()
  }, [])

  async function load() {
    try {
      const res = await getDocuments()
      setDocs(res.documents)
    } catch (err) {
      console.error(err)
    }
  }

  async function handleDelete(id) {
    if (!confirm('Delete document?')) return
    await deleteDocument(id)
    setDocs(docs.filter(d => d.id !== id))
  }

  async function handleToggle(id, shared) {
    const res = await setShared(id, !shared)
    setDocs(docs.map(d => (d.id === id ? { ...d, is_shared: res.is_shared } : d)))
  }

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'filename', headerName: 'Filename', flex: 1 },
    {
      field: 'is_shared',
      headerName: 'Shared',
      width: 90,
      valueGetter: params => (params.row.is_shared ? 'Yes' : 'No'),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 240,
      sortable: false,
      renderCell: params => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button size="small" onClick={() => handleDelete(params.row.id)}>
            Delete
          </Button>
          <Button size="small" onClick={() => handleToggle(params.row.id, params.row.is_shared)}>
            {params.row.is_shared ? 'Unshare' : 'Share'}
          </Button>
          <Button size="small" onClick={() => navigator.clipboard.writeText(`${API_BASE}/documents/${params.row.id}`)}>
            Copy Link
          </Button>
        </Box>
      ),
    },
  ]

  return (
    <Box>
      <h2>Documents</h2>
      <DataGrid
        autoHeight
        rows={docs}
        columns={columns}
        disableRowSelectionOnClick
        density="compact"
      />
    </Box>
  )
}
