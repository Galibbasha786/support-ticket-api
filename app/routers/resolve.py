from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    InsufficientEffortError,
    OutOfStockError,
    ResolveRequest,
    ResolveResponse,
    OvertimeBreakdownResponse,
)
from app.services import resolve_service

router = APIRouter()


@router.post("/resolve", response_model=ResolveResponse)
def resolve_ticket(data: ResolveRequest, db: Session = Depends(get_db)):
    try:
        result = resolve_service.resolve(db, data.ticket_id, data.effort_logged)
        return ResolveResponse(**result)

    except ValueError as e:

        # e.args[0] always contains the actual error code/message.
        # Using e.args[0] is safer and more consistent than str(e),
        # especially when the exception contains multiple arguments.

        if e.args[0] == "ticket_not_found":
            raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )

        if e.args[0] == "out_of_stock":
            raise HTTPException(
                status_code=400,
                detail=OutOfStockError().model_dump(),
            )

        # ========================= BUG =========================
        # The service raises:
        #
        # raise ValueError(
        #     "insufficient_effort",
        #     required_effort,
        #     logged_effort
        # )
        #
        # This creates:
        #
        # e.args =
        # (
        #   "insufficient_effort",
        #   required_effort,
        #   logged_effort
        # )
        #
        # Earlier the router checked:
        #
        # if str(e) == "insufficient_effort"
        #
        # But str(e) becomes:
        #
        # "('insufficient_effort', required, logged)"
        #
        # which never equals
        #
        # "insufficient_effort"
        #
        # Therefore the condition never executed,
        # and the exception reached the final "raise",
        # resulting in a 500 Internal Server Error.
        #
        # ========================= FIX =========================
        # Instead of comparing str(e),
        # compare e.args[0], which always contains
        # the actual error identifier.
        # This correctly matches the exception and
        # allows us to access the additional values
        # (required effort and logged effort)
        # stored in e.args[1] and e.args[2].
        # ======================================================

        if e.args[0] == "insufficient_effort":
            required = e.args[1]
            logged = e.args[2]

            raise HTTPException(
                status_code=400,
                detail=InsufficientEffortError(
                    required=required,
                    logged=logged,
                ).model_dump(),
            )

        raise


@router.get("/resolve/overtime-breakdown", response_model=OvertimeBreakdownResponse)
def overtime_breakdown(overtime: int = Query(..., ge=0)):
    try:
        result = resolve_service.overtime_breakdown(overtime)
        return OvertimeBreakdownResponse(**result)

    except ValueError as e:

        if e.args[0] == "invalid_overtime":
            raise HTTPException(
                status_code=400,
                detail="Minimum overtime must be at least 5 units."
            )

        raise