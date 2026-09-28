import AddIcon from '@mui/icons-material/Add'
import DragIndicatorIcon from '@mui/icons-material/DragIndicator'
import {
    closestCenter,
    DndContext,
    KeyboardSensor,
    PointerSensor,
    useSensor,
    useSensors,
} from '@dnd-kit/core'
import type { DragEndEvent } from '@dnd-kit/core'
import {
    arrayMove,
    SortableContext,
    sortableKeyboardCoordinates,
    useSortable,
    verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import {
    Alert,
    Box,
    Button,
    Divider,
    IconButton,
    MenuItem,
    Paper,
    Stack,
    TextField,
    Typography,
} from '@mui/material'
import {
    useMutation,
    useQuery,
    useQueryClient,
} from '@tanstack/react-query'
import { getCurrencies } from '../api/currency'
import { isAxiosError } from 'axios'
import { useState } from 'react'
import type { ReactNode } from 'react'
import {
    Link as RouterLink,
    useNavigate,
} from 'react-router-dom'

import { createTrip } from '../api/trips'
import type {
    DestinationCreatePayload,
    TripCreatePayload,
} from '../types/trip'

interface DestinationForm extends DestinationCreatePayload {
    clientId: string
}

interface SortableDestinationProps {
    id: string
    children: ReactNode
}

function createEmptyDestination(): DestinationForm {
    return {
        clientId: crypto.randomUUID(),
        country: '',
        city: '',
        currency: 'EUR',
    }
}

function SortableDestination({
    id,
    children,
}: SortableDestinationProps) {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ id })

    return (
        <Box
            ref={setNodeRef}
            sx={{
                position: 'relative',
                transform: CSS.Transform.toString(transform),
                transition,
                zIndex: isDragging ? 2 : 1,
                opacity: isDragging ? 0.75 : 1,
            }}
        >
            <IconButton
                type="button"
                aria-label="Arrastrar destino"
                {...attributes}
                {...listeners}
                sx={{
                    position: 'absolute',
                    top: 17,
                    left: 16,
                    zIndex: 2,
                    cursor: isDragging ? 'grabbing' : 'grab',
                    touchAction: 'none',
                    color: 'text.secondary',
                }}
            >
                <DragIndicatorIcon />
            </IconButton>

            {children}
        </Box>
    )
}

function getErrorMessage(error: unknown) {
    if (!isAxiosError(error)) {
        return 'No se ha podido crear el viaje.'
    }

    if (error.response?.status === 422) {
        return 'Revisa los datos introducidos. Algunos campos no son válidos.'
    }

    if (error.response?.status === 503) {
        return 'El servicio de monedas no está disponible. Inténtalo más tarde.'
    }

    return 'No se ha podido crear el viaje. Inténtalo de nuevo.'
}

