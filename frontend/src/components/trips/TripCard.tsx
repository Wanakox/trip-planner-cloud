import ArrowForwardIcon from '@mui/icons-material/ArrowForward'
import CalendarMonthOutlinedIcon from '@mui/icons-material/CalendarMonthOutlined'
import LocationOnOutlinedIcon from '@mui/icons-material/LocationOnOutlined'
import {
  Box,
  Paper,
  Stack,
  Typography,
} from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

import type {
  Trip,
  TripStatus,
} from '../../types/trip'

type TripCardProps = {
  trip: Trip
}

type StatusConfig = {
  label: string
  color: string
  gradient: string
  lightColor: string
}

const statusConfig: Record<
  TripStatus,
  StatusConfig
> = {
  planning: {
    label: 'Planificando',
    color: '#2459d3',
    gradient:
      'linear-gradient(135deg, #1f4fd1 0%, #3267e8 58%, #5688f4 100%)',
    lightColor: '#e8f0ff',
  },
  in_progress: {
    label: 'En curso',
    color: '#c76a00',
    gradient:
      'linear-gradient(135deg, #d97706 0%, #f59e0b 58%, #fbbf24 100%)',
    lightColor: '#fff3dc',
  },
  completed: {
    label: 'Completado',
    color: '#07875c',
    gradient:
      'linear-gradient(135deg, #047857 0%, #079669 58%, #16b981 100%)',
    lightColor: '#e2f7ef',
  },
  cancelled: {
    label: 'Cancelado',
    color: '#d20f19',
    gradient:
      'linear-gradient(135deg, #c90d17 0%, #df1721 58%, #ef4444 100%)',
    lightColor: '#ffe7e8',
  },
}

