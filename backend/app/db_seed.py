from sqlalchemy.orm import Session
from app.models import Queue, Service, Counter
from app.db import Base

def seed_db(db: Session):
    # Ensure tables are created on the engine bound to session
    engine = db.get_bind()
    Base.metadata.create_all(bind=engine)

    # Check if queue exists
    existing_queue = db.query(Queue).filter(Queue.name == "Mombasa Service Centre").first()
    if not existing_queue:
        queue = Queue(name="Mombasa Service Centre", location="Mombasa, Kenya")
        db.add(queue)
        db.commit()
        db.refresh(queue)

        # Add Services
        services = [
            Service(queue_id=queue.id, name="Customer Care", code_prefix="C", avg_service_minutes=5),
            Service(queue_id=queue.id, name="Account Services", code_prefix="A", avg_service_minutes=8),
            Service(queue_id=queue.id, name="Payments", code_prefix="P", avg_service_minutes=4),
            Service(queue_id=queue.id, name="Other Inquiries", code_prefix="O", avg_service_minutes=6)
        ]
        db.add_all(services)

        # Add Counters
        counters = [
            Counter(queue_id=queue.id, name="Counter 1", is_active=True),
            Counter(queue_id=queue.id, name="Counter 2", is_active=True),
            Counter(queue_id=queue.id, name="Counter 3", is_active=True)
        ]
        db.add_all(counters)
        db.commit()
        print("Database seeded with Mombasa Service Centre, default services, and counters.")

if __name__ == "__main__":
    from app.db import SessionLocal
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