export function CreateTripPage() {
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const [name, setName] = useState('')
    const [origin, setOrigin] = useState('')
    const [description, setDescription] =
        useState('')
    const [startDate, setStartDate] =
        useState('')
    const [endDate, setEndDate] =
        useState('')
    const [budget, setBudget] = useState('0')

    const [destinations, setDestinations] =
        useState<DestinationForm[]>([
            createEmptyDestination(),
        ])

    const [validationError, setValidationError] =
        useState<string | null>(null)

    const sensors = useSensors(
        useSensor(PointerSensor),
        useSensor(KeyboardSensor, {
            coordinateGetter: sortableKeyboardCoordinates,
        }),
    )

    const currenciesQuery = useQuery({
        queryKey: ['currencies'],
        queryFn: getCurrencies,
        staleTime: 1000 * 60 * 60,
    })

    const mutation = useMutation({
        mutationFn: createTrip,

        onSuccess: async (createdTrip) => {
            await queryClient.invalidateQueries({
                queryKey: ['trips'],
            })

            navigate(`/viajes/${createdTrip.id}`, {
                replace: true,
            })
        },
    })

    const updateDestination = (
        index: number,
        field: keyof DestinationCreatePayload,
        value: string,
    ) => {
        setDestinations((currentDestinations) =>
            currentDestinations.map(
                (destination, destinationIndex) =>
                    destinationIndex === index
                        ? {
                            ...destination,
                            [field]: value,
                        }
                        : destination,
            ),
        )
    }

    const addDestination = () => {
        setDestinations((currentDestinations) => [
            ...currentDestinations,
            createEmptyDestination(),
        ])
    }

    const removeDestination = (index: number) => {
        setDestinations((currentDestinations) =>
            currentDestinations.filter(
                (_, destinationIndex) =>
                    destinationIndex !== index,
            ),
        )
    }

    const handleDragEnd = (event: DragEndEvent) => {
        const { active, over } = event

        if (!over || active.id === over.id) {
            return
        }

        setDestinations((currentDestinations) => {
            const oldIndex = currentDestinations.findIndex(
                (destination) =>
                    destination.clientId === active.id,
            )
            const newIndex = currentDestinations.findIndex(
                (destination) =>
                    destination.clientId === over.id,
            )

            if (oldIndex === -1 || newIndex === -1) {
                return currentDestinations
            }

            return arrayMove(
                currentDestinations,
                oldIndex,
                newIndex,
            )
        })
    }

    const handleSubmit = (
        event: React.FormEvent<HTMLFormElement>,
    ) => {
        event.preventDefault()
        setValidationError(null)

        if (endDate < startDate) {
            setValidationError(
                'La fecha de finalización no puede ser anterior a la fecha de inicio.',
            )
            return
        }

        if (Number(budget) < 0) {
            setValidationError(
                'El presupuesto no puede ser negativo.',
            )
            return
        }

        const payload: TripCreatePayload = {
            name: name.trim(),
            origin: origin.trim(),
            description:
                description.trim() || null,
            start_date: startDate,
            end_date: endDate,
            budget: Number(budget),
            destinations: destinations.map(
                (destination) => ({
                    country: destination.country.trim(),
                    city: destination.city.trim(),
                    currency:
                        destination.currency.toUpperCase(),
                }),
            ),
        }

        mutation.mutate(payload)
    }

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
                    maxWidth: 1000,
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
                    Crear viaje
                </Typography>

                <Typography
                    color="text.secondary"
                    sx={{
                        mt: 1,
                        fontSize: 16,
                    }}
                >
                    Añade la información principal de tu
                    próximo viaje.
                </Typography>

                <Paper
                    component="form"
                    variant="outlined"
                    onSubmit={handleSubmit}
                    sx={{
                        mt: 4,
                        borderRadius: '22px',
                        borderColor: '#dce3ec',
                        p: {
                            xs: 2.5,
                            sm: 4,
                        },
                    }}
                >
                    {(validationError ||
                        mutation.isError) && (
                            <Alert
                                severity="error"
                                sx={{ mb: 3 }}
                            >
                                {validationError ||
                                    getErrorMessage(mutation.error)}
                            </Alert>
                        )}

                    <Typography
                        component="h2"
                        sx={{
                            fontSize: 21,
                            fontWeight: 800,
                        }}
                    >
                        Información general
                    </Typography>

                    <Box
                        sx={{
                            mt: 3,
                            display: 'grid',
                            gridTemplateColumns: {
                                xs: '1fr',
                                md: '1fr 1fr',
                            },
                            gap: 2.5,
                        }}
                    >
                        <TextField
                            label="Nombre del viaje"
                            value={name}
                            onChange={(event) =>
                                setName(event.target.value)
                            }
                            required
                            slotProps={{
                                htmlInput: {
                                    maxLength: 150,
                                },
                            }}
                        />

                        <TextField
                            label="Lugar de origen"
                            value={origin}
                            onChange={(event) =>
                                setOrigin(event.target.value)
                            }
                            required
                            slotProps={{
                                htmlInput: {
                                    maxLength: 100,
                                },
                            }}
                        />

                        <TextField
                            label="Fecha de inicio"
                            type="date"
                            value={startDate}
                            onChange={(event) => {
                                setStartDate(event.target.value)

                                if (
                                    endDate &&
                                    endDate < event.target.value
                                ) {
                                    setEndDate(event.target.value)
                                }
                            }}
                            required
                            slotProps={{
                                inputLabel: {
                                    shrink: true,
                                },
                            }}
                        />

                        <TextField
                            label="Fecha de finalización"
                            type="date"
                            value={endDate}
                            onChange={(event) =>
                                setEndDate(event.target.value)
                            }
                            required
                            slotProps={{
                                inputLabel: {
                                    shrink: true,
                                },
                                htmlInput: {
                                    min: startDate || undefined,
                                },
                            }}
                        />

                        <TextField
                            label="Presupuesto"
                            type="number"
                            value={budget}
                            onChange={(event) =>
                                setBudget(event.target.value)
                            }
                            required
                            slotProps={{
                                htmlInput: {
                                    min: 0,
                                    step: 0.01,
                                },
                            }}
                        />

                        <TextField
                            label="Descripción"
                            value={description}
                            onChange={(event) =>
                                setDescription(event.target.value)
                            }
                            multiline
                            minRows={3}
                            sx={{
                                gridColumn: {
                                    md: '1 / -1',
                                },
                            }}
                            slotProps={{
                                htmlInput: {
                                    maxLength: 2000,
                                },
                            }}
                        />
                    </Box>

                    <Divider sx={{ my: 4 }} />

                    <Stack
                        direction={{
                            xs: 'column',
                            sm: 'row',
                        }}
                        spacing={2}
                        sx={{
                            alignItems: {
                                sm: 'center',
                            },
                            justifyContent: 'space-between',
                        }}
                    >
                        <Box>
                            <Typography
                                component="h2"
                                sx={{
                                    fontSize: 21,
                                    fontWeight: 800,
                                }}
                            >
                                Destinos
                            </Typography>

                            <Typography
                                color="text.secondary"
                                sx={{
                                    mt: 0.5,
                                    fontSize: 14,
                                }}
                            >
                                El viaje debe tener al menos un
                                destino.
                            </Typography>
                        </Box>

                        <Button
                            type="button"
                            variant="outlined"
                            startIcon={<AddIcon />}
                            onClick={addDestination}
                            disabled={
                                destinations.length >= 20
                            }
                        >
                            Añadir destino
                        </Button>
                    </Stack>

                    <DndContext
                        sensors={sensors}
                        collisionDetection={closestCenter}
                        onDragEnd={handleDragEnd}
                    >
                        <SortableContext
                            items={destinations.map(
                                (destination) =>
                                    destination.clientId,
                            )}
                            strategy={verticalListSortingStrategy}
                        >
                            <Stack spacing={2.5} sx={{ mt: 3 }}>
                                {destinations.map(
                                    (destination, index) => (
                                <SortableDestination
                                    key={destination.clientId}
                                    id={destination.clientId}
                                >
                                <Paper
                                    variant="outlined"
                                    sx={{
                                        position: 'relative',
                                        borderRadius: '16px',
                                        borderColor: '#e2e8f0',
                                        bgcolor: '#f8fafc',
                                        p: {
                                            xs: 2,
                                            sm: 2.5,
                                        },
                                        pl: {
                                            xs: 6.5,
                                            sm: 7,
                                        },
                                    }}
                                >
                                    <Stack
                                        direction="row"
                                        sx={{
                                            mb: 2,
                                            alignItems: 'center',
                                            justifyContent:
                                                'space-between',
                                        }}
                                    >
                                        <Typography
                                            sx={{
                                                fontSize: 15,
                                                fontWeight: 800,
                                            }}
                                        >
                                            Destino {index + 1}
                                        </Typography>

                                        <IconButton
                                            type="button"
                                            aria-label={`Eliminar destino ${index + 1}`}
                                            onClick={() =>
                                                removeDestination(index)
                                            }
                                            disabled={
                                                destinations.length === 1
                                            }
                                            color="error"
                                            size="small"
                                            sx={{
                                                fontSize: 22,
                                                fontWeight: 700,
                                            }}
                                        >
                                            ×
                                        </IconButton>
                                    </Stack>

                                    <Box
                                        sx={{
                                            display: 'grid',
                                            gridTemplateColumns: {
                                                xs: '1fr',
                                                md: '1fr 1fr 160px',
                                            },
                                            gap: 2,
                                        }}
                                    >
                                        <TextField
                                            label="País"
                                            value={destination.country}
                                            onChange={(event) =>
                                                updateDestination(
                                                    index,
                                                    'country',
                                                    event.target.value,
                                                )
                                            }
                                            required
                                        />

                                        <TextField
                                            label="Ciudad"
                                            value={destination.city}
                                            onChange={(event) =>
                                                updateDestination(
                                                    index,
                                                    'city',
                                                    event.target.value,
                                                )
                                            }
                                            required
                                        />

                                        <TextField
                                            select
                                            fullWidth
                                            required
                                            label="Moneda"
                                            value={destination.currency}
                                            onChange={(event) =>
                                                updateDestination(index, 'currency', event.target.value)
                                            }
                                            disabled={currenciesQuery.isPending || currenciesQuery.isError}
                                            error={currenciesQuery.isError}
                                            helperText={
                                                currenciesQuery.isPending
                                                    ? 'Cargando monedas…'
                                                    : currenciesQuery.isError
                                                        ? 'No se pudieron cargar las monedas.'
                                                        : undefined
                                            }
                                        >
                                            {(currenciesQuery.data ?? []).map((currency) => (
                                                <MenuItem key={currency.code} value={currency.code}>
                                                    {currency.code} — {currency.name}
                                                </MenuItem>
                                            ))}
                                        </TextField>
                                    </Box>
                                </Paper>
                                </SortableDestination>
                                    ),
                                )}
                            </Stack>
                        </SortableContext>
                    </DndContext>

                    <Divider sx={{ my: 4 }} />

                    <Stack
                        direction={{
                            xs: 'column-reverse',
                            sm: 'row',
                        }}
                        spacing={2}
                        sx={{
                            justifyContent: 'flex-end',
                        }}
                    >
                        <Button
                            component={RouterLink}
                            to="/viajes"
                            variant="outlined"
                            disabled={mutation.isPending}
                        >
                            Cancelar
                        </Button>

                        <Button
                            type="submit"
                            variant="contained"
                            disabled={
                                mutation.isPending ||
                                currenciesQuery.isPending ||
                                currenciesQuery.isError
                            }
                        >
                            {mutation.isPending
                                ? 'Creando viaje...'
                                : 'Crear viaje'}
                        </Button>
                    </Stack>
                </Paper>
            </Box>
        </Box>
    )
}
