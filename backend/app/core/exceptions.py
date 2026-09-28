class TripPlannerError(Exception):
    """Base exception with a user-facing default message."""

    default_message = "Se ha producido un error en TripPlanner."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


# ============================================================
# AUTENTICACIÓN Y USUARIOS
# ============================================================


class EmailAlreadyRegisteredError(TripPlannerError):
    """El correo electrónico ya está asociado a otro usuario."""

    default_message = "El correo electrónico ya está asociado a otro usuario."


class UsernameAlreadyRegisteredError(TripPlannerError):
    """El nombre de usuario ya está asociado a otro usuario."""

    default_message = "El nombre de usuario ya está asociado a otro usuario."


class InvalidCredentialsError(TripPlannerError):
    """El identificador o la contraseña son incorrectos."""

    default_message = "El identificador o la contraseña son incorrectos."


# ============================================================
# MONEDAS Y SERVICIOS EXTERNOS
# ============================================================


class CurrencyProviderError(TripPlannerError):
    """No se pudo obtener información del proveedor de monedas."""

    default_message = "No se pudo obtener información del proveedor de monedas."


class UnsupportedCurrencyError(TripPlannerError):
    """El código de moneda no está soportado."""

    default_message = "El código de moneda no está soportado."


# ============================================================
# VIAJES
# ============================================================


class TripNotFoundError(TripPlannerError):
    """El viaje no existe o no pertenece al usuario."""

    default_message = "El viaje no existe o no pertenece al usuario."


class InvalidTripDatesError(TripPlannerError):
    """La fecha final es anterior a la fecha inicial."""

    default_message = "La fecha final es anterior a la fecha inicial."


class TripNotCompletedError(TripPlannerError):
    """El viaje todavía no está completado."""

    default_message = "El viaje todavía no está completado."


# ============================================================
# DESTINOS
# ============================================================


class DestinationNotFoundError(TripPlannerError):
    """El destino no existe o no pertenece al viaje indicado."""

    default_message = "El destino no existe o no pertenece al viaje indicado."


class LastDestinationDeletionError(TripPlannerError):
    """No se puede eliminar el único destino de un viaje."""

    default_message = "No se puede eliminar el único destino de un viaje."


class DestinationLimitExceededError(TripPlannerError):
    """El viaje ha alcanzado el número máximo de destinos."""

    default_message = "El viaje ha alcanzado el número máximo de destinos."


# ============================================================
# ORDENACIÓN
# ============================================================


class InvalidDestinationOrderError(TripPlannerError):
    """La lista de destinos no representa un orden válido."""

    default_message = "La lista de destinos no representa un orden válido."


class InvalidActivityOrderError(TripPlannerError):
    """La lista de actividades no representa un orden válido."""

    default_message = "La lista de actividades no representa un orden válido."


# ============================================================
# ACTIVIDADES
# ============================================================


class ActivityNotFoundError(TripPlannerError):
    """La actividad no existe o no pertenece al viaje indicado."""

    default_message = "La actividad no existe o no pertenece al viaje indicado."


class InvalidActivityDayError(TripPlannerError):
    """El número de día no está dentro de la duración del viaje."""

    default_message = "El número de día no está dentro de la duración del viaje."


# ============================================================
# TRANSPORTES
# ============================================================


class TransportNotFoundError(TripPlannerError):
    """El transporte no existe o no pertenece al viaje indicado."""

    default_message = "El transporte no existe o no pertenece al viaje indicado."


class InvalidTransportDatesError(TripPlannerError):
    """Las fechas u horas del transporte no son coherentes."""

    default_message = "Las fechas u horas del transporte no son coherentes."


class TransportOutsideTripDatesError(TripPlannerError):
    """El transporte se encuentra fuera de las fechas del viaje."""

    default_message = "El transporte se encuentra fuera de las fechas del viaje."


# ============================================================
# ALOJAMIENTOS
# ============================================================


