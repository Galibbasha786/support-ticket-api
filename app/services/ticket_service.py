#import time  -- not being used
from sqlalchemy.orm import Session

#from app.config import settings.  --- its not  being used
from app.models import Ticket, Queue
from app.schemas import TicketBulkEntry, TicketCreate, TicketCreateStandalone

# remived validation here as it is done in add_ticket_to_queue as check is like below 10 caoacity exceeded

def create_ticket(db: Session, data: TicketCreateStandalone) -> Ticket:

    # If queue_id is provided, attach the ticket to that queue
    if data.queue_id:

        # OPTIMIZATION:
        # db.get() is faster and cleaner than query().filter().first()
        # when fetching by Primary Key.
        queue = db.get(Queue, data.queue_id)

        if not queue:
            raise ValueError("queue_not_found")

        # Calculate future ticket count once
        total_tickets = queue.current_ticket_count + data.quantity

        # Business Rule:
        # Do not allow queue capacity to be exceeded.
        if total_tickets > queue.capacity:
            raise ValueError("capacity_exceeded")

        ticket = Ticket(
            title=data.title,
            complexity=data.complexity,
            quantity=data.quantity,
            queue_id=data.queue_id,
        )

        db.add(ticket)

        # Keep queue statistics synchronized
        queue.current_ticket_count += data.quantity

    else:
        # Standalone ticket (not attached to any queue)
        ticket = Ticket(
            title=data.title,
            complexity=data.complexity,
            quantity=data.quantity,
            queue_id=None,
        )

        db.add(ticket)

    # OPTIMIZATION:
    # Rollback keeps SQLAlchemy session usable
    # if commit fails.
    try:
        db.commit()
        db.refresh(ticket)
    except Exception:
        db.rollback()
        raise
  

    return ticket



def add_ticket_to_queue(
    db: Session,
    queue_id: str,
    data: TicketCreate,
) -> Ticket:

    # Faster primary key lookup
    queue = db.get(Queue, queue_id)

    if not queue:
        raise ValueError("queue_not_found")

    total_tickets = queue.current_ticket_count + data.quantity

    # Capacity Validation
    if total_tickets > queue.capacity:
        raise ValueError("capacity_exceeded")

    ticket = Ticket(
        title=data.title,
        complexity=data.complexity,
        quantity=data.quantity,
        queue_id=queue_id,
    )

    db.add(ticket)

    # Update queue statistics
    queue.current_ticket_count += data.quantity

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(ticket)

    return ticket

def bulk_add_tickets(
    db: Session,
    queue_id: str,
    entries: list[TicketBulkEntry],
) -> int:

    queue = db.get(Queue, queue_id)

    if not queue:
        raise ValueError("queue_not_found")

    # Calculate total quantity once
    total_quantity = sum(
        entry.quantity
        for entry in entries
        if entry.quantity > 0
    )

    # Validate before inserting anything
    if queue.current_ticket_count + total_quantity > queue.capacity:
        raise ValueError("capacity_exceeded")

    added = 0

    # OPTIMIZATION:
    # Store all Ticket objects first,
    # then add them together.
    tickets: list[Ticket] = []

    for entry in entries:

        if entry.quantity <= 0:
            continue

        ticket = Ticket(
            title=entry.title,
            complexity=entry.complexity,
            quantity=entry.quantity,
            queue_id=queue_id,
        )

        tickets.append(ticket)

        queue.current_ticket_count += entry.quantity

        added += 1

    # More efficient than multiple db.add()
    db.add_all(tickets)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

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
