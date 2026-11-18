"""Pruebas unitarias para el gestor de colas de Banco Meridional."""

from datetime import datetime

import pytest

from queue_manager import VALID_SERVICES, BranchQueueManager


def test_global_sequential_ticket_numbering_across_services() -> None:
    manager = BranchQueueManager()

    t1 = manager.issue_ticket("Ana", "deposito")
    t2 = manager.issue_ticket("Luis", "retiro")
    t3 = manager.issue_ticket("Marta", "gestion_cuenta")
    t4 = manager.issue_ticket("Carlos", "deposito")

    assert [t1.number, t2.number, t3.number, t4.number] == [1, 2, 3, 4]
    assert t1.client_name == "Ana"
    assert t1.service_type == "deposito"
    assert isinstance(t1.arrival_time, datetime)


def test_independent_service_queues_no_head_of_line_blocking() -> None:
    """Un agente de depósitos llama a su cliente aunque hayan llegado retiros antes."""
    manager = BranchQueueManager()

    manager.issue_ticket("Retiro 1", "retiro")
    manager.issue_ticket("Retiro 2", "retiro")
    t_dep = manager.issue_ticket("Depósito 1", "deposito")

    called = manager.call_next("deposito")
    assert called == t_dep
    assert manager.get_stats()["retiro"] == 2
    assert manager.get_stats()["deposito"] == 0


def test_fifo_order_within_each_service() -> None:
    manager = BranchQueueManager()

    t1 = manager.issue_ticket("Primero", "gestion_cuenta")
    t2 = manager.issue_ticket("Segundo", "gestion_cuenta")
    t3 = manager.issue_ticket("Tercero", "gestion_cuenta")

    assert manager.call_next("gestion_cuenta") == t1
    assert manager.call_next("gestion_cuenta") == t2
    assert manager.call_next("gestion_cuenta") == t3
    assert manager.call_next("gestion_cuenta") is None


def test_peek_next_does_not_remove_ticket() -> None:
    manager = BranchQueueManager()
    assert manager.peek_next("retiro") is None

    t1 = manager.issue_ticket("Elena", "retiro")
    manager.issue_ticket("Jorge", "retiro")

    assert manager.peek_next("retiro") == t1
    assert manager.get_stats()["retiro"] == 2
    assert manager.call_next("retiro") == t1


def test_list_waiting_grouped_by_service_in_fifo_order() -> None:
    manager = BranchQueueManager()
    d1 = manager.issue_ticket("D1", "deposito")
    r1 = manager.issue_ticket("R1", "retiro")
    d2 = manager.issue_ticket("D2", "deposito")

    waiting = manager.list_waiting()
    assert list(waiting.keys()) == list(VALID_SERVICES)
    assert waiting["deposito"] == [d1, d2]
    assert waiting["retiro"] == [r1]
    assert waiting["gestion_cuenta"] == []


def test_get_stats_counts_per_service_and_total() -> None:
    manager = BranchQueueManager()
    assert manager.get_stats() == {
        "deposito": 0,
        "retiro": 0,
        "gestion_cuenta": 0,
        "total": 0,
    }

    manager.issue_ticket("A", "deposito")
    manager.issue_ticket("B", "retiro")
    manager.issue_ticket("C", "retiro")
    manager.issue_ticket("D", "gestion_cuenta")

    assert manager.get_stats() == {
        "deposito": 1,
        "retiro": 2,
        "gestion_cuenta": 1,
        "total": 4,
    }

    manager.call_next("retiro")
    assert manager.get_stats()["retiro"] == 1
    assert manager.get_stats()["total"] == 3


def test_validation_errors_for_invalid_service_or_empty_name() -> None:
    manager = BranchQueueManager()

    with pytest.raises(ValueError):
        manager.issue_ticket("   ", "deposito")

    with pytest.raises(ValueError):
        manager.issue_ticket("Ana", "prestamos")

    with pytest.raises(ValueError):
        manager.call_next("prestamos")

    with pytest.raises(ValueError):
        manager.peek_next("prestamos")
