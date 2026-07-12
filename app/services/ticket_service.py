import time
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Ticket, Queue
from app.schemas import TicketBulkEntry, TicketCreate, TicketCreateStandalone

# remived validation here as it is done in add_ticket_to_queue as check is like below 10 caoacity exceeded

def create_ticket(db: Session, data: TicketCreateStandalone) -> Ticket:
    if data.queue_id:
        queue = db.query(Queue).filter(Queue.id == data.queue_id).first()

        if not queue:
            raise ValueError("queue_not_found")

        # Total quantity after adding this ticket
        total_tickets = queue.current_ticket_count + data.quantity

        # Do not allow exceeding queue capacity
        if total_tickets > queue.capacity:
            raise ValueError("capacity_exceeded")

        ticket = Ticket(
            title=data.title,
            complexity=data.complexity,
            queue_id=data.queue_id,
            quantity=data.quantity,
        )

        db.add(ticket)

        # Update queue ticket count
        queue.current_ticket_count += data.quantity

    else:
        ticket = Ticket(
            title=data.title,
            complexity=data.complexity,
            queue_id=None,
            quantity=data.quantity,
        )

        db.add(ticket)

    db.commit()
    db.refresh(ticket)

    return ticket


def add_ticket_to_queue(db: Session, queue_id: str, data: TicketCreate) -> Ticket:

    queue = db.query(Queue).filter(Queue.id == queue_id).first()

    if not queue:
        raise ValueError("queue_not_found")

    total_tickets = queue.current_ticket_count + data.quantity

    # Queue capacity validation
    if total_tickets > queue.capacity:
        raise ValueError("capacity_exceeded")

    ticket = Ticket(
        title=data.title,
        complexity=data.complexity,
        queue_id=queue_id,
        quantity=data.quantity,
    )

    db.add(ticket)

    # Increase ticket count
    queue.current_ticket_count += data.quantity

    db.commit()
    db.refresh(ticket)

    return ticket

def bulk_add_tickets(db: Session, queue_id: str, entries: list[TicketBulkEntry]) -> int:

    queue = db.query(Queue).filter(Queue.id == queue_id).first()

    if not queue:
        raise ValueError("queue_not_found")

    added = 0

    total_quantity = sum(e.quantity for e in entries if e.quantity > 0)

    # Check capacity BEFORE inserting anything
    if queue.current_ticket_count + total_quantity > queue.capacity:
        raise ValueError("capacity_exceeded")

    for e in entries:

        if e.quantity <= 0:
            continue

        ticket = Ticket(
            title=e.title,
            complexity=e.complexity,
            queue_id=queue_id,
            quantity=e.quantity,
        )

        db.add(ticket)

        queue.current_ticket_count += e.quantity

        added += 1

    # Commit everything once
    db.commit()

    return added


def list_tickets_by_queue(db: Session, queue_id: str) -> list[Ticket]:
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise ValueError("queue_not_found")
    return list(queue.tickets)


def get_ticket_by_id(db: Session, ticket_id: str) -> Ticket | None:
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()


def update_ticket_complexity(db: Session, ticket_id: str, complexity: int) -> None:
    ticket = get_ticket_by_id(db, ticket_id)
    if not ticket:
        raise ValueError("ticket_not_found")
    prev_updated = ticket.updated_at
    ticket.complexity = complexity
    ticket.updated_at = prev_updated
    db.commit()


def remove_ticket_quantity(
    db: Session, queue_id: str, ticket_id: str, quantity: int | None
) -> None:
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise ValueError("queue_not_found")
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.queue_id == queue_id).first()
    if not ticket:
        raise ValueError("ticket_not_found")
    if quantity is not None:
        to_remove = min(quantity, ticket.quantity)
        ticket.quantity -= to_remove
        queue.current_ticket_count -= to_remove
        if ticket.quantity <= 0:
            db.delete(ticket)
    else:
        queue.current_ticket_count -= ticket.quantity
        db.delete(ticket)
    db.commit()


def bulk_remove_tickets(
    db: Session, queue_id: str, ticket_ids: list[str] | None
) -> None:
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise ValueError("queue_not_found")
    if ticket_ids is not None and len(ticket_ids) > 0:
        tickets = db.query(Ticket).filter(
            Ticket.queue_id == queue_id,
            Ticket.id.in_(ticket_ids),
        ).all()
        for ticket in tickets:
            queue.current_ticket_count -= ticket.quantity
            db.delete(ticket)
    else:
        for ticket in list(queue.tickets):
            queue.current_ticket_count -= ticket.quantity
            db.delete(ticket)
    db.commit()
