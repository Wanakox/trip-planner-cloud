import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    primary: {
      main: '#115bca',
      dark: '#0d47a1',
      light: '#dbecff',
    },
    secondary: {
      main: '#067f56',
    },
    background: {
      default: '#f7fafd',
      paper: '#ffffff',
    },
    text: {
      primary: '#0b1a2f',
      secondary: '#475569',
    },
  },
  typography: {
    fontFamily: 'Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    button: {
      fontWeight: 600,
      textTransform: 'none',
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          minHeight: 48,
          boxShadow: 'none',
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        fullWidth: true,
      },
    },
  },
})
