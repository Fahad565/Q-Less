Q-Less

Your queue, on your phone.

Q-Less is a telecom-powered virtual queue management system designed for high-volume service environments such as banks, clinics, government service centres, universities, and telecom shops.

Instead of forcing customers to sit in a physical waiting area and listen for a paper ticket number, Q-Less lets them join a queue through USSD, receive a digital ticket and queue position, and get SMS notifications as their turn approaches. Staff manage the live queue from a simple web dashboard.

This project is being built as a proof of concept for the Africa's Talking Telecommunication Innovation Hackathon: Build with Africa's Talking.

1. The Problem

A traditional service-centre queue often looks like this:

Customer arrives
      |
      v
Take paper ticket
      |
      v
Sit and wait
      |
      v
Listen for:
"Ticket 27, Counter 3"
      |
      v
Proceed to counter

The customer has little visibility into:

How many people are ahead.

Roughly how long they may wait.

Whether they can safely step away from the waiting area.

When they should return.

What counter they should go to.

Q-Less moves the queue from a paper ticket + physical waiting experience to a mobile notification experience.

2. The Q-Less Idea

                    Q-LESS
       Telecom-powered virtual queue

            +-------------------+
            |     CUSTOMER      |
            +-------------------+
                     |
                  USSD
                     |
                     v
            +-------------------+
            |   QUEUE SERVICE   |
            |   / FASTAPI API   |
            +-------------------+
                 |         |
                 |         |
                 v         v
          +-----------+  +-----------+
          | Queue DB  |  | SMS Service|
          +-----------+  +-----------+
                 ^             |
                 |             v
                 |        +----------+
                 |        | Customer  |
                 |        |   Phone   |
                 |        +----------+
                 |
          +-------------------+
          |   STAFF WEB APP   |
          |   Queue Dashboard |
          +-------------------+

Core components

USSD Service
Customer-facing entry point for joining and checking a queue.

Queue Service / Backend
Owns queue state, ticket generation, position calculation, service counters, and notification triggers.

SMS Service
Sends ticket confirmation, queue-position updates, approaching-turn alerts, and counter instructions.

Staff Web Service
A browser-based dashboard where staff can view and operate the queue.

Database
Stores customers/tickets, queues, services, counters, and queue events.

3. Target User

Primary customer

A person visiting a high-volume service location who has a basic mobile phone or smartphone and wants to avoid spending the entire waiting period physically standing or sitting near a service counter.

Primary staff user

A bank teller, customer-service agent, receptionist, clinic administrator, government service officer, or other queue operator who needs a simple way to call and manage customers.

4. Example Use Case: Bank Branch

Q-Less is demonstrated using a fictional bank branch, but the architecture is intended to be reusable across many service environments.

Traditional experience

Customer -> gets Ticket 47 -> waits -> hears "47, Counter 1" -> walks to counter

Q-Less experience

Customer
   |
   | Dial USSD
   v
+----------------------+
| Q-Less                |
| 1. Join queue         |Q-Less
POST   /api/tickets/{ticket_id}/complete
POST   /api/tickets/{ticket_id}/skip
POST   /api/tickets/{ticket_id}/recall
GET    /api/tickets/{ticket_id}

These are suggested interfaces, not a requirement to implement every endpoint exactly this way.

Health endpoint

GET /health

Return a simple healthy response so the service can be verified during the demo/deployment.

13. Hackathon Demo Plan

The demo should show the complete loop rather than a collection of disconnected screens.

Scene 1 — Problem

Explain the traditional queue:

A customer takes ticket 47 and has to sit around until someone announces ticket 47.

Scene 2 — Join via USSD

Open the Africa's Talking USSD simulator.

Show:

Q-Less
1. Join Queue
2. My Ticket
3. Leave Queue

Select a service and create a ticket.

Scene 3 — Ticket appears

USSD shows:

Ticket: Q47
Position: 8
Estimated wait: ~40 mins

Scene 4 — Real SMS

The demo phone receives:

Q-Less: You are Q47.
There are 7 customers ahead of you.
Estimated wait: ~40 minutes.

Scene 5 — Staff dashboard

Staff dashboard shows Q47 in the waiting queue.

The operator repeatedly selects Call Next.

Scene 6 — Approaching notification

When Q47 reaches the configured threshold:

Q-Less: You are approaching your turn.
Please return to the service area.

Scene 7 — Counter assignment

Staff calls Q47 and assigns Counter 3.

Customer receives:

Q-Less: Q47, please proceed to Counter 3.

Scene 8 — Closing line

Q-Less turns a physical waiting queue into a mobile, notification-driven queue.
Target demo environment: Africa's Talking USSD simulator + live SMS test phone + staff web dashboard
| 2. My ticket          |
| 3. Leave queue        |
+----------------------+
   |
   | Select service
   v
+----------------------+
| Ticket: Q47           |
| Position: 8           |
| Est. wait: ~40 mins   |
+----------------------+
   |
   | SMS
   v
