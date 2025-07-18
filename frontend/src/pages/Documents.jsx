import { useEffect, useState } from 'react'
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Stack,
} from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'
import { API_BASE, getDocuments, deleteDocument, setShared } from '../api.js'
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

  async function confirmDelete() {
    if (!deleteId) return
    await deleteDocument(deleteId)
    setDocs(docs.filter(d => d.id !== deleteId))
    setDeleteId(null)
  }

  const handleDelete = id => {
    setDeleteId(id)
  }

  async function handleToggle(id, shared) {
    const res = await setShared(id, !shared)
    setDocs(docs.map(d => (d.id === id ? { ...d, is_shared: res.is_shared } : d)))
  }

  const columns = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'filename', headerName: 'Filename', flex: 1 },
    { field: 'owner', headerName: 'Owner', width: 120 },
    {
      field: 'updated_at',
      headerName: 'Updated',
      width: 160,
      valueGetter: params =>
        params.row.updated_at ? new Date(params.row.updated_at).toLocaleString() : '',
    },
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
      <Dialog
        open={deleteId !== null}
        onClose={() => setDeleteId(null)}
        aria-labelledby="confirm-delete-title"
      >
        <DialogTitle id="confirm-delete-title">Delete Document</DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this document?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteId(null)}>Cancel</Button>
          <Button onClick={confirmDelete} autoFocus aria-label="confirm delete">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  )
}
