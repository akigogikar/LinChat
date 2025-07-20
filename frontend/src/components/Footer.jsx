import { Box, Link, Stack } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import logo from '../assets/logo.svg'

export default function Footer() {
  return (
    <Box component="footer" sx={{ mt: 4, py: 2, textAlign: 'center', borderTop: 1, borderColor: 'divider' }}>
      <Stack spacing={1} alignItems="center">
        <Box component="img" src={logo} alt="LinChat" sx={{ height: 32 }} />
        <Stack direction="row" spacing={2}>
          <Link component={RouterLink} to="/about" underline="hover">
            About
          </Link>
          <Link component={RouterLink} to="/contact" underline="hover">
            Contact
          </Link>
          <Link component={RouterLink} to="/privacy" underline="hover">
            Privacy
          </Link>
        </Stack>
      </Stack>
    </Box>
  )
}
