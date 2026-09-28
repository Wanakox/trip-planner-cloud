import FlightTakeoffOutlinedIcon from '@mui/icons-material/FlightTakeoffOutlined'
import HomeOutlinedIcon from '@mui/icons-material/HomeOutlined'
import MenuIcon from '@mui/icons-material/Menu'
import {
  Box,
  Drawer,
  IconButton,
  Stack,
  Typography,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
  NavLink,
  Outlet,
  useLocation,
} from 'react-router-dom'

import { BrandLogo } from '../BrandLogo'
import { UserAvatar } from '../UserAvatar'
import { getCurrentUser } from '../../api/user'

const drawerWidth = 250

type NavigationItem = {
  label: string
  path: string
  icon: typeof HomeOutlinedIcon
}

const navigationItems: NavigationItem[] = [
  {
    label: 'Mis viajes',
    path: '/viajes',
    icon: HomeOutlinedIcon,
  },
  {
    label: 'Buscar vuelos',
    path: '/buscar-vuelos',
    icon: FlightTakeoffOutlinedIcon,
  },
]

function DashboardSidebar({
  onNavigate,
}: {
  onNavigate?: () => void
}) {
  const location = useLocation()
  const profileQuery = useQuery({
    queryKey: ['current-user'],
    queryFn: getCurrentUser,
  })

  return (
    <Stack
      sx={{
        height: '100%',
        px: 2.2,
        py: 3,
      }}
    >
      <Box sx={{ px: 1.2 }}>
        <BrandLogo />
      </Box>

      <Stack
        component="nav"
        spacing={1}
        sx={{ mt: 5 }}
      >
        {navigationItems.map((item) => {
          const Icon = item.icon

          const isActive =
            item.path === '/viajes'
              ? location.pathname === '/viajes' ||
                location.pathname.startsWith(
                  '/viajes/',
                )
              : location.pathname.startsWith(
                  item.path,
                )

          return (
            <Box
              key={item.path}
              component={NavLink}
              to={item.path}
              onClick={onNavigate}
              sx={{
                minHeight: 48,
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
                px: 2,
                borderRadius: '12px',
                color: isActive
                  ? 'primary.main'
                  : 'text.secondary',
                bgcolor: isActive
                  ? 'primary.light'
                  : 'transparent',
                fontSize: 15,
                fontWeight: isActive ? 700 : 600,
                textDecoration: 'none',
                transition:
                  'background-color 160ms ease, color 160ms ease',
                '&:hover': {
                  bgcolor: isActive
                    ? 'primary.light'
                    : '#f1f5f9',
                  color: isActive
                    ? 'primary.main'
                    : 'text.primary',
                },
              }}
            >
              <Icon sx={{ fontSize: 20 }} />

              {item.label}
            </Box>
          )
        })}
      </Stack>

      <Box
        component={NavLink}
        to="/perfil"
        onClick={onNavigate}
        sx={{
          mt: 'auto',
          display: 'flex',
          alignItems: 'center',
          gap: 1.4,
          p: 1.2,
          borderRadius: '12px',
          color: 'text.primary',
          textDecoration: 'none',
          '&:hover': {
            bgcolor: '#f1f5f9',
          },
        }}
      >
        {profileQuery.data && <UserAvatar user={profileQuery.data} />}

        <Box sx={{ minWidth: 0 }}>
          <Typography
            sx={{
              fontSize: 14,
              fontWeight: 700,
            }}
          >
            {profileQuery.data
              ? `${profileQuery.data.name} ${profileQuery.data.surname}`
              : 'Mi perfil'}
          </Typography>

          <Typography
            color="text.secondary"
            sx={{
              mt: 0.2,
              fontSize: 12,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            Ver perfil
          </Typography>
        </Box>

        <Typography
  aria-hidden="true"
  sx={{
    ml: 'auto',
    color: 'text.secondary',
    fontSize: 20,
    lineHeight: 1,
  }}
>
  →
</Typography>
      </Box>
    </Stack>
  )
}

export function DashboardLayout() {
  const [mobileMenuOpen, setMobileMenuOpen] =
    useState(false)

  return (
    <Box
      sx={{
        minHeight: '100dvh',
        display: 'flex',
        bgcolor: 'background.default',
      }}
    >
      <Box
        component="aside"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          display: {
            xs: 'none',
            md: 'block',
          },
          borderRight: '1px solid #e2e8f0',
          bgcolor: 'background.paper',
        }}
      >
        <Box
          sx={{
            position: 'fixed',
            width: drawerWidth,
            height: '100dvh',
          }}
        >
          <DashboardSidebar />
        </Box>
      </Box>

      <Box
        sx={{
          display: {
            xs: 'block',
            md: 'none',
          },
        }}
      >
        <IconButton
          aria-label="Abrir menú"
          onClick={() => setMobileMenuOpen(true)}
          sx={{
            position: 'fixed',
            zIndex: 1100,
            top: 16,
            left: 16,
            bgcolor: 'background.paper',
            border: '1px solid #dce3ec',
            boxShadow:
              '0 6px 20px rgba(15,23,42,0.1)',
            '&:hover': {
              bgcolor: 'background.paper',
            },
          }}
        >
          <MenuIcon />
        </IconButton>

        <Drawer
          open={mobileMenuOpen}
          onClose={() => setMobileMenuOpen(false)}
          slotProps={{
            paper: {
              sx: {
                width: drawerWidth,
              },
            },
          }}
        >
          <DashboardSidebar
            onNavigate={() =>
              setMobileMenuOpen(false)
            }
          />
        </Drawer>
      </Box>

      <Box
        sx={{
          flex: 1,
          minWidth: 0,
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}
