from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import Queue, Ticket, TicketStatus
from app.schemas import QueueResponse, TicketResponse, AssignCounterRequest
from app.services.queue_service import QueueService

router = APIRouter(prefix="/api/queues", tags=["queues"])

@router.get("", response_model=List[QueueResponse])
@router.get("/", response_model=List[QueueResponse])
def list_queues(db: Session = Depends(get_db)):
    return db.query(Queue).all()

@router.get("/{queue_id}")
def get_queue(queue_id: int, db: Session = Depends(get_db)):
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    # Fetch active tickets for this queue
    tickets = db.query(Ticket).filter(
        Ticket.queue_id == queue_id,
        Ticket.status.in_([TicketStatus.WAITING, TicketStatus.CALLED, TicketStatus.SERVING])
    ).order_by(Ticket.id.asc()).all()

    ticket_responses = []
    for t in tickets:
        pos, est_wait = QueueService.calculate_position_and_wait(db, t)
        t_dict = {
            "id": t.id,
            "ticket_number": t.ticket_number,
            "customer_phone": t.customer_phone,
            "queue_id": t.queue_id,
            "service_id": t.service_id,
            "counter_id": t.counter_id,
            "status": t.status,
            "created_at": t.created_at,
            "called_at": t.called_at,
            "completed_at": t.completed_at,
            "position": pos,
            "estimated_wait_minutes": est_wait,
            "service_name": t.service.name if t.service else None,
            "counter_name": t.counter.name if t.counter else None
        }
        ticket_responses.append(t_dict)

    return {
        "id": queue.id,
        "name": queue.name,
        "location": queue.location,
        "services": queue.services,
        "counters": queue.counters,
        "tickets": ticket_responses
    }

@router.post("/{queue_id}/call-next", response_model=TicketResponse)
def call_next(queue_id: int, counter_id: int = None, db: Session = Depends(get_db)):
    ticket = QueueService.call_next(db, queue_id, counter_id)
    if not ticket:
        raise HTTPException(status_code=400, detail="No waiting tickets in queue")

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
