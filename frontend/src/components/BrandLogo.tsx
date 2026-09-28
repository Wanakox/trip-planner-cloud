import { Box, Stack, Typography } from '@mui/material'
import {
  Link as RouterLink,
  useNavigate,
} from 'react-router-dom'

import {
  clearStoredSession,
  hasValidAccessToken,
} from '../utils/authSession'

type BrandLogoProps = {
  inverse?: boolean
}

export function BrandLogo({ inverse = false }: BrandLogoProps) {
  const navigate = useNavigate()

  const handleClick = (
    event: React.MouseEvent<HTMLAnchorElement>,
  ) => {
    event.preventDefault()

    if (hasValidAccessToken()) {
      navigate('/viajes')
      return
    }

    clearStoredSession()
    navigate('/')
  }

  return (
    <Stack
      component={RouterLink}
      direction="row"
      spacing={1.5}
      to="/"
      onClick={handleClick}
      sx={{
        alignItems: 'center',
        color: inverse ? 'white' : 'text.primary',
        textDecoration: 'none',
      }}
    >
      <Box sx={{ width: 40, height: 40, borderRadius: '12px', bgcolor: inverse ? 'white' : 'primary.main', color: inverse ? 'primary.main' : 'white', display: 'grid', placeItems: 'center', fontSize: 22, fontWeight: 800 }}>
        ✦
      </Box>
      <Typography
        sx={{
          fontSize: 22,
          fontWeight: 800,
        }}
      >
        TripPlanner
      </Typography>
    </Stack>
  )
}
