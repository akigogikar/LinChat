import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton } from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'

export default function WorkspaceTable({ workspaces, onDelete }) {
  return (
    <TableContainer component={Paper} sx={{marginTop:2}}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell></TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {workspaces.map(w => (
            <TableRow key={w.id}>
              <TableCell>{w.id}</TableCell>
              <TableCell>{w.name}</TableCell>
              <TableCell>
                <IconButton size="small" onClick={() => onDelete(w.id)}>
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
