import {
  AppBar,
  Box,
  Button,
  Paper,
  Stack,
  Toolbar,
  Typography,
} from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'

import { BrandLogo } from '../components/BrandLogo'

const features = [
  {
    number: '01',
    title: 'Itinerario organizado',
    body: 'Organiza destinos, actividades y horarios por día.',
    color: '#115bca',
  },
  {
    number: '02',
    title: 'Gastos bajo control',
    body: 'Controla el presupuesto y reparte gastos entre participantes.',
    color: '#067f56',
  },
  {
    number: '03',
    title: 'Documentación segura',
    body: 'Guarda reservas, notas y archivos importantes.',
    color: '#f97316',
  },
]

export function HomePage() {
  return (
    <Box
      component="main"
      sx={{
        minHeight: '100dvh',
        bgcolor: 'background.paper',
        display: 'flex',
        flexDirection: 'column',
        overflow: { md: 'hidden' },
      }}
    >
      <AppBar
        color="inherit"
        elevation={0}
        position="static"
        sx={{
          borderBottom: '1px solid #dce3ec',
          flexShrink: 0,
        }}
      >
        <Box
          sx={{
            width: '100%',
            px: { xs: 2.5, sm: 4, lg: 6 },
          }}
        >
          <Toolbar
            disableGutters
            sx={{
              minHeight: {
                xs: '72px !important',
                md: '80px !important',
              },
            }}
          >
            <BrandLogo />

            <Stack
              direction="row"
              spacing={1.5}
              sx={{ ml: 'auto' }}
            >
              <Button
                component={RouterLink}
                to="/iniciar-sesion"
                variant="outlined"
                color="inherit"
              >
                Iniciar sesión
              </Button>

              <Button
                component={RouterLink}
                to="/registro"
                variant="contained"
              >
                Registrarse
              </Button>
            </Stack>
          </Toolbar>
        </Box>
      </AppBar>

      <Box
        sx={{
          bgcolor: 'background.default',
          flex: { md: '1 1 60%' },
          display: 'flex',
          alignItems: 'center',
          px: { xs: 2.5, sm: 4, lg: 6 },
          py: { xs: 6, md: 3 },
        }}
      >
        <Box
          sx={{
            width: '100%',
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              md: '1fr 1fr',
            },
            gap: {
              xs: 6,
              md: 6,
              lg: 10,
            },
            alignItems: 'center',
          }}
        >
          <Box>
            <Typography
              color="primary"
              sx={{
                fontSize: 14,
                fontWeight: 700,
                letterSpacing: 0.3,
              }}
            >
              TU VIAJE, TODO EN UN MISMO LUGAR
            </Typography>

            <Typography
              component="h1"
              sx={{
                mt: 1.5,
                maxWidth: 700,
                fontSize: {
                  xs: 40,
                  sm: 48,
                  md: 'clamp(42px, 3vw, 56px)',
                },
                lineHeight: 1.08,
                fontWeight: 800,
                letterSpacing: -1.5,
              }}
            >
              Planifica cada momento. Disfruta todo el viaje.
            </Typography>

            <Typography
              color="text.secondary"
              sx={{
                mt: 2,
                maxWidth: 680,
                fontSize: {
                  xs: 16,
                  lg: 18,
                },
                lineHeight: 1.55,
              }}
            >
              Organiza itinerarios, reservas, gastos y documentos sin
              perderte entre aplicaciones. TripPlanner convierte tus planes
              en un viaje claro y compartido.
            </Typography>

            <Button
              component={RouterLink}
              to="/registro"
              variant="contained"
              size="large"
              sx={{
                mt: 3,
                px: 4,
                py: 1.6,
                fontSize: 17,
                fontWeight: 700,
                borderRadius: '10px',
              }}
            >
              Crear mi primer viaje
            </Button>
          </Box>

          <Box
  sx={{
    position: 'relative',
    height: {
      xs: 500,
      md: 'clamp(410px, 47vh, 480px)',
    },
    p: { xs: 2.5, sm: 3 },
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
    borderRadius: '30px',
    background:
      'linear-gradient(135deg, #e6f0ff 0%, #d5e6ff 55%, #c7dcff 100%)',
  }}
>
  {/* Decoración del fondo */}
  <Box
    sx={{
      position: 'absolute',
      width: 210,
      height: 210,
      borderRadius: '50%',
      bgcolor: 'rgba(255,255,255,0.35)',
      top: -95,
      right: -55,
    }}
  />

  <Box
    sx={{
      position: 'absolute',
      width: 120,
      height: 120,
      borderRadius: '50%',
      bgcolor: 'rgba(45,91,219,0.08)',
      bottom: -40,
      left: -30,
    }}
  />

  {/* Tarjeta del viaje */}
  <Paper
    variant="outlined"
    sx={{
      position: 'relative',
      zIndex: 1,
      width: '100%',
      maxWidth: 480,
      height: '100%',
      maxHeight: 425,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      borderRadius: '24px',
      borderColor: 'rgba(255,255,255,0.7)',
      bgcolor: 'white',
      boxShadow:
        '0 26px 60px rgba(30,64,175,0.2), 0 5px 14px rgba(15,23,42,0.09)',
      transition: 'transform 200ms ease, box-shadow 200ms ease',
      '&:hover': {
        transform: 'translateY(-5px)',
        boxShadow:
          '0 32px 72px rgba(30,64,175,0.25), 0 8px 18px rgba(15,23,42,0.11)',
      },
    }}
  >
    {/* Cabecera */}
    <Box
      sx={{
        position: 'relative',
        minHeight: 140,
        px: 3.2,
        py: 2.8,
        overflow: 'hidden',
        color: 'white',
        background:
          'linear-gradient(135deg, #1f4fd1 0%, #3267e8 58%, #5688f4 100%)',
      }}
    >
      {/* Círculos decorativos */}
      <Box
        sx={{
          position: 'absolute',
          width: 150,
          height: 150,
          borderRadius: '50%',
          bgcolor: 'rgba(255,255,255,0.09)',
          top: -65,
          right: -25,
        }}
      />

      <Box
        sx={{
          position: 'absolute',
          width: 65,
          height: 65,
          borderRadius: '50%',
          border: '1px solid rgba(255,255,255,0.18)',
          right: 65,
          bottom: -30,
        }}
      />

      <Box
        sx={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 2,
        }}
      >
        {/* Estado */}
        <Box
          sx={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 0.9,
            bgcolor: 'rgba(255,255,255,0.96)',
            color: '#1f5ed3',
            borderRadius: '999px',
            px: 1.7,
            py: 0.7,
            fontSize: 13,
            fontWeight: 800,
            boxShadow: '0 3px 10px rgba(15,23,42,0.12)',
          }}
        >
          <Box
            sx={{
              width: 8,
              height: 8,
              flexShrink: 0,
              borderRadius: '50%',
              bgcolor: '#2d63db',
            }}
          />

          Planificando
        </Box>

        <Typography
          sx={{
            color: 'rgba(255,255,255,0.85)',
            fontSize: 13,
            fontWeight: 700,
          }}
        >
          7 días
        </Typography>
      </Box>

      <Typography
        component="h3"
        sx={{
          position: 'relative',
          mt: 1.9,
          color: 'white',
          fontSize: { xs: 25, sm: 29 },
          lineHeight: 1.15,
          fontWeight: 800,
          letterSpacing: -0.5,
        }}
      >
        Aventura por Creta
      </Typography>

      <Typography
        sx={{
          position: 'relative',
          mt: 0.7,
          color: 'rgba(255,255,255,0.8)',
          fontSize: 14,
        }}
      >
        Tu próxima aventura por el Mediterráneo
      </Typography>
    </Box>

    {/* Contenido */}
    <Box
      sx={{
        px: 3.2,
        py: 2.5,
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Destinos */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 1.4,
        }}
      >
        <Box
          sx={{
            flexShrink: 0,
            width: 38,
            height: 38,
            display: 'grid',
            placeItems: 'center',
            borderRadius: '11px',
            bgcolor: '#eaf2ff',
            color: '#1f5ed3',
            fontSize: 18,
          }}
        >
          ◈
        </Box>

        <Box>
          <Typography
            color="text.secondary"
            sx={{
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: 0.8,
            }}
          >
            DESTINOS
          </Typography>

          <Typography
            sx={{
              mt: 0.3,
              color: 'text.primary',
              fontSize: 15,
              fontWeight: 600,
            }}
          >
            Heraclión · Matalá · Chania
          </Typography>

          <Typography
            color="text.secondary"
            sx={{
              mt: 0.15,
              fontSize: 13,
            }}
          >
            Grecia
          </Typography>
        </Box>
      </Box>

      {/* Fecha y presupuesto */}
      <Box
        sx={{
          mt: 2,
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: 1.4,
        }}
      >
        <Box
          sx={{
            bgcolor: '#f6f8fc',
            border: '1px solid #e6ebf2',
            borderRadius: '13px',
            px: 1.8,
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
            FECHAS
          </Typography>

          <Typography
            sx={{
              mt: 0.45,
              fontSize: 14,
              fontWeight: 700,
            }}
          >
            12–19 SEP 2026
          </Typography>
        </Box>

        <Box
          sx={{
            bgcolor: '#f6f8fc',
            border: '1px solid #e6ebf2',
            borderRadius: '13px',
            px: 1.8,
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
              mt: 0.45,
              color: '#1f5ed3',
              fontSize: 17,
              fontWeight: 800,
            }}
          >
            1.350 €
          </Typography>
        </Box>
      </Box>

      {/* Botón de la tarjeta */}
      <Button
        variant="contained"
        disableElevation
        sx={{
          mt: 'auto',
          minHeight: 46,
          bgcolor: '#e1edff',
          color: '#1459c7',
          fontSize: 15,
          fontWeight: 800,
          borderRadius: '12px',
          textTransform: 'none',
          '&:hover': {
            bgcolor: '#cfe1ff',
          },
          '&:hover .trip-arrow': {
            transform: 'translateX(4px)',
          },
        }}
      >
        Ver viaje

        <Box
          component="span"
          className="trip-arrow"
          sx={{
            ml: 1,
            fontSize: 20,
            lineHeight: 1,
            transition: 'transform 180ms ease',
          }}
        >
          →
        </Box>
      </Button>
    </Box>
  </Paper>
</Box>
        </Box>
      </Box>

      <Box
        sx={{
          flex: { md: '1 1 32%' },
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          px: { xs: 2.5, sm: 4, lg: 6 },
          py: { xs: 5, md: 2.5 },
        }}
      >
        <Typography
          sx={{
            component: "h2",
            fontSize: { xs: 24, md: 28 },
            fontWeight: 800
          }}
        >
          Todo lo que necesitas para viajar tranquilo
        </Typography>

        <Box
          sx={{
            mt: 2,
            display: 'grid',
            gridTemplateColumns: {
              xs: '1fr',
              md: 'repeat(3, 1fr)',
            },
            gap: {
              xs: 2,
              md: 3,
            },
          }}
        >
          {features.map((feature) => (
            <Paper
              key={feature.number}
              variant="outlined"
              sx={{
                borderColor: '#dce3ec',
                borderRadius: '18px',
                p: 2.5,
                minHeight: { md: 140 },
              }}
            >
              <Stack
                direction="row"
                spacing={2}
                sx={{
                  alignItems: 'flex-start',
                }}
              >
                <Box
                  sx={{
                    bgcolor: feature.color,
                    color: 'white',
                    borderRadius: '12px',
                    minWidth: 44,
                    height: 44,
                    display: 'grid',
                    placeItems: 'center',
                    fontSize: 13,
                    fontWeight: 700,
                  }}
                >
                  {feature.number}
                </Box>

                <Box>
                  <Typography
                    sx={{
                      fontSize: { xs: 19, lg: 21 },
                      fontWeight: 700,
                    }}
                  >
                    {feature.title}
                  </Typography>

                  <Typography
                    color="text.secondary"
                    sx={{
                      mt: 1,
                      fontSize: { xs: 15, lg: 16 },
                      lineHeight: 1.55,
                    }}
                  >
                    {feature.body}
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          ))}
        </Box>
      </Box>
    </Box>
  )
}