"You are Q47. 7 people are ahead of you."
   |
   | Queue progresses
   v
"You are approaching your turn. Please return."
   |
   | Staff calls ticket
   v
"Q47: Please proceed to Counter 3."

The important product idea is not the bank itself. The bank is a demo context for a reusable queue system.

5. Core MVP Features

Customer — USSD

Start Q-Less session.

Select Join Queue.

Select a service.

Receive a queue ticket number.

See current queue position.

See estimated waiting time.

Check ticket status.

Leave/cancel a queue entry.

Customer — SMS

Send SMS notifications for:

Queue joined / ticket issued.

Queue position / estimated wait.

Customer is approaching their turn.

Customer is called.

Customer's counter assignment.

Optional cancellation/expiry messages.

Staff — Web Dashboard

View active queues.

See current ticket being served.

See waiting tickets.

Call the next customer.

Assign/select a counter.

Mark a ticket as completed.

Skip a ticket.

Recall a ticket.

View basic queue statistics.

Backend

Ticket generation.

Queue ordering.

Position calculation.

Estimated waiting-time calculation.

Queue state transitions.

Counter assignment.

SMS notification triggers.

Basic audit/event logging.

6. Suggested USSD Flow

The exact shortcode/menu wording can change depending on the Africa's Talking environment, but the logical flow is:

USSD START
    |
    v
Q-Less
1. Join Queue
2. My Ticket
3. Leave Queue
    |
    +---- 1 ----> Select Service
    |                 |
    |                 +--> Customer Care
    |                 +--> Account Services
    |                 +--> Payments
    |                 +--> Other
    |                 |
    |                 v
    |            CREATE TICKET
    |                 |
    |                 v
    |           Show ticket + position
    |                 |
    |                 v
    |             End session
    |
    +---- 2 ----> Show ticket + live position
    |
    +---- 3 ----> Confirm leave queue

For the hackathon PoC, the USSD flow can be demonstrated through the available sandbox/simulator while the SMS can be demonstrated on a real test phone.

7. Queue Logic

The MVP uses a straightforward first-in-first-out model:

WAITING -> CALLED -> SERVING -> COMPLETED
              |
              +-> SKIPPED
              |
              +-> RECALLED
              |
              +-> CANCELLED

Example

Queue:
Q23  SERVING  Counter 2
Q24  WAITING
Q25  WAITING
Q26  WAITING
Q27  WAITING

Staff clicks Call Next:

Q23 -> COMPLETED
Q24 -> CALLED -> Counter 1

Q27's position changes automatically as earlier tickets leave the queue.

8. Estimated Wait Time

For the MVP, use a simple estimate:

Estimated wait ~= people ahead x average service time

Example:

4 people ahead
x 8 minutes average service time
= ~32 minutes

The value is clearly an estimate, not a guaranteed appointment time.

A later version can calculate rolling averages from real completed tickets.

9. Notification Logic

A practical MVP rule set:

Ticket created
    -> confirmation SMS

Position changes materially
    -> optional update SMS

Position <= configured threshold (e.g. 2)
    -> "You are approaching" SMS

Staff calls ticket
    -> "Proceed to Counter X" SMS

Ticket completed
    -> completion SMS (optional)

The threshold should be configurable rather than hard-coded into the product design.

10. System Architecture

                         +----------------------+
                         |       CUSTOMER       |
                         |  Basic phone / phone |
                         +----------+-----------+
                                    |
                              USSD interaction
                                    |
                                    v
                         +----------------------+
                         |  USSD PROVIDER /     |
                         |  SANDBOX SIMULATOR   |
                         +----------+-----------+
                                    |
                               webhook/request
                                    |
                                    v
+-------------------+      +----------------------+      +------------------+
|                   |      |                      |      |                  |
|  STAFF WEB APP    +----->+   Q-LESS BACKEND    +----->+   SMS SERVICE    |
|  Queue Dashboard  |      |      FastAPI        |      |  Africa's Talking|
|                   |<-----+                      |      |                  |
+-------------------+      +----------+-----------+      +--------+---------+
                                      |
                                      |
                                      v
                             +------------------+
                             |    DATABASE      |
                             | SQLite for PoC   |
                             +------------------+

Recommended initial stack

Frontend:       Next.js / React
Backend:        FastAPI (Python)
Database:       SQLite for MVP
USSD:           Africa's Talking USSD integration / sandbox
SMS:            Africa's Talking SMS integration
Styling:        Simple responsive UI
Deployment:     Local first; deploy only what is needed for the demo

The stack is intentionally lightweight. The goal is to prove the user experience and system flow rather than build production infrastructure.

11. Proposed Repository Structure

