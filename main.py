"""Interfaz de terminal para el gestor de colas de Banco Meridional."""

from __future__ import annotations

import argparse
from collections.abc import Callable

from queue_manager import SERVICE_LABELS, VALID_SERVICES, BranchQueueManager, Ticket


def format_ticket(ticket: Ticket) -> str:
    """Formatea un ticket para mostrarlo en terminal."""
    label = SERVICE_LABELS[ticket.service_type]
    timestamp = ticket.arrival_time.strftime("%H:%M:%S")
    return f"#{ticket.number:03d} | {ticket.client_name} | {label} ({ticket.service_type}) | {timestamp}"


def prompt_service(input_fn: Callable[[str], str] = input) -> str | None:
    """Solicita al usuario seleccionar un tipo de servicio."""
    print("\nSeleccione tipo de servicio:")
    for idx, service in enumerate(VALID_SERVICES, start=1):
        print(f"  {idx}. {SERVICE_LABELS[service]} ({service})")

    raw = input_fn("Servicio (1-3 o nombre): ").strip().lower()
    if raw in VALID_SERVICES:
        return raw
    if raw in {"1", "2", "3"}:
        return VALID_SERVICES[int(raw) - 1]
    print("Opción de servicio no válida.")
    return None


def print_waiting_list(manager: BranchQueueManager) -> None:
    """Muestra todos los clientes en espera agrupados por tipo de servicio."""
    grouped = manager.list_waiting()
    print("\n--- Clientes en espera ---")
    for service in VALID_SERVICES:
        tickets = grouped[service]
        label = SERVICE_LABELS[service]
        print(f"\n[{label}] ({len(tickets)} en espera):")
        if not tickets:
            print("  (sin clientes en espera)")
        else:
            for pos, ticket in enumerate(tickets, start=1):
                print(f"  {pos}. {format_ticket(ticket)}")


def print_stats(manager: BranchQueueManager) -> None:
    """Muestra las estadísticas globales de espera."""
    stats = manager.get_stats()
    print("\n--- Estadísticas globales ---")
    for service in VALID_SERVICES:
        print(f"  {SERVICE_LABELS[service]:<20}: {stats[service]}")
    print(f"  {'TOTAL EN ESPERA':<20}: {stats['total']}")


def load_demo_scenario(manager: BranchQueueManager) -> None:
    """Carga un escenario de demostración con clientes en los tres servicios."""
    demo_clients = [
        ("Ana Gómez", "retiro"),
        ("Luis Pérez", "retiro"),
        ("Marta Ruiz", "deposito"),
        ("Carlos Vega", "gestion_cuenta"),
        ("Elena Soto", "deposito"),
    ]
    print("\nCargando escenario de demostración...")
    for name, service in demo_clients:
        ticket = manager.issue_ticket(name, service)
        print(f"  Emitido: {format_ticket(ticket)}")


def run_demo() -> None:
    """Ejecuta una simulación no interactiva de todas las operaciones del sistema."""
    manager = BranchQueueManager()
    print("=== Simulación Banco Meridional ===")
    load_demo_scenario(manager)
    print_waiting_list(manager)
    print_stats(manager)

    print("\n[Peek] Siguiente en Depósitos:")
    next_dep = manager.peek_next("deposito")
    print(" ", format_ticket(next_dep) if next_dep else "(ninguno)")

    print("\n[Agente Depósitos] Llama al siguiente (ignora retiros previos):")
    called_dep = manager.call_next("deposito")
    print("  Atendiendo a:", format_ticket(called_dep) if called_dep else "(ninguno)")

    print("\n[Agente Retiros] Llama al siguiente:")
    called_ret = manager.call_next("retiro")
    print("  Atendiendo a:", format_ticket(called_ret) if called_ret else "(ninguno)")

    print_waiting_list(manager)
    print_stats(manager)


def run_interactive() -> None:
    """Ejecuta el menú interactivo en terminal."""
    manager = BranchQueueManager()
    print("=== Gestor de Colas — Banco Meridional ===")

    while True:
        print("\nMenú principal:")
        print("  1. Emitir ticket")
        print("  2. Llamar al siguiente cliente (Agente)")
        print("  3. Ver siguiente en espera (Peek)")
        print("  4. Listar clientes en espera")
        print("  5. Ver estadísticas globales")
        print("  6. Cargar escenario de demostración")
        print("  7. Salir")

        option = input("Seleccione una opción (1-7): ").strip()

        if option == "1":
            name = input("Nombre del cliente: ")
            service = prompt_service()
            if service is None:
                continue
            try:
                ticket = manager.issue_ticket(name, service)
                print(f"Ticket emitido: {format_ticket(ticket)}")
            except ValueError as exc:
                print(f"Error: {exc}")

        elif option == "2":
            service = prompt_service()
            if service is None:
                continue
            ticket = manager.call_next(service)
            if ticket is None:
                print(f"No hay clientes esperando en {SERVICE_LABELS[service]}.")
            else:
                print(f"Llamando a: {format_ticket(ticket)}")

        elif option == "3":
            service = prompt_service()
            if service is None:
                continue
            ticket = manager.peek_next(service)
            if ticket is None:
                print(f"No hay clientes esperando en {SERVICE_LABELS[service]}.")
            else:
                print(f"Siguiente en {SERVICE_LABELS[service]}: {format_ticket(ticket)}")

        elif option == "4":
            print_waiting_list(manager)

        elif option == "5":
            print_stats(manager)

        elif option == "6":
            load_demo_scenario(manager)

        elif option == "7":
            print("Cerrando gestor de colas. ¡Hasta luego!")
            break

        else:
            print("Opción no válida. Elija un número del 1 al 7.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gestor de colas en terminal para Banco Meridional."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ejecuta una simulación automática de las operaciones en terminal.",
    )
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
