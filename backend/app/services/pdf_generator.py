from collections import defaultdict
from datetime import date, time
from decimal import Decimal
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    Flowable,
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from app.models.trip import Trip
from app.schemas.timeline import TimelineResponse


PRIMARY_COLOR = colors.HexColor("#2F80ED")
SECONDARY_COLOR = colors.HexColor("#56CCF2")
ACCENT_COLOR = colors.HexColor("#27AE60")
WARNING_COLOR = colors.HexColor("#F2994A")
TEXT_COLOR = colors.HexColor("#2D3436")
MUTED_COLOR = colors.HexColor("#636E72")
LIGHT_BLUE = colors.HexColor("#EAF4FF")
LIGHT_GREEN = colors.HexColor("#ECF9F1")
LIGHT_ORANGE = colors.HexColor("#FFF4E8")
LIGHT_GRAY = colors.HexColor("#F7F9FB")
BORDER_COLOR = colors.HexColor("#D9E2EC")


def format_date(value: date | None) -> str:
    if value is None:
        return "-"

    return value.strftime("%d/%m/%Y")


def format_short_date(value: date | None) -> str:
    if value is None:
        return "-"

    return value.strftime("%d/%m")


def format_time(value: time | None) -> str:
    if value is None:
        return "-"

    return value.strftime("%H:%M")


def format_money(
    value: Decimal | None,
    currency: str,
) -> str:
    if value is None:
        return "-"

    return f"{value:.2f} {currency}"


def humanize(value: str) -> str:
    return value.replace("_", " ").strip().title()


def enum_value(value: Any) -> str:
    raw_value = getattr(value, "value", str(value))
    return humanize(raw_value)


def safe_text(value: object | None) -> str:
    if value is None:
        return "-"

    return escape(str(value))


def safe_multiline_text(value: object | None) -> str:
    if value is None:
        return "-"

    return escape(str(value)).replace(
        "\n",
        "<br/>",
    )


def create_pdf_styles() -> dict[str, ParagraphStyle]:
    sample_styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "TripTitle",
            parent=sample_styles["Title"],
            alignment=TA_CENTER,
            fontSize=24,
            leading=30,
            textColor=PRIMARY_COLOR,
            spaceAfter=8,
        ),
        "subtitle": ParagraphStyle(
            "TripSubtitle",
            parent=sample_styles["Heading2"],
            alignment=TA_CENTER,
            fontSize=12,
            leading=17,
            textColor=MUTED_COLOR,
            spaceAfter=18,
        ),
        "section": ParagraphStyle(
            "TripSection",
            parent=sample_styles["Heading2"],
            fontSize=16,
            leading=20,
            textColor=PRIMARY_COLOR,
            spaceBefore=14,
            spaceAfter=4,
        ),
        "item_title_blue": ParagraphStyle(
            "TripItemTitleBlue",
            parent=sample_styles["Heading3"],
            fontSize=12,
            leading=16,
            textColor=PRIMARY_COLOR,
            spaceAfter=5,
        ),
        "item_title_green": ParagraphStyle(
            "TripItemTitleGreen",
            parent=sample_styles["Heading3"],
            fontSize=12,
            leading=16,
            textColor=ACCENT_COLOR,
            spaceAfter=5,
        ),
        "item_title_orange": ParagraphStyle(
            "TripItemTitleOrange",
            parent=sample_styles["Heading3"],
            fontSize=12,
            leading=16,
            textColor=WARNING_COLOR,
            spaceAfter=5,
        ),
        "normal": ParagraphStyle(
            "TripNormal",
            parent=sample_styles["BodyText"],
            fontSize=10,
            leading=14,
            textColor=TEXT_COLOR,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "TripSmall",
            parent=sample_styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=MUTED_COLOR,
        ),
        "muted": ParagraphStyle(
            "TripMuted",
            parent=sample_styles["BodyText"],
            fontSize=9,
            leading=12,
            textColor=MUTED_COLOR,
            spaceAfter=4,
        ),
        "timeline_day": ParagraphStyle(
            "TimelineDay",
            parent=sample_styles["Heading3"],
            fontSize=12,
            leading=16,
            textColor=PRIMARY_COLOR,
            spaceBefore=8,
            spaceAfter=4,
        ),
    }


