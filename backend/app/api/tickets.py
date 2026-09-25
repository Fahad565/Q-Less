from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Ticket, TicketStatus
from app.schemas import TicketCreate, TicketResponse, AssignCounterRequest
from app.services.queue_service import QueueService

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

@router.post("", response_model=TicketResponse)
@router.post("/", response_model=TicketResponse)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    try:
        ticket = QueueService.create_ticket(
            db=db,
            customer_phone=ticket_data.customer_phone,
            service_id=ticket_data.service_id
        )
        pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_phone": ticket.customer_phone,
            "queue_id": ticket.queue_id,
            "service_id": ticket.service_id,
            "counter_id": ticket.counter_id,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "called_at": ticket.called_at,
            "completed_at": ticket.completed_at,
            "position": pos,
            "estimated_wait_minutes": est_wait,
            "service_name": ticket.service.name if ticket.service else None,
            "counter_name": ticket.counter.name if ticket.counter else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
    return {
        "id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "customer_phone": ticket.customer_phone,
        "queue_id": ticket.queue_id,
        "service_id": ticket.service_id,
        "counter_id": ticket.counter_id,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "called_at": ticket.called_at,
        "completed_at": ticket.completed_at,
        "position": pos,
        "estimated_wait_minutes": est_wait,
        "service_name": ticket.service.name if ticket.service else None,
        "counter_name": ticket.counter.name if ticket.counter else None
    }

@router.get("/{ticket_id}/position")
def get_ticket_position(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
    return {
        "ticket_id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "status": ticket.status,
        "position": pos,
        "estimated_wait_minutes": est_wait
    }

@router.post("/{ticket_id}/recall", response_model=TicketResponse)
def recall_ticket(ticket_id: int, db: Session = Depends(get_db)):
    try:
        ticket = QueueService.update_status(db, ticket_id, TicketStatus.CALLED)
        pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_phone": ticket.customer_phone,
            "queue_id": ticket.queue_id,
            "service_id": ticket.service_id,
            "counter_id": ticket.counter_id,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "called_at": ticket.called_at,
            "completed_at": ticket.completed_at,
            "position": pos,
            "estimated_wait_minutes": est_wait,
            "service_name": ticket.service.name if ticket.service else None,
            "counter_name": ticket.counter.name if ticket.counter else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{ticket_id}/skip", response_model=TicketResponse)
def skip_ticket(ticket_id: int, db: Session = Depends(get_db)):
    try:
        ticket = QueueService.update_status(db, ticket_id, TicketStatus.SKIPPED)
        pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_phone": ticket.customer_phone,
            "queue_id": ticket.queue_id,
            "service_id": ticket.service_id,
            "counter_id": ticket.counter_id,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "called_at": ticket.called_at,
            "completed_at": ticket.completed_at,
            "position": pos,
            "estimated_wait_minutes": est_wait,
            "service_name": ticket.service.name if ticket.service else None,
            "counter_name": ticket.counter.name if ticket.counter else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{ticket_id}/complete", response_model=TicketResponse)
def complete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    try:
        ticket = QueueService.update_status(db, ticket_id, TicketStatus.COMPLETED)
        pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_phone": ticket.customer_phone,
            "queue_id": ticket.queue_id,
            "service_id": ticket.service_id,
            "counter_id": ticket.counter_id,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "called_at": ticket.called_at,
            "completed_at": ticket.completed_at,
            "position": pos,
            "estimated_wait_minutes": est_wait,
            "service_name": ticket.service.name if ticket.service else None,
            "counter_name": ticket.counter.name if ticket.counter else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{ticket_id}/cancel", response_model=TicketResponse)
def cancel_ticket(ticket_id: int, db: Session = Depends(get_db)):
    try:
        ticket = QueueService.update_status(db, ticket_id, TicketStatus.CANCELLED)
        pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_phone": ticket.customer_phone,
            "queue_id": ticket.queue_id,
            "service_id": ticket.service_id,
            "counter_id": ticket.counter_id,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "called_at": ticket.called_at,
            "completed_at": ticket.completed_at,
            "position": pos,
            "estimated_wait_minutes": est_wait,
            "service_name": ticket.service.name if ticket.service else None,
            "counter_name": ticket.counter.name if ticket.counter else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{ticket_id}/assign-counter", response_model=TicketResponse)
def assign_counter(ticket_id: int, request: AssignCounterRequest, db: Session = Depends(get_db)):
    try:
        ticket = QueueService.assign_counter(db, ticket_id, request.counter_id)
        pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "customer_phone": ticket.customer_phone,
            "queue_id": ticket.queue_id,
            "service_id": ticket.service_id,
            "counter_id": ticket.counter_id,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "called_at": ticket.called_at,
            "completed_at": ticket.completed_at,
            "position": pos,
            "estimated_wait_minutes": est_wait,
            "service_name": ticket.service.name if ticket.service else None,
            "counter_name": ticket.counter.name if ticket.counter else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