function formatDate(date: string) {
  return new Intl.DateTimeFormat('es-ES', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
    .format(new Date(`${date}T00:00:00`))
    .replace('.', '')
    .toUpperCase()
}

function formatBudget(
  budget: string | number,
  currency: string,
) {
  return new Intl.NumberFormat('es-ES', {
    style: 'currency',
    currency,
    maximumFractionDigits: 2,
  }).format(Number(budget))
}

export function TripCard({
  trip,
}: TripCardProps) {
  const status = statusConfig[trip.status]

  const orderedDestinations = [
    ...trip.destinations,
  ].sort(
    (firstDestination, secondDestination) =>
      firstDestination.order -
      secondDestination.order,
  )

  const cities = orderedDestinations
    .map((destination) => destination.city)
    .join(' · ')

  const countries = [
    ...new Set(
      orderedDestinations.map(
        (destination) => destination.country,
      ),
    ),
  ].join(' · ')

  const dateRange = `${formatDate(
    trip.start_date,
  )} – ${formatDate(trip.end_date)}`

  const formattedBudget = formatBudget(
    trip.budget,
    trip.currency,
  )

  return (
    <Paper
      component={RouterLink}
      to={`/viajes/${trip.id}`}
      aria-label={`Ver detalles de ${trip.name}`}
      variant="outlined"
      sx={{
        height: '100%',
        minHeight: 440,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        borderRadius: '22px',
        borderColor: '#dce3ec',
        bgcolor: 'background.paper',
        color: 'text.primary',
        textDecoration: 'none',
        cursor: 'pointer',
        boxShadow: '0 10px 30px rgba(15, 23, 42, 0.06)',
        transition:
          'transform 180ms ease, box-shadow 180ms ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow:
            '0 18px 42px rgba(15, 23, 42, 0.11)',
        },
        '&:focus-visible': {
          outline: '3px solid',
          outlineColor: 'primary.main',
          outlineOffset: 3,
        },
      }}
    >
      <Box
        sx={{
          position: 'relative',
          minHeight: 150,
          px: 3,
          py: 2.5,
          overflow: 'hidden',
          color: 'white',
          background: status.gradient,
        }}
      >
        <Box
          aria-hidden="true"
          sx={{
            position: 'absolute',
            width: 155,
            height: 155,
            borderRadius: '50%',
            bgcolor: 'rgba(255,255,255,0.14)',
            top: -70,
            right: -30,
          }}
        />

        <Box
          aria-hidden="true"
          sx={{
            position: 'absolute',
            width: 72,
            height: 72,
            borderRadius: '50%',
            border:
              '2px solid rgba(255,255,255,0.28)',
            right: 70,
            bottom: -38,
          }}
        />

        <Stack
          direction="row"
          spacing={2}
          sx={{
            position: 'relative',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <Box
            sx={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 0.8,
              borderRadius: '999px',
              bgcolor: 'rgba(255,255,255,0.96)',
              color: status.color,
              px: 1.6,
              py: 0.65,
              fontSize: 12,
              fontWeight: 800,
              boxShadow:
                '0 3px 10px rgba(15,23,42,0.12)',
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                flexShrink: 0,
                borderRadius: '50%',
                bgcolor: status.color,
              }}
            />

            {status.label}
          </Box>

          <Typography
            sx={{
              color: 'rgba(255,255,255,0.88)',
              fontSize: 13,
              fontWeight: 700,
            }}
          >
            {trip.total_days}{' '}
            {trip.total_days === 1
              ? 'día'
              : 'días'}
          </Typography>
        </Stack>

        <Typography
          component="h2"
          sx={{
            position: 'relative',
            mt: 2,
            color: 'white',
            fontSize: {
              xs: 24,
              sm: 27,
            },
            lineHeight: 1.15,
            fontWeight: 800,
            letterSpacing: -0.4,
          }}
        >
          {trip.name}
        </Typography>

        <Typography
          sx={{
            position: 'relative',
            mt: 0.8,
            minHeight: 22,
            color: 'rgba(255,255,255,0.82)',
            fontSize: 14,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {trip.description ||
            'Todo preparado para tu próximo viaje'}
        </Typography>
      </Box>

      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          px: 3,
          py: 2.5,
        }}
      >
        <Stack
          direction="row"
          spacing={1.5}
          sx={{
            alignItems: 'flex-start',
          }}
        >
          <Box
            sx={{
              flexShrink: 0,
              width: 40,
              height: 40,
              display: 'grid',
              placeItems: 'center',
              borderRadius: '12px',
              bgcolor: status.lightColor,
              color: status.color,
            }}
          >
            <LocationOnOutlinedIcon
              fontSize="small"
            />
          </Box>

          <Box sx={{ minWidth: 0 }}>
            <Typography
              color="text.secondary"
              sx={{
                fontSize: 10,
                fontWeight: 800,
                letterSpacing: 0.8,
              }}
            >
              DESTINOS
            </Typography>

            <Typography
              sx={{
                mt: 0.3,
                fontSize: 15,
                fontWeight: 700,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {cities || 'Sin destinos'}
            </Typography>

            {countries && (
              <Typography
                color="text.secondary"
                sx={{
                  mt: 0.15,
                  fontSize: 13,
                }}
              >
                {countries}
              </Typography>
            )}
          </Box>
        </Stack>

        <Box
          sx={{
            mt: 2.2,
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              sm: '1fr 1fr',
            },
            gap: 1.4,
          }}
        >
          <Box
            sx={{
              minWidth: 0,
              border: '1px solid #e6ebf2',
              borderRadius: '13px',
              bgcolor: '#f7f9fc',
              px: 1.7,
              py: 1.4,
            }}
          >
            <Stack
              direction="row"
              spacing={0.7}
              sx={{ alignItems: 'center' }}
            >
              <CalendarMonthOutlinedIcon
                sx={{
                  color: 'text.secondary',
                  fontSize: 16,
                }}
              />

              <Typography
                color="text.secondary"
                sx={{
                  fontSize: 10,
                  fontWeight: 800,
                  letterSpacing: 0.7,
                }}
              >
                FECHAS
              </Typography>
            </Stack>

            <Typography
              sx={{
                mt: 0.55,
                fontSize: 12,
                fontWeight: 700,
              }}
            >
              {dateRange}
            </Typography>
          </Box>

          <Box
            sx={{
              minWidth: 0,
              border: '1px solid #e6ebf2',
              borderRadius: '13px',
              bgcolor: '#f7f9fc',
              px: 1.7,
              py: 1.4,
            }}
          >
            <Typography
              color="text.secondary"
              sx={{
                fontSize: 10,
                fontWeight: 800,
                letterSpacing: 0.7,
              }}
            >
              PRESUPUESTO
            </Typography>

            <Typography
              sx={{
                mt: 0.55,
                color: status.color,
                fontSize: 17,
                fontWeight: 800,
              }}
            >
              {formattedBudget}
            </Typography>
          </Box>
        </Box>

        <Box
          component="span"
          sx={{
            mt: 'auto',
            minHeight: 46,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 1,
            px: 2,
            py: 1.25,
            borderRadius: '12px',
            bgcolor: status.lightColor,
            color: status.color,
            fontSize: 14,
            fontWeight: 800,
            '&:hover': {
              bgcolor: status.lightColor,
              filter: 'brightness(0.97)',
            },
            '& .trip-arrow': {
              transition: 'transform 180ms ease',
            },
            '&:hover .trip-arrow': {
              transform: 'translateX(4px)',
            },
          }}
        >
          Ver viaje
          <ArrowForwardIcon
            className="trip-arrow"
            fontSize="small"
          />
        </Box>
      </Box>
    </Paper>
  )
}