class SegmentedTimelineFlowable(Flowable):
    """
    Dibuja una línea temporal segmentada por días.
    Si hay muchos días, los reparte en varias filas.
    """

    def __init__(
        self,
        days: list[Any],
        days_per_row: int = 7,
    ) -> None:
        super().__init__()
        self.days = days
        self.days_per_row = days_per_row
        self.row_height = 2.8 * cm
        self.side_margin = 0.8 * cm
        self.node_radius = 0.22 * cm

    def _chunk_days(self) -> list[list[Any]]:
        return [
            self.days[index : index + self.days_per_row]
            for index in range(
                0,
                len(self.days),
                self.days_per_row,
            )
        ]

    def wrap(
        self,
        availWidth: float,
        availHeight: float,
    ) -> tuple[float, float]:
        self.width = availWidth
        rows = max(
            len(self._chunk_days()),
            1,
        )
        self.height = rows * self.row_height
        return availWidth, self.height

    def draw(self) -> None:
        canvas = self.canv
        rows = self._chunk_days()

        if not rows:
            return

        for row_index, row_days in enumerate(rows):
            row_top = self.height - (row_index * self.row_height)
            line_y = row_top - 1.0 * cm
            label_day_y = line_y - 0.55 * cm
            label_date_y = line_y - 0.9 * cm

            start_x = self.side_margin
            end_x = self.width - self.side_margin

            if len(row_days) == 1:
                positions = [
                    (start_x + end_x) / 2
                ]
            else:
                step = (
                    end_x - start_x
                ) / (len(row_days) - 1)
                positions = [
                    start_x + (step * index)
                    for index in range(len(row_days))
                ]

            canvas.setStrokeColor(SECONDARY_COLOR)
            canvas.setLineWidth(3)

            if len(positions) > 1:
                canvas.line(
                    positions[0],
                    line_y,
                    positions[-1],
                    line_y,
                )

            for x_position, day in zip(
                positions,
                row_days,
                strict=False,
            ):
                canvas.setFillColor(PRIMARY_COLOR)
                canvas.circle(
                    x_position,
                    line_y,
                    self.node_radius,
                    stroke=0,
                    fill=1,
                )

                canvas.setFillColor(colors.white)
                canvas.setFont(
                    "Helvetica-Bold",
                    8,
                )
                canvas.drawCentredString(
                    x_position,
                    line_y - 3,
                    str(day.day_number),
                )

                canvas.setFillColor(TEXT_COLOR)
                canvas.setFont(
                    "Helvetica-Bold",
                    8,
                )
                canvas.drawCentredString(
                    x_position,
                    label_day_y,
                    f"Día {day.day_number}",
                )

                canvas.setFillColor(MUTED_COLOR)
                canvas.setFont(
                    "Helvetica",
                    7,
                )
                canvas.drawCentredString(
                    x_position,
                    label_date_y,
                    format_short_date(day.date),
                )


def add_section_header(
    story: list[object],
    title: str,
    styles: dict[str, ParagraphStyle],
    line_color: colors.Color = PRIMARY_COLOR,
) -> None:
    story.append(
        Paragraph(
            title,
            styles["section"],
        )
    )
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.3,
            color=line_color,
            spaceBefore=0,
            spaceAfter=10,
        )
    )


def add_key_value_line(
    story: list[object],
    label: str,
    value: object | None,
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(
        Paragraph(
            f"<b>{escape(label)}:</b> {safe_text(value)}",
            styles["normal"],
        )
    )


def add_block_separator(
    story: list[object],
    color: colors.Color = BORDER_COLOR,
) -> None:
    story.append(
        Spacer(
            1,
            0.1 * cm,
        )
    )
    story.append(
        HRFlowable(
            width="100%",
            thickness=0.8,
            color=color,
            spaceBefore=0,
            spaceAfter=8,
        )
    )


def add_general_information(
    story: list[object],
    trip: Trip,
    styles: dict[str, ParagraphStyle],
) -> None:
    add_section_header(
        story=story,
        title="Información general",
        styles=styles,
        line_color=PRIMARY_COLOR,
    )

    add_key_value_line(
        story,
        "Nombre",
        trip.name,
        styles,
    )
    add_key_value_line(
        story,
        "Origen",
        trip.origin,
        styles,
    )
    add_key_value_line(
        story,
        "Fechas",
        f"{format_date(trip.start_date)} - {format_date(trip.end_date)}",
        styles,
    )
    add_key_value_line(
        story,
        "Duración",
        f"{trip.total_days} días",
        styles,
    )
    add_key_value_line(
        story,
        "Presupuesto",
        format_money(
            trip.budget,
            trip.currency,
        ),
        styles,
    )
    add_key_value_line(
        story,
        "Moneda",
        trip.currency,
        styles,
    )
    add_key_value_line(
        story,
        "Estado",
        enum_value(trip.status),
        styles,
    )
    add_key_value_line(
        story,
        "Valoración",
        (
            f"{trip.rating}/5"
            if trip.rating is not None
            else "Sin valoración"
        ),
        styles,
    )

    story.append(
        Paragraph(
            "<b>Descripción:</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            safe_multiline_text(
                trip.description
            ),
            styles["normal"],
        )
    )


