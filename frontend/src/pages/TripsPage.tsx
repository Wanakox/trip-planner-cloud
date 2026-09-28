import AddIcon from '@mui/icons-material/Add'
import SearchIcon from '@mui/icons-material/Search'
import {
    Alert,
    Box,
    Button,
    CircularProgress,
    InputAdornment,
    MenuItem,
    Paper,
    Stack,
    TextField,
    Typography,
} from '@mui/material'
import { useQuery } from '@tanstack/react-query'
import { useMemo, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'

import { getTrips } from '../api/trips'
import { TripCard } from '../components/trips/TripCard'
import type { TripStatus } from '../types/trip'

type StatusFilter = TripStatus | 'all'

export function TripsPage() {
    const [search, setSearch] = useState('')

    const [statusFilter, setStatusFilter] =
        useState<StatusFilter>('all')

    const {
        data: trips = [],
        isLoading,
        isError,
        refetch,
    } = useQuery({
        queryKey: ['trips'],
        queryFn: getTrips,
    })

    const filteredTrips = useMemo(() => {
        const normalizedSearch = search
            .trim()
            .toLowerCase()

        return trips.filter((trip) => {
            const matchesName = trip.name
                .toLowerCase()
                .includes(normalizedSearch)

            const matchesOrigin = trip.origin
                .toLowerCase()
                .includes(normalizedSearch)

            const matchesDestination =
                trip.destinations.some((destination) => {
                    const matchesCity = destination.city
                        .toLowerCase()
                        .includes(normalizedSearch)

                    const matchesCountry =
                        destination.country
                            .toLowerCase()
                            .includes(normalizedSearch)

                    return matchesCity || matchesCountry
                })

            const matchesSearch =
                normalizedSearch.length === 0 ||
                matchesName ||
                matchesOrigin ||
                matchesDestination

            const matchesStatus =
                statusFilter === 'all' ||
                trip.status === statusFilter

            return matchesSearch && matchesStatus
        })
    }, [search, statusFilter, trips])

    const hasActiveFilters =
        search.trim().length > 0 ||
        statusFilter !== 'all'

    const clearFilters = () => {
        setSearch('')
        setStatusFilter('all')
    }

    return (
        <Box
            component="main"
            sx={{
                width: '100%',
                minHeight: '100dvh',
                bgcolor: 'background.default',
                px: {
                    xs: 2,
                    sm: 3,
                    md: 5,
                    lg: 6,
                },
                pt: {
                    xs: 10,
                    md: 5,
                },
                pb: {
                    xs: 3,
                    md: 5,
                },
            }}
        >
            <Box
                sx={{
                    width: '100%',
                    maxWidth: 1400,
                    mx: 'auto',
                }}
            >
                <Box>
                    <Typography
                        component="h1"
                        sx={{
                            fontSize: {
                                xs: 32,
                                md: 38,
                            },
                            lineHeight: 1.1,
                            fontWeight: 800,
                            letterSpacing: -0.8,
                        }}
                    >
                        Mis viajes
                    </Typography>

                    <Typography
                        color="text.secondary"
                        sx={{
                            mt: 1,
                            fontSize: {
                                xs: 15,
                                md: 16,
                            },
                        }}
                    >
                        Organiza y consulta todos tus planes
                        desde aquí.
                    </Typography>
                </Box>

                <Stack
                    direction={{
                        xs: 'column',
                        md: 'row',
                    }}
                    spacing={2}
                    sx={{
                        mt: 4,
                        alignItems: {
                            xs: 'stretch',
                            md: 'center',
                        },
                    }}
                >
                    <TextField
                        value={search}
                        onChange={(event) =>
                            setSearch(event.target.value)
                        }
                        placeholder="Buscar por nombre o destino..."
                        aria-label="Buscar viajes"
                        sx={{
                            flex: 1,
                            maxWidth: {
                                md: 620,
                            },
                            bgcolor: 'background.paper',
                            '& .MuiOutlinedInput-root': {
                                minHeight: 52,
                            },
                        }}
                        slotProps={{
                            input: {
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <SearchIcon
                                            sx={{
                                                color: 'text.secondary',
                                                fontSize: 20,
                                            }}
                                        />
                                    </InputAdornment>
                                ),
                            },
                        }}
                    />

                    <TextField
                        select
                        value={statusFilter}
                        onChange={(event) =>
                            setStatusFilter(
                                event.target
                                    .value as StatusFilter,
                            )
                        }
                        aria-label="Filtrar viajes por estado"
                        sx={{
                            width: {
                                xs: '100%',
                                md: 190,
                            },
                            bgcolor: 'background.paper',
                            '& .MuiOutlinedInput-root': {
                                minHeight: 52,
                            },
                        }}
                    >
                        <MenuItem value="all">
                            Todos
                        </MenuItem>

                        <MenuItem value="planning">
                            Planificando
                        </MenuItem>

                        <MenuItem value="in_progress">
                            En curso
                        </MenuItem>

                        <MenuItem value="completed">
                            Completados
                        </MenuItem>

                        <MenuItem value="cancelled">
                            Cancelados
                        </MenuItem>
                    </TextField>

                    <Button
                        component={RouterLink}
                        to="/viajes/nuevo"
                        variant="contained"
                        startIcon={<AddIcon />}
                        sx={{
                            minWidth: {
                                md: 170,
                            },
                            minHeight: 52,
                            ml: {
                                md: 'auto',
                            },
                            borderRadius: '12px',
                            fontWeight: 700,
                        }}
                    >
                        Crear viaje
                    </Button>
                </Stack>

                {isLoading && (
                    <Box
                        sx={{
                            minHeight: 360,
                            display: 'grid',
                            placeItems: 'center',
                        }}
                    >
                        <Stack
                            spacing={2}
                            sx={{
                                alignItems: 'center',
                            }}
                        >
                            <CircularProgress />

                            <Typography color="text.secondary">
                                Cargando tus viajes...
                            </Typography>
                        </Stack>
                    </Box>
                )}

                {isError && (
                    <Alert
                        severity="error"
                        sx={{
                            mt: 4,
                            borderRadius: '14px',
                            alignItems: 'center',
                        }}
                        action={
                            <Button
                                color="inherit"
                                onClick={() => refetch()}
                            >
                                Reintentar
                            </Button>
                        }
                    >
                        No se han podido cargar tus viajes.
                        Comprueba la conexión e inténtalo de
                        nuevo.
                    </Alert>
                )}

                {!isLoading &&
                    !isError &&
                    trips.length === 0 && (
                        <Paper
                            variant="outlined"
                            sx={{
                                mt: 4,
                                minHeight: 320,
                                display: 'grid',
                                placeItems: 'center',
                                borderRadius: '20px',
                                borderColor: '#dce3ec',
                                bgcolor: 'background.paper',
                                p: 4,
                            }}
                        >
                            <Box
                                sx={{
                                    maxWidth: 440,
                                    textAlign: 'center',
                                }}
                            >
                                <Box
                                    sx={{
                                        width: 64,
                                        height: 64,
                                        mx: 'auto',
                                        display: 'grid',
                                        placeItems: 'center',
                                        borderRadius: '18px',
                                        bgcolor: 'primary.light',
                                        color: 'primary.main',
                                        fontSize: 30,
                                        fontWeight: 800,
                                    }}
                                >
                                    ✦
                                </Box>

                                <Typography
                                    component="h2"
                                    sx={{
                                        mt: 2.5,
                                        fontSize: 22,
                                        fontWeight: 800,
                                    }}
                                >
                                    Todavía no tienes viajes
                                </Typography>

                                <Typography
                                    color="text.secondary"
                                    sx={{
                                        mt: 1,
                                        lineHeight: 1.6,
                                    }}
                                >
                                    Cuando crees tu primer viaje,
                                    aparecerá en esta página.
                                </Typography>

                                <Button
                                    component={RouterLink}
                                    to="/viajes/nuevo"
                                    variant="contained"
                                    startIcon={<AddIcon />}
                                    sx={{
                                        mt: 3,
                                    }}
                                >
                                    Crear mi primer viaje
                                </Button>
                            </Box>
                        </Paper>
                    )}

                {!isLoading &&
                    !isError &&
                    trips.length > 0 &&
                    filteredTrips.length === 0 && (
                        <Paper
                            variant="outlined"
                            sx={{
                                mt: 4,
                                borderRadius: '16px',
                                borderColor: '#dce3ec',
                                p: 4,
                                textAlign: 'center',
                            }}
                        >
                            <Typography
                                component="h2"
                                sx={{
                                    fontSize: 20,
                                    fontWeight: 700,
                                }}
                            >
                                No se han encontrado viajes
                            </Typography>

                            <Typography
                                color="text.secondary"
                                sx={{ mt: 1 }}
                            >
                                Prueba con otra búsqueda o cambia
                                el filtro de estado.
                            </Typography>

                            {hasActiveFilters && (
                                <Button
                                    variant="outlined"
                                    onClick={clearFilters}
                                    sx={{ mt: 2.5 }}
                                >
                                    Limpiar filtros
                                </Button>
                            )}
                        </Paper>
                    )}

                {!isLoading &&
                    !isError &&
                    filteredTrips.length > 0 && (
                        <>
                            <Stack
                                direction="row"
                                sx={{
                                    mt: 4,
                                    alignItems: 'center',
                                    justifyContent: 'space-between',
                                }}
                            >
                                <Typography
                                    color="text.secondary"
                                    sx={{
                                        fontSize: 14,
                                        fontWeight: 600,
                                    }}
                                >
                                    {filteredTrips.length}{' '}
                                    {filteredTrips.length === 1
                                        ? 'viaje encontrado'
                                        : 'viajes encontrados'}
                                </Typography>

                                {hasActiveFilters && (
                                    <Button
                                        size="small"
                                        onClick={clearFilters}
                                    >
                                        Limpiar filtros
                                    </Button>
                                )}
                            </Stack>

                            <Box
                                sx={{
                                    mt: 2,
                                    display: 'grid',
                                    gridTemplateColumns: {
                                        xs: 'minmax(0, 1fr)',
                                        md: 'repeat(2, minmax(0, 1fr))',
                                        xl: 'repeat(3, minmax(0, 1fr))',
                                    },
                                    gap: 3,
                                    alignItems: 'stretch',
                                }}
                            >
                                {filteredTrips.map((trip) => (
                                    <TripCard
                                        key={trip.id}
                                        trip={trip}
                                    />
                                ))}
                            </Box>
                        </>
                    )}
            </Box>
        </Box>
    )
}