import { useEffect, useState } from 'react'
import { Box, Button, Stack } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import { API_BASE, getDocuments, setShared } from '../api.js'
import UploadDropzone from '../components/UploadDropzone.jsx'


export default function Documents() {
  const [docs, setDocs] = useState([])
  const [sortModel, setSortModel] = useState([{ field: 'filename', sort: 'asc' }])
  const [filterModel, setFilterModel] = useState({ items: [] })


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


  async function handleToggle(id, shared) {
    const res = await setShared(id, !shared)
    setDocs(docs.map(d => (d.id === id ? { ...d, is_shared: res.is_shared } : d)))
  }

  const columns = [
    { field: 'filename', headerName: 'Name', flex: 1 },
    { field: 'owner', headerName: 'Owner', width: 160 },
    {
      field: 'is_shared',
      headerName: 'Shared',
      width: 90,
      valueGetter: params => (params.row.is_shared ? 'Yes' : 'No'),
    },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 220,
      sortable: false,
      renderCell: params => (
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button size="small" onClick={() => window.open(`${API_BASE}/documents/${params.row.id}`)}>
            Preview
          </Button>
          <Button size="small" onClick={() => handleToggle(params.row.id, params.row.is_shared)}>
            {params.row.is_shared ? 'Unshare' : 'Share'}
          </Button>
        </Box>
      ),
    },
  ]

  return (
    <Stack spacing={2}>
      <h2>Documents</h2>
      <UploadDropzone onUploaded={load} />
      <DataGrid
        autoHeight
        rows={docs}
        columns={columns}
        disableRowSelectionOnClick
        density="compact"
        sortModel={sortModel}
        onSortModelChange={setSortModel}
        filterModel={filterModel}
        onFilterModelChange={setFilterModel}
      />
    </Stack>
  )
}