def add_destinations(
    story: list[object],
    trip: Trip,
    styles: dict[str, ParagraphStyle],
) -> None:
    add_section_header(
        story=story,
        title="Destinos",
        styles=styles,
        line_color=SECONDARY_COLOR,
    )

    if not trip.destinations:
        story.append(
            Paragraph(
                "No hay destinos registrados.",
                styles["muted"],
            )
        )
        return

    for destination in sorted(
        trip.destinations,
        key=lambda item: item.order,
    ):
        story.append(
            Paragraph(
                (
                    f"Destino {destination.order} · "
                    f"{safe_text(destination.city)}, "
                    f"{safe_text(destination.country)}"
                ),
                styles["item_title_blue"],
            )
        )

        add_key_value_line(
            story,
            "Moneda",
            destination.currency,
            styles,
        )

        add_block_separator(
            story,
            color=LIGHT_BLUE,
        )


def add_transports(
    story: list[object],
    trip: Trip,
    styles: dict[str, ParagraphStyle],
) -> None:
    add_section_header(
        story=story,
        title="Transportes",
        styles=styles,
        line_color=WARNING_COLOR,
    )

    if not trip.transports:
        story.append(
            Paragraph(
                "No hay transportes registrados.",
                styles["muted"],
            )
        )
        return

    ordered_transports = sorted(
        trip.transports,
        key=lambda item: (
            item.departure_date,
            item.departure_time or time.min,
            item.id,
        ),
    )

    for transport in ordered_transports:
        story.append(
            Paragraph(
                (
                    f"{enum_value(transport.transport_type)} · "
                    f"{safe_text(transport.origin)} → "
                    f"{safe_text(transport.destination)}"
                ),
                styles["item_title_orange"],
            )
        )

        add_key_value_line(
            story,
            "Salida",
            (
                f"{format_date(transport.departure_date)} "
                f"{format_time(transport.departure_time)}"
            ),
            styles,
        )
        add_key_value_line(
            story,
            "Llegada",
            (
                f"{format_date(transport.arrival_date)} "
                f"{format_time(transport.arrival_time)}"
            ),
            styles,
        )
        add_key_value_line(
            story,
            "Check-in",
            format_date(
                transport.check_in_date
            ),
            styles,
        )
        add_key_value_line(
            story,
            "Precio",
            format_money(
                transport.price,
                trip.currency,
            ),
            styles,
        )

        add_block_separator(
            story,
            color=LIGHT_ORANGE,
        )


def add_accommodations(
    story: list[object],
    trip: Trip,
    styles: dict[str, ParagraphStyle],
) -> None:
    add_section_header(
        story=story,
        title="Alojamientos",
        styles=styles,
        line_color=ACCENT_COLOR,
    )

    if not trip.accommodations:
        story.append(
            Paragraph(
                "No hay alojamientos registrados.",
                styles["muted"],
            )
        )
        return

    ordered_accommodations = sorted(
        trip.accommodations,
        key=lambda item: (
            item.check_in_date,
            item.check_in_time or time.min,
            item.id,
        ),
    )

    for accommodation in ordered_accommodations:
        story.append(
            Paragraph(
                safe_text(accommodation.name),
                styles["item_title_green"],
            )
        )

        add_key_value_line(
            story,
            "Dirección",
            accommodation.address,
            styles,
        )
        add_key_value_line(
            story,
            "Entrada",
            (
                f"{format_date(accommodation.check_in_date)} "
                f"{format_time(accommodation.check_in_time)}"
            ),
            styles,
        )
        add_key_value_line(
            story,
            "Salida",
            (
                f"{format_date(accommodation.check_out_date)} "
                f"{format_time(accommodation.check_out_time)}"
            ),
            styles,
        )
        add_key_value_line(
            story,
            "Precio",
            format_money(
                accommodation.price,
                trip.currency,
            ),
            styles,
        )

        add_block_separator(
            story,
            color=LIGHT_GREEN,
        )


