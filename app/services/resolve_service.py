import time
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Ticket

EFFORT_BLOCKS = sorted(
    settings.STANDARD_EFFORT_BLOCKS,
    reverse=True
)
def resolve(db: Session, ticket_id: str, effort_logged: int) -> dict:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise ValueError("ticket_not_found")
    time.sleep(0.05)  # demo: widens race window for concurrent resolve/add
    if ticket.quantity <= 0:
        raise ValueError("out_of_stock")
    if effort_logged < ticket.complexity:
        raise ValueError("insufficient_effort", ticket.complexity, effort_logged)
    # No validation that effort_logged or overtime use STANDARD_EFFORT_BLOCKS
    overtime = effort_logged - ticket.complexity
    ticket.quantity -= 1
    ticket.queue.current_ticket_count -= 1
    db.commit()
    db.refresh(ticket)
    return {
        "ticket": ticket.title,
        "complexity": ticket.complexity,
        "effort_logged": effort_logged,
        "overtime_returned": overtime,
        "remaining_quantity": ticket.quantity,
        "message": "Ticket resolved successfully",
    }


def overtime_breakdown(overtime: int) -> dict:
    # BUG FIX:
    # The smallest available effort block is 5.
    # Therefore overtime values less than 5 cannot be represented.
    # Instead of returning an empty breakdown,
    # raise an error indicating invalid overtime.
    # or we can add 1 in the STANDARD_EFFORT_BLOCKS to allow overtime of 1,2,3,4 but that is not a good idea as it will break the logic of the system. So we will raise an error instead.
    if overtime < min(EFFORT_BLOCKS):
        raise ValueError("invalid_overtime")

    #blocks = sorted(settings.STANDARD_EFFORT_BLOCKS, reverse=True) --> as sorting for every request it takes O(n)*O(n log n) time complexity removing this replacing out removes the repeated sorting
    result= {}
    remaining = overtime
    for block in EFFORT_BLOCKS:
        if remaining <= 0:
            break
        count = remaining // block
        if count > 0:
            result[str(block)] = count
            remaining -= count * block
    return {"overtime": overtime, "blocks": result}