q-less/
|
+-- README.md
+-- PRD.md
+-- .env.example
+-- .gitignore
|
+-- backend/
|   +-- app/
|       +-- main.py
|       +-- api/
|       |   +-- ussd.py
|       |   +-- queues.py
|       |   +-- tickets.py
|       |   +-- staff.py
|       +-- services/
|       |   +-- queue_service.py
|       |   +-- sms_service.py
|       |   +-- notification_service.py
|       +-- models/
|       +-- db/
|       +-- tests/
|
+-- frontend/
|   +-- app/
|   +-- components/
|   +-- lib/
|   +-- tests/
|
+-- docs/
    +-- DEMO_SCRIPT.md
    +-- ARCHITECTURE.md

The structure can be simplified further during the first implementation sprint. Do not create folders merely for the sake of architecture.

12. API-Level Responsibilities

USSD endpoint

Receives USSD requests and returns menu text.

Conceptually:

POST /api/ussd

The endpoint should:

Identify the session.

Identify the customer/mobile number provided by the USSD channel.

Determine the current menu state.

Return the appropriate USSD response.

Create/update a queue ticket when appropriate.

Staff API

Example endpoints:

GET    /api/queues
GET    /api/queues/{queue_id}
POST   /api/queues/{queue_id}/tickets
POST   /api/tickets/{ticket_id}/call
POST   /api/tickets/{ticket_id}/complete
POST   /api/tickets/{ticket_id}/skip
POST   /api/tickets/{ticket_id}/recall
GET    /api/tickets/{ticket_id}

These are suggested interfaces, not a requirement to implement every endpoint exactly this way.

Health endpoint

GET /health

Return a simple healthy response so the service can be verified during the demo/deployment.

13. Hackathon Demo Plan

The demo should show the complete loop rather than a collection of disconnected screens.

Scene 1 — Problem

Explain the traditional queue:

A customer takes ticket 47 and has to sit around until someone announces ticket 47.

Scene 2 — Join via USSD

Open the Africa's Talking USSD simulator.

Show:

Q-Less
1. Join Queue
2. My Ticket
3. Leave Queue

Select a service and create a ticket.

Scene 3 — Ticket appears

USSD shows:

Ticket: Q47
Position: 8
Estimated wait: ~40 mins

Scene 4 — Real SMS

The demo phone receives:

Q-Less: You are Q47.
There are 7 customers ahead of you.
Estimated wait: ~40 minutes.

Scene 5 — Staff dashboard

Staff dashboard shows Q47 in the waiting queue.

The operator repeatedly selects Call Next.

Scene 6 — Approaching notification

When Q47 reaches the configured threshold:

Q-Less: You are approaching your turn.
Please return to the service area.

Scene 7 — Counter assignment

Staff calls Q47 and assigns Counter 3.

Customer receives:

Q-Less: Q47, please proceed to Counter 3.

Scene 8 — Closing line

Q-Less turns a physical waiting queue into a mobile, notification-driven queue.

14. Why Telecom Matters

Q-Less is deliberately not just a web queue application.

Its key value is the combination of:

USSD
  +
SMS
  +
Web staff operations
  +
Queue state

USSD means the customer can interact without installing an application. SMS provides asynchronous notifications that can reach the customer's phone outside the queue UI.

This also makes Q-Less relevant to digital inclusion/accessibility as a secondary theme, while its primary hackathon category is Customer Care & Support Automation.

15. Non-Goals for the MVP

Do not expand the first version into:

Native Android/iOS apps.

Full bank integrations.

Payment processing.

Complex identity verification.

Multi-country telecom operations.

Advanced machine learning.

Production-grade analytics.

Complex role-based enterprise administration.

Hardware ticket kiosks.

A full appointment-booking platform.

Those can be future directions.

16. Success Criteria

Q-Less is successful as a hackathon PoC when a judge can watch one continuous scenario and see:

1. Customer joins queue via USSD
2. Ticket is created
3. Queue position is visible
4. Staff manages queue from web dashboard
5. Customer receives SMS notification
6. Queue advances
7. Customer receives approaching-turn notification
8. Customer receives counter instruction

The entire story should work reliably with test data from start to finish.

17. Product Direction After the Hackathon

Potential extensions include:

Multi-branch queues
       |
       +-- Bank branches
       +-- Hospitals / clinics
       +-- Government offices
       +-- Universities
       +-- Telecom shops
       +-- SACCOs

Advanced version
       |
       +-- Dynamic wait-time prediction
       +-- Service-specific routing
       +-- Appointment + queue hybrid
       +-- Customer feedback
       +-- Queue analytics
       +-- Staff performance analytics
       +-- Multi-language USSD/SMS
       +-- Accessibility features

The hackathon MVP should remain small.

18. Build Principle

Prove the queue experience first. Then improve the system.

The primary objective is not to build the largest queue platform. It is to demonstrate a believable and useful telecom-enabled alternative to physical waiting.

19. Current Status

Stage: Hackathon PoC / MVP

Primary track: Customer Care & Support Automation

Secondary relevance: Digital Inclusion & Accessibility

Target demo environment: Africa's Talking USSD simulator + live SMS test phone + staff web dashboard
