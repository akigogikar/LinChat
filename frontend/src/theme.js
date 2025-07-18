import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  typography: {
    fontFamily: 'Arial, sans-serif',
  },
  components: {
    MuiContainer: {
      styleOverrides: {
        root: {
          paddingTop: '1rem',
          paddingBottom: '1rem',
        },
      },
    },
  },
})

export default theme
