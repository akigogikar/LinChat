import { Box } from '@mui/material'
import { DataGrid } from '@mui/x-data-grid'

export default function AuditLogTable({ logs }) {
  const columns = [
    {
      field: 'timestamp',
      headerName: 'Time',
      flex: 1,
      valueGetter: params => new Date(params.row.timestamp).toLocaleString(),
    },
    { field: 'user_id', headerName: 'User', width: 80 },
    { field: 'action', headerName: 'Action', flex: 1 },
  ]

  return (
    <Box sx={{ mt: 2 }}>
      <DataGrid
        autoHeight
        rows={logs}
        columns={columns}
        disableRowSelectionOnClick
        density="compact"
      />
    </Box>
  )
}