def add_participants(
    story: list[object],
    trip: Trip,
    styles: dict[str, ParagraphStyle],
) -> None:
    add_section_header(
        story=story,
        title="Participantes",
        styles=styles,
        line_color=PRIMARY_COLOR,
    )

    if not trip.participants:
        story.append(
            Paragraph(
                "No hay participantes registrados.",
                styles["muted"],
            )
        )
        return

    for participant in sorted(
        trip.participants,
        key=lambda item: item.name.lower(),
    ):
        story.append(
            Paragraph(
                f"• {safe_text(participant.name)}",
                styles["normal"],
            )
        )


def add_expenses(
    story: list[object],
    trip: Trip,
    styles: dict[str, ParagraphStyle],
) -> None:
    add_section_header(
        story=story,
        title="Gastos",
        styles=styles,
        line_color=SECONDARY_COLOR,
    )

    if not trip.expenses:
        story.append(
            Paragraph(
                "No hay gastos registrados.",
                styles["muted"],
            )
        )
        return

    participant_names = {
        participant.id: participant.name
        for participant in trip.participants
    }

    totals_by_currency: dict[str, Decimal] = defaultdict(
        lambda: Decimal("0")
    )

    ordered_expenses = sorted(
        trip.expenses,
        key=lambda item: (
            item.expense_date,
            item.id,
        ),
    )

    for expense in ordered_expenses:
        totals_by_currency[expense.currency] += expense.amount

        story.append(
            Paragraph(
                safe_text(expense.name),
                styles["item_title_blue"],
            )
        )

        add_key_value_line(
            story,
            "Categoría",
            enum_value(expense.category),
            styles,
        )
        add_key_value_line(
            story,
            "Participante",
            participant_names.get(
                expense.participant_id,
                "-",
            ),
            styles,
        )
        add_key_value_line(
            story,
            "Fecha",
            format_date(
                expense.expense_date
            ),
            styles,
        )
        add_key_value_line(
            story,
            "Importe",
            format_money(
                expense.amount,
                expense.currency,
            ),
            styles,
        )

        add_block_separator(
            story,
            color=LIGHT_BLUE,
        )

    totals = ", ".join(
        f"{amount:.2f} {currency}"
        for currency, amount in sorted(
            totals_by_currency.items()
        )
    )

    story.append(
        Paragraph(
            f"<b>Total de gastos:</b> {escape(totals)}",
            styles["normal"],
        )
    )


def add_notes(
    story: list[object],
    trip: Trip,
    styles: dict[str, ParagraphStyle],
) -> None:
    add_section_header(
        story=story,
        title="Notas",
        styles=styles,
        line_color=ACCENT_COLOR,
    )

    if not trip.notes:
        story.append(
            Paragraph(
                "No hay notas registradas.",
                styles["muted"],
            )
        )
        return

    ordered_notes = sorted(
        trip.notes,
        key=lambda item: (
            item.day_number is None,
            item.day_number or 0,
            item.id,
        ),
    )

    for note in ordered_notes:
        title = safe_text(note.title)

        if note.day_number is not None:
            title = (
                f"{title} · Día {note.day_number}"
            )

        story.append(
            Paragraph(
                title,
                styles["item_title_green"],
            )
        )

        story.append(
            Paragraph(
                safe_multiline_text(note.text),
                styles["normal"],
            )
        )

        add_block_separator(
            story,
            color=LIGHT_GREEN,
        )


