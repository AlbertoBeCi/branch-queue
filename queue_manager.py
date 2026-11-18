"""Gestor de colas por tipo de servicio para Banco Meridional."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

VALID_SERVICES: tuple[str, ...] = ("deposito", "retiro", "gestion_cuenta")

SERVICE_LABELS: dict[str, str] = {
    "deposito": "Depósitos",
    "retiro": "Retiros",
    "gestion_cuenta": "Gestión de cuenta",
}


@dataclass(frozen=True)
class Ticket:
    """Representa un ticket emitido para un cliente en la sucursal."""

    number: int
    client_name: str
    service_type: str
    arrival_time: datetime = field(default_factory=datetime.now)


class BranchQueueManager:
    """Gestiona colas FIFO independientes por tipo de servicio en tiempo O(1)."""

    def __init__(self) -> None:
        self._queues: dict[str, deque[Ticket]] = {
            service: deque() for service in VALID_SERVICES
        }
        self._next_ticket_number: int = 1

    @staticmethod
    def _validate_service(service_type: str) -> str:
        if service_type not in VALID_SERVICES:
            valid = ", ".join(VALID_SERVICES)
            raise ValueError(
                f"Tipo de servicio inválido: {service_type!r}. Opciones válidas: {valid}."
            )
        return service_type

    def issue_ticket(self, client_name: str, service_type: str) -> Ticket:
        """Emite un ticket con numeración global secuencial y lo encola en su servicio."""
        cleaned_name = client_name.strip()
        if not cleaned_name:
            raise ValueError("El nombre del cliente no puede estar vacío.")
        service = self._validate_service(service_type)

        ticket = Ticket(
            number=self._next_ticket_number,
            client_name=cleaned_name,
            service_type=service,
        )
        self._next_ticket_number += 1
        self._queues[service].append(ticket)
        return ticket

    def call_next(self, service_type: str) -> Ticket | None:
        """Desencola y devuelve el siguiente cliente para el tipo de servicio dado."""
        service = self._validate_service(service_type)
        queue = self._queues[service]
        if not queue:
            return None
        return queue.popleft()

    def peek_next(self, service_type: str) -> Ticket | None:
        """Devuelve el siguiente cliente en espera para el servicio sin retirarlo."""
        service = self._validate_service(service_type)
        queue = self._queues[service]
        if not queue:
            return None
        return queue[0]

    def list_waiting(self) -> dict[str, list[Ticket]]:
        """Devuelve todos los clientes en espera agrupados por servicio en orden FIFO."""
        return {service: list(self._queues[service]) for service in VALID_SERVICES}

    def get_stats(self) -> dict[str, int]:
        """Reporta el número de clientes en espera por tipo de servicio y el total."""
        stats = {service: len(self._queues[service]) for service in VALID_SERVICES}
        stats["total"] = sum(stats.values())
        return stats
