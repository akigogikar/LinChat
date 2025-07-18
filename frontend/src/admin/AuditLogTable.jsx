import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material'

export default function AuditLogTable({ logs }) {
  return (
    <TableContainer component={Paper} sx={{marginTop:2}}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Time</TableCell>
            <TableCell>User</TableCell>
            <TableCell>Action</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {logs.map(l => (
            <TableRow key={l.id}>
              <TableCell>{new Date(l.timestamp).toLocaleString()}</TableCell>
              <TableCell>{l.user_id}</TableCell>
              <TableCell>{l.action}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
