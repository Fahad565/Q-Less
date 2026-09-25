from fastapi import APIRouter, Form, Depends, Response
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Queue, Service, Ticket, TicketStatus
from app.services.queue_service import QueueService

router = APIRouter(prefix="/api/ussd", tags=["ussd"])

@router.post("", response_class=Response)
@router.post("/", response_class=Response)
def handle_ussd(
    sessionId: str = Form(""),
    serviceCode: str = Form(""),
    phoneNumber: str = Form(""),
    text: str = Form(""),
    db: Session = Depends(get_db)
):
    """
    Africa's Talking USSD Handler
    Format:
    CON <message> -> Continue session
    END <message> -> End session
    """
    text_input = text.strip()
    user_inputs = [i for i in text_input.split("*") if i] if text_input else []

    # Get primary queue (default to first queue)
    queue = db.query(Queue).first()
    if not queue:
        return Response(content="END System unavailable: No queue configured.", media_type="text/plain")

    # ROOT MENU
    if len(user_inputs) == 0:
        response_text = (
            "CON Welcome to Q-Less\n"
            "1. Join Queue\n"
            "2. My Ticket\n"
            "3. Leave Queue"
        )
        return Response(content=response_text, media_type="text/plain")

    first_choice = user_inputs[0]

    # CHOICE 1: JOIN QUEUE
    if first_choice == "1":
        services = db.query(Service).filter(Service.queue_id == queue.id).all()

        # Step 1.1: Select Service
        if len(user_inputs) == 1:
            menu = "CON Select Service:\n"
            for idx, svc in enumerate(services, 1):
                menu += f"{idx}. {svc.name}\n"
            return Response(content=menu.strip(), media_type="text/plain")

        # Step 1.2: Service chosen -> Create ticket
        if len(user_inputs) == 2:
            try:
                svc_idx = int(user_inputs[1]) - 1
                if svc_idx < 0 or svc_idx >= len(services):
                    return Response(content="END Invalid service choice.", media_type="text/plain")
                selected_service = services[svc_idx]
            except ValueError:
                return Response(content="END Invalid input.", media_type="text/plain")

            try:
                ticket = QueueService.create_ticket(
                    db=db,
                    customer_phone=phoneNumber,
                    service_id=selected_service.id
                )
                pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
                response_text = (
                    f"END Ticket Created!\n"
                    f"Ticket Number: {ticket.ticket_number}\n"
                    f"Queue Position: {pos}\n"
                    f"Estimated Wait: ~{est_wait} mins\n"
                    f"SMS confirmation sent."
                )
                return Response(content=response_text, media_type="text/plain")
            except ValueError as e:
                return Response(content=f"END {str(e)}", media_type="text/plain")

    # CHOICE 2: MY TICKET
    elif first_choice == "2":
        ticket = QueueService.get_active_ticket_for_phone(db, phoneNumber)
        if not ticket:
            return Response(content="END You do not have an active ticket in the queue.", media_type="text/plain")

        if ticket.status == TicketStatus.WAITING:
            pos, est_wait = QueueService.calculate_position_and_wait(db, ticket)
            response_text = (
                f"END Ticket {ticket.ticket_number} Status:\n"
                f"Status: WAITING\n"
                f"Position: {pos}\n"
                f"Estimated Wait: ~{est_wait} mins"
            )
        elif ticket.status == TicketStatus.CALLED:
            counter_name = ticket.counter.name if ticket.counter else "Assigned Counter"
            response_text = f"END Ticket {ticket.ticket_number} Status:\nCALLED! Please proceed to {counter_name}."
        elif ticket.status == TicketStatus.SERVING:
            counter_name = ticket.counter.name if ticket.counter else "Assigned Counter"
            response_text = f"END Ticket {ticket.ticket_number} Status:\nCurrently being served at {counter_name}."
        else:
            response_text = f"END Ticket {ticket.ticket_number} Status: {ticket.status.value}"

        return Response(content=response_text, media_type="text/plain")

    # CHOICE 3: LEAVE QUEUE
    elif first_choice == "3":
        ticket = QueueService.get_active_ticket_for_phone(db, phoneNumber)
        if not ticket:
            return Response(content="END You do not have an active ticket to cancel.", media_type="text/plain")

        if len(user_inputs) == 1:
            return Response(
                content=f"CON Are you sure you want to cancel Ticket {ticket.ticket_number}?\n1. Yes, cancel\n2. No, go back",
                media_type="text/plain"
            )

        if len(user_inputs) == 2:
            if user_inputs[1] == "1":
                QueueService.update_status(db, ticket.id, TicketStatus.CANCELLED)
                return Response(content=f"END Ticket {ticket.ticket_number} has been cancelled.", media_type="text/plain")
            else:
                return Response(content="END Cancellation aborted.", media_type="text/plain")

    return Response(content="END Invalid option. Please try again.", media_type="text/plain")