def add_timeline_visual(
    story: list[object],
    timeline: TimelineResponse,
    styles: dict[str, ParagraphStyle],
) -> None:
    add_section_header(
        story=story,
        title="Línea temporal",
        styles=styles,
        line_color=PRIMARY_COLOR,
    )

    story.append(
        Paragraph(
            "Resumen visual del viaje dividido por días.",
            styles["muted"],
        )
    )

    story.append(
        Spacer(
            1,
            0.2 * cm,
        )
    )

    days_per_page = 28

    day_chunks = [
        timeline.days[index:index + days_per_page]
        for index in range(
            0,
            len(timeline.days),
            days_per_page,
        )
    ]

    for index, chunk in enumerate(day_chunks):
        if index > 0:
            story.append(PageBreak())

            story.append(
                Paragraph(
                    "Línea temporal (continuación)",
                    styles["section"],
                )
            )

            story.append(
                HRFlowable(
                    width="100%",
                    thickness=1.0,
                    color=PRIMARY_COLOR,
                    spaceBefore=0,
                    spaceAfter=10,
                )
            )

        story.append(
            SegmentedTimelineFlowable(
                days=chunk,
                days_per_row=7,
            )
        )

    story.append(
        Spacer(
            1,
            0.4 * cm,
        )
    )


def add_timeline_details(
    story: list[object],
    timeline: TimelineResponse,
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(
        Paragraph(
            "Detalle por día",
            styles["section"],
        )
    )
    story.append(
        HRFlowable(
            width="100%",
            thickness=1.0,
            color=SECONDARY_COLOR,
            spaceBefore=0,
            spaceAfter=10,
        )
    )

    for day in timeline.days:
        story.append(
            Paragraph(
                (
                    f"Día {day.day_number} · "
                    f"{format_date(day.date)}"
                ),
                styles["timeline_day"],
            )
        )

        if not day.activities:
            story.append(
                Paragraph(
                    "• Sin actividades registradas.",
                    styles["muted"],
                )
            )
            story.append(
                Spacer(
                    1,
                    0.15 * cm,
                )
            )
            continue

        ordered_activities = sorted(
            day.activities,
            key=lambda item: (
                item.order,
                item.id,
            ),
        )

        for activity in ordered_activities:
            story.append(
                Paragraph(
                    (
                        f"• <b>{escape(format_time(activity.start_time))}</b> "
                        f"{safe_text(activity.name)}"
                    ),
                    styles["normal"],
                )
            )

            story.append(
                Paragraph(
                    (
                        f"<b>Ubicación:</b> "
                        f"{safe_text(activity.location)}"
                    ),
                    styles["small"],
                )
            )

            story.append(
                Paragraph(
                    (
                        "<b>Estado:</b> "
                        + (
                            "Completada"
                            if activity.completed
                            else "Pendiente"
                        )
                    ),
                    styles["small"],
                )
            )

            story.append(
                Spacer(
                    1,
                    0.12 * cm,
                )
            )

        add_block_separator(
            story,
            color=LIGHT_BLUE,
        )


def generate_trip_pdf(
    trip: Trip,
    timeline: TimelineResponse,
    output_path: Path,
) -> None:
    """
    Genera el PDF resumen del viaje.
    """

    styles = create_pdf_styles()

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"Resumen del viaje {trip.name}",
        author="TripPlanner",
    )

    story: list[object] = [
        Paragraph(
            safe_text(trip.name),
            styles["title"],
        ),
        Paragraph(
            (
                f"{format_date(trip.start_date)}"
                f" - {format_date(trip.end_date)}"
            ),
            styles["subtitle"],
        ),
        HRFlowable(
            width="70%",
            thickness=2,
            color=SECONDARY_COLOR,
            spaceBefore=0,
            spaceAfter=12,
            hAlign="CENTER",
        ),
    ]

    add_general_information(
        story=story,
        trip=trip,
        styles=styles,
    )

    add_destinations(
        story=story,
        trip=trip,
        styles=styles,
    )

    add_transports(
        story=story,
        trip=trip,
        styles=styles,
    )

    add_accommodations(
        story=story,
        trip=trip,
        styles=styles,
    )

    add_participants(
        story=story,
        trip=trip,
        styles=styles,
    )

    add_expenses(
        story=story,
        trip=trip,
        styles=styles,
    )

    add_notes(
        story=story,
        trip=trip,
        styles=styles,
    )

    story.append(
        PageBreak()
    )

    add_timeline_visual(
        story=story,
        timeline=timeline,
        styles=styles,
    )

    add_timeline_details(
        story=story,
        timeline=timeline,
        styles=styles,
    )

    document.build(story)