class AccommodationNotFoundError(TripPlannerError):
    """El alojamiento no existe o no pertenece al viaje indicado."""

    default_message = "El alojamiento no existe o no pertenece al viaje indicado."


class InvalidAccommodationDatesError(TripPlannerError):
    """Las fechas u horas del alojamiento no son coherentes."""

    default_message = "Las fechas u horas del alojamiento no son coherentes."


class AccommodationOutsideTripDatesError(TripPlannerError):
    """El alojamiento se encuentra fuera de las fechas del viaje."""

    default_message = "El alojamiento se encuentra fuera de las fechas del viaje."


# ============================================================
# PARTICIPANTES
# ============================================================


class ParticipantNotFoundError(TripPlannerError):
    """El participante no existe o no pertenece al viaje indicado."""

    default_message = "El participante no existe o no pertenece al viaje indicado."


class ParticipantHasExpensesError(TripPlannerError):
    """El participante tiene gastos asociados y no puede eliminarse."""

    default_message = "El participante tiene gastos asociados y no puede eliminarse."


# ============================================================
# GASTOS
# ============================================================


class ExpenseNotFoundError(TripPlannerError):
    """El gasto no existe o no pertenece al viaje indicado."""

    default_message = "El gasto no existe o no pertenece al viaje indicado."


class InvalidExpenseAmountError(TripPlannerError):
    """La cantidad del gasto debe ser mayor que cero."""

    default_message = "La cantidad del gasto debe ser mayor que cero."


# ============================================================
# TAREAS
# ============================================================


class TaskNotFoundError(TripPlannerError):
    """La tarea no existe o no pertenece al viaje indicado."""

    default_message = "La tarea no existe o no pertenece al viaje indicado."


class InvalidTaskOrderError(TripPlannerError):
    """La lista de tareas no representa un orden válido."""

    default_message = "La lista de tareas no representa un orden válido."


# ============================================================
# NOTAS
# ============================================================


class NoteNotFoundError(TripPlannerError):
    """La nota no existe o no pertenece al viaje indicado."""

    default_message = "La nota no existe o no pertenece al viaje indicado."


class InvalidNoteDayError(TripPlannerError):
    """El número de día no está dentro de la duración del viaje."""

    default_message = "El número de día no está dentro de la duración del viaje."


class NoteLimitExceededError(TripPlannerError):
    """El viaje ha alcanzado el número máximo de notas permitido."""

    default_message = "El viaje ha alcanzado el número máximo de notas permitido."


class NoteDayAlreadyExistsError(TripPlannerError):
    """Ya existe una nota asociada al día indicado del viaje."""

    default_message = "Ya existe una nota asociada al día indicado del viaje."


class NotesUnavailableError(TripPlannerError):
    """Las notas no están disponibles para el estado actual del viaje."""

    default_message = "Las notas solo están disponibles durante o después del viaje."


# ============================================================
# ARCHIVOS
# ============================================================


class TripFileNotFoundError(TripPlannerError):
    """El archivo no existe o no pertenece al viaje indicado."""

    default_message = "El archivo no existe o no pertenece al viaje indicado."


class TripFileLimitExceededError(TripPlannerError):
    """El viaje ha alcanzado el número máximo de archivos permitido."""

    default_message = "El viaje ha alcanzado el número máximo de archivos permitido."


class TripFileStorageError(TripPlannerError):
    """Se produjo un error al gestionar el archivo almacenado."""

    default_message = "Se produjo un error al gestionar el archivo almacenado."


# ============================================================
# EXPORTACIÓN DE VIAJES
# ============================================================


class TripExportError(TripPlannerError):
    """No se pudo generar la exportación del viaje."""

    default_message = "No se pudo generar la exportación del viaje."


# ============================================================
# VUELOS Y SERVICIOS EXTERNOS
# ============================================================


class FlightProviderError(TripPlannerError):
    """No se pudo obtener información del proveedor de vuelos."""

    default_message = "No se pudo obtener información del proveedor de vuelos."
