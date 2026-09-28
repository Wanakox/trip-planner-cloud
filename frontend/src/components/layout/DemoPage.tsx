import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import ConstructionOutlinedIcon from '@mui/icons-material/ConstructionOutlined'
import {
  Box,
  Button,
  Paper,
  Typography,
} from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

type DemoPageProps = {
  title: string
  description: string
}

export function DemoPage({
  title,
  description,
}: DemoPageProps) {
  return (
    <Box
      component="main"
      sx={{
        minHeight: '100dvh',
        px: {
          xs: 2,
          sm: 4,
          lg: 6,
        },
        pt: {
          xs: 10,
          md: 5,
        },
        pb: 5,
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: 1100,
          mx: 'auto',
        }}
      >
        <Typography
          component="h1"
          sx={{
            fontSize: {
              xs: 32,
              md: 38,
            },
            fontWeight: 800,
            letterSpacing: -0.8,
          }}
        >
          {title}
        </Typography>

        <Typography
          color="text.secondary"
          sx={{
            mt: 1,
            fontSize: 16,
          }}
        >
          {description}
        </Typography>

        <Paper
          variant="outlined"
          sx={{
            mt: 4,
            minHeight: 420,
            display: 'grid',
            placeItems: 'center',
            borderRadius: '22px',
            borderColor: '#dce3ec',
            bgcolor: 'background.paper',
            p: 4,
          }}
        >
          <Box
            sx={{
              maxWidth: 520,
              textAlign: 'center',
            }}
          >
            <Box
              sx={{
                width: 76,
                height: 76,
                mx: 'auto',
                display: 'grid',
                placeItems: 'center',
                borderRadius: '22px',
                bgcolor: 'primary.light',
                color: 'primary.main',
              }}
            >
              <ConstructionOutlinedIcon
                sx={{ fontSize: 38 }}
              />
            </Box>

            <Typography
              component="h2"
              sx={{
                mt: 3,
                fontSize: 25,
                fontWeight: 800,
              }}
            >
              Vista en construcción
            </Typography>

            <Typography
              color="text.secondary"
              sx={{
                mt: 1.5,
                lineHeight: 1.7,
              }}
            >
              Esta es una demostración temporal.
              La funcionalidad completa se añadirá
              en una fase posterior del desarrollo.
            </Typography>

            <Button
              component={RouterLink}
              to="/viajes"
              variant="contained"
              startIcon={<ArrowBackIcon />}
              sx={{ mt: 3 }}
            >
              Volver a mis viajes
            </Button>
          </Box>
        </Paper>
      </Box>
    </Box>
  )
}