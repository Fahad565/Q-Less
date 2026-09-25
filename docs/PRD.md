# Q-Less — Product Requirements Document

**Product:** Q-Less
**Type:** Telecom-powered virtual queue management PoC
**Hackathon:** Africa's Talking — Telecommunication Innovation Hackathon: Build with Africa's Talking
**Primary category:** Customer Care & Support Automation
**Secondary relevance:** Digital Inclusion & Accessibility
**Document status:** MVP / Hackathon PRD

---

# 1. Product Summary

Q-Less is a virtual queue system that allows customers to join and monitor a physical service queue through **USSD**, while receiving important queue updates through **SMS**. Staff operate the queue using a **web dashboard**.

The product replaces the passive waiting experience of:

```text
Paper ticket -> sit -> listen for ticket number -> walk to counter
```

with:

```text
USSD -> digital ticket -> receive updates -> return when needed -> counter
```

The initial proof of concept uses a bank branch as the demonstration environment, but Q-Less is designed as a reusable service-queue platform.

---

# 2. Problem Statement

High-volume service centres often require customers to take a queue number and remain physically present while waiting. Customers may not know their true position in the queue, may not know the estimated waiting time, and may miss their turn if they step away.

The current experience creates avoidable friction:

```text
Customer arrives
      |
      v
Gets ticket
      |
      v
Waits physically
      |
      v
Monitors announcements
      |
      v
Eventually receives service
```

Q-Less aims to give customers visibility and notifications without requiring a dedicated mobile application.

---

# 3. Product Vision

> **Turn physical waiting into a mobile, notification-driven experience.**

A customer should be able to participate in a service queue using an ordinary mobile phone, understand where they are in the queue, and receive an actionable notification when their turn approaches.

---

# 4. Target Users

## 4.1 Customer

A person waiting for service at a bank, clinic, government service centre, university, telecom shop, SACCO, or similar environment.

### Customer needs

- Join a queue easily.
- Know their ticket number.
- Know their approximate queue position.
- Understand the expected wait.
- Avoid unnecessary physical waiting.
- Know when to return.
- Know which counter to approach.

## 4.2 Staff

A member of staff responsible for serving customers and advancing a queue.

### Staff needs

- See waiting customers.
- Call the next customer.
- Assign a counter.
- Complete or skip tickets.
- Recall tickets when necessary.
- See queue state in real time.

---

# 5. Goals

## Primary goals

1. Allow customers to join a queue through USSD.
2. Generate a unique ticket number.
3. Track live queue position.
4. Provide a simple estimated waiting time.
5. Send SMS notifications to customers.
6. Give staff a web interface to operate the queue.
7. Demonstrate the full customer-to-staff workflow in a hackathon PoC.

## Secondary goals

1. Avoid requiring a native mobile application.
2. Make the interaction understandable on low-bandwidth/basic-phone environments.
3. Demonstrate how telecom channels can complement a web-based operational system.

---

# 6. Non-Goals

The MVP will not attempt to provide:

- Full enterprise identity and access management.
- Real bank integrations.
- Real financial transactions.
- Native mobile applications.
- Advanced predictive ML.
- Production-grade fraud detection.
- Full appointment scheduling.
- Hardware ticket machines.
- Complex multi-country telecom routing.
- Large-scale analytics.

The PoC exists to prove the core workflow.

---

# 7. Product Scope

```text
                       Q-LESS MVP
                           |
         +-----------------+------------------+
         |                 |                  |
         v                 v                  v
       USSD               SMS            STAFF WEB
     CUSTOMER           CUSTOMER          DASHBOARD
         |                 |                  |
         +-----------------+------------------+
                           |
                           v
                    QUEUE BACKEND
                           |
                           v
                       DATABASE
```

---

# 8. Core User Journey

```text
[1] Customer chooses service
          |
          v
[2] Customer joins queue via USSD
          |
          v
[3] Backend creates ticket
          |
          v
[4] Customer receives ticket + position
          |
          v
[5] SMS confirmation is sent
          |
          v
[6] Staff processes queue
          |
          v
[7] Queue position decreases
          |
          v
[8] Customer approaches threshold
          |
          v
[9] SMS: "Please return"
          |
          v
[10] Staff calls customer
          |
          v
[11] SMS: "Proceed to Counter X"
          |
          v
[12] Staff completes ticket
```

---

# 9. Functional Requirements

## FR-001 — USSD session start

The system must accept a USSD session and present the Q-Less menu.

Example:

```text
Q-Less
1. Join Queue
2. My Ticket
3. Leave Queue
```

### Acceptance criteria

- A USSD session can be started.
- The menu is returned successfully.
- The session can progress through menu states.

---

## FR-002 — Join queue

The customer must be able to select **Join Queue** and choose a service.

Example:

```text
Select service:
1. Customer Care
2. Account Services
3. Payments
4. Other
```

### Acceptance criteria

- Customer can select a valid service.
- A ticket is created.
- Ticket is placed at the end of the queue.
- Customer receives ticket number and current position.

---

## FR-003 — Digital ticket

Each active queue entry must have a unique ticket identifier within the queue/branch context.

Example:

```text
Q47
```

### Acceptance criteria

- No two active tickets share the same queue ticket number.
- Ticket remains traceable throughout its lifecycle.

---

## FR-004 — Queue position

The customer must be able to retrieve the current position of their ticket.

Example:

```text
Ticket: Q47
Position: 4
```

### Acceptance criteria

- Position reflects completed/cancelled/skipped entries according to queue rules.
- Position can be retrieved from USSD.

---

## FR-005 — Estimated waiting time

The backend must calculate a simple estimated waiting time.

```text
Estimated wait = people ahead x average service time
```

### Acceptance criteria

- A service can have a configurable average service time.
- Estimate is recalculated as queue position changes.
- The UI labels the value as an estimate.

---

## FR-006 — SMS ticket confirmation

After a successful join operation, the system should send a confirmation SMS.

Example:

```text
Q-Less: You are Q47.
There are 7 customers ahead of you.
Estimated wait: ~40 minutes.
```

### Acceptance criteria

- SMS is triggered after ticket creation.
- Message includes the ticket number.
- Message includes useful queue information.

---

## FR-007 — Approaching-turn notification

The system must detect when a ticket reaches a configurable proximity threshold.

Example:

```text
Position <= 2
```

### Acceptance criteria

- Threshold can be configured.
- Customer is not repeatedly spammed with the same notification.
- An approaching-turn event is recorded.

Example SMS:

```text
Q-Less: You are approaching your turn.
Please return to the service area.
```

---

## FR-008 — Staff dashboard

Staff must be able to view the current queue.

Minimum view:

```text
NOW SERVING
Q23 -> Counter 2

WAITING
Q24
Q25
Q26
Q27

[ACTION: CALL NEXT]
```

### Acceptance criteria

- Queue is visible from a browser.
- Waiting entries are displayed in order.
- Current serving ticket is identifiable.

---

## FR-009 — Call next

Staff can call the next waiting ticket.

### Acceptance criteria

- Next eligible ticket is selected according to queue order.
- Ticket moves to the called/serving state.
- Staff can select a counter.
- Customer receives a counter instruction SMS.

Example:

```text
Q-Less: Q47, please proceed to Counter 3.
```

---

## FR-010 — Complete ticket

Staff can mark a ticket as completed.

### Acceptance criteria

- Ticket leaves the active waiting queue.
- Next eligible customer becomes available to call.
- Completion time is recorded.

---

## FR-011 — Skip ticket

Staff can skip a ticket when the customer does not respond.

### Acceptance criteria

- Ticket is marked skipped.
- Queue can continue.
- Ticket remains visible in an appropriate history/audit state.

---

## FR-012 — Recall ticket

Staff can recall a previously called ticket.

### Acceptance criteria

- Staff can trigger a recall.
- Optional recall notification can be sent.

---

## FR-013 — Customer leaves queue

A customer can cancel/leave their active queue position through USSD.

### Acceptance criteria

- Ticket is marked cancelled.
- Ticket is removed from active queue calculations.
- A cancellation event is recorded.

---

# 10. Queue State Model

```text
             +-----------+
             |  WAITING  |
             +-----+-----+
                   |
                CALL NEXT
                   |
                   v
             +-----------+
             |   CALLED  |
             +-----+-----+
                   |
                   v
             +-----------+
             |  SERVING  |
             +--+-----+--+
                |     |
                |     +----------------+
             COMPLETE                 SKIP
                |                      |
                v                      v
          +-----------+          +-----------+
          | COMPLETED |          |  SKIPPED  |
          +-----------+          +-----------+

WAITING ---------------------> CANCELLED
                 customer leaves
```

For the MVP, `CALLED` and `SERVING` may be represented as one state if that simplifies implementation. The logical distinction is useful for the product model.

---

# 11. SMS Notification Matrix

| Event | Recipient | Example action |
|---|---|---|
| Ticket created | Customer | Confirm ticket + position |
| Position threshold reached | Customer | Ask customer to return |
| Ticket called | Customer | Provide counter number |
| Ticket recalled | Customer | Ask customer to approach again |
| Ticket cancelled | Customer | Confirm cancellation |
| Ticket completed | Customer | Optional completion confirmation |

The MVP should prioritize the first three.

---

# 12. Staff Dashboard Requirements

## Queue overview

The main dashboard should show:

```text
Q-LESS | Mombasa Service Centre

Queue: Customer Care

Currently Serving: Q23
Counter: 2

Next:
Q24
Q25
Q26
Q27

---------------------------------
[ CALL NEXT ]
---------------------------------
```

## Ticket details

A selected ticket should show:

- Ticket number.
- Service.
- Customer phone identifier (masked where appropriate).
- Status.
- Position.
- Created time.
- Called time.
- Counter.

For the hackathon demo, the UI can use test data and simplified staff access.

---

# 13. Data Model

A minimal relational model can use the following entities.

## Queue

```text
id
name
branch_name
active
created_at
```

## Service

```text
id
queue_id
name
average_service_minutes
active
```

## Counter

```text
id
queue_id
name_or_number
active
```

## Ticket

```text
id
queue_id
service_id
ticket_number
customer_phone
status
position_snapshot (optional)
created_at
called_at
completed_at
counter_id
```

## Queue Event

```text
id
ticket_id
event_type
metadata
created_at
```

The event table is useful because it gives the PoC a simple audit trail.

---

# 14. Technical Architecture

```text
                         CUSTOMER
                            |
                     *XXX# / USSD
                            |
                            v
               +--------------------------+
               | Africa's Talking USSD   |
               | Sandbox / live channel   |
               +------------+-------------+
                            |
                        HTTP webhook
                            |
                            v
+----------------+  +----------------------+  +-------------------+
|                |  |                      |  |                   |
| STAFF WEB APP  +->+  Q-LESS FASTAPI API +->+   SMS SERVICE     |
| Next.js        |  |                      |  | Africa's Talking  |
|                |<-+  Queue Engine        |  |                   |
+----------------+  |  Notification Logic |  +---------+---------+
                    +----------+-----------+            |
                               |                        SMS
                               v                         |
                    +---------------------+              v
                    |      SQLite         |         CUSTOMER PHONE
                    |      for PoC        |
                    +---------------------+
```

---

# 15. Interface Boundaries

## USSD service

Responsible for:

- Receiving USSD requests.
- Maintaining menu/session state.
- Calling backend queue operations.
- Returning USSD text responses.

It should **not** own business logic such as queue ordering. That belongs in the queue service.

## SMS service

Responsible for:

- Formatting outbound SMS.
- Sending through the telecom messaging provider.
- Returning success/failure state to the backend.
- Recording notification events.

## Web service

Responsible for:

- Staff dashboard.
- Queue display.
- Staff actions.
- API interaction.

## Queue service

Responsible for:

- Creating tickets.
- Ordering tickets.
- Calculating queue positions.
- Managing ticket states.
- Calculating estimated waiting time.
- Emitting notification events.

---

# 16. Non-Functional Requirements

## NFR-001 — Simplicity

A customer should be able to join the queue using a small number of USSD interactions.

## NFR-002 — Reliability

Queue operations must be deterministic. Calling the next ticket should not accidentally create duplicate or conflicting active calls.

## NFR-003 — Responsiveness

The staff dashboard should update quickly after queue actions.

For the PoC, polling is acceptable. WebSockets are optional and not required.

## NFR-004 — Accessibility

The customer workflow should not depend on a smartphone app.

## NFR-005 — Security

The PoC should avoid exposing full customer phone numbers in the staff UI where unnecessary.

## NFR-006 — Observability

The backend should log important queue and notification events so that failures can be diagnosed during the demo.

---

# 17. Error Handling

The following cases must be handled gracefully:

### USSD session timeout

Show a concise message allowing the customer to start again.

### Invalid menu selection

Return a useful error and allow retry.

### SMS failure

The queue ticket should remain valid even if an SMS fails. Log the notification failure.

### Customer tries to join twice

Return the current active ticket instead of creating an unnecessary duplicate, unless the product explicitly allows multiple queues.

### Staff calls with no waiting tickets

Show:

```text
No waiting customers.
```

---

# 18. Hackathon Demonstration Environment

The intended demo uses three surfaces:

```text
+---------------------------+
| Laptop: Staff Dashboard   |
+---------------------------+

              +
              |
              |
              v
+---------------------------+
| Laptop: USSD Simulator    |
+---------------------------+

              +
              |
              |
              v
+---------------------------+
| Physical phone: SMS       |
+---------------------------+
```

### USSD

Use the Africa's Talking sandbox/simulator to demonstrate the USSD conversation.

### SMS

Use the configured test environment/number so the customer notifications can be shown live on a phone where supported.

### Web

Run the staff dashboard on the laptop alongside the USSD simulator.

The objective is to make the three channels appear as **one continuous system**.

---

# 19. Demo Scenario

### Setup

Create a queue with:

```text
Branch: Q-Less Mombasa Service Centre
Service: Customer Care
Average service time: 8 minutes
Counters: 1, 2, 3
```

Seed the queue with several tickets:

```text
Q23
Q24
Q25
Q26
```

Then use the USSD simulator as a new customer to create:

```text
Q27
```

### Demo script

**Step 1:** Customer joins using USSD.

**Step 2:** Q27 is displayed with position and estimated wait.

**Step 3:** SMS confirmation appears on the phone.

**Step 4:** Staff dashboard shows Q27 waiting.

**Step 5:** Staff clicks `CALL NEXT` several times.

**Step 6:** Q27 reaches the configured notification threshold.

**Step 7:** Phone receives approaching-turn SMS.

**Step 8:** Staff calls Q27 and selects Counter 3.

**Step 9:** Phone receives counter SMS.

**Step 10:** Staff completes Q27.

This should be the **single golden path** that must work before adding extras.

---

# 20. MVP Acceptance Test

The MVP is considered demo-ready when the following test passes from a clean start.

```text
[ ] Start USSD session
[ ] Select Join Queue
[ ] Select service
[ ] Create Q-ticket
[ ] Verify ticket appears in backend
[ ] Verify ticket appears in staff dashboard
[ ] Verify position is calculated
[ ] Verify estimated wait is displayed
[ ] Verify confirmation SMS is sent
[ ] Staff calls earlier tickets
[ ] Verify Q-ticket position decreases
[ ] Reach notification threshold
[ ] Verify approaching SMS is sent once
[ ] Staff calls Q-ticket
[ ] Assign counter
[ ] Verify counter SMS is sent
[ ] Complete Q-ticket
[ ] Verify ticket no longer appears as waiting
```

---

# 21. Development Milestones

## Milestone 1 — Project Foundation

Deliver:

- Repository.
- Backend skeleton.
- Frontend skeleton.
- Database setup.
- Environment variables.
- `/health` endpoint.

## Milestone 2 — Queue Engine

Deliver:

- Queues.
- Services.
- Tickets.
- Queue ordering.
- Position calculation.
- Ticket state transitions.

## Milestone 3 — Staff Dashboard

Deliver:

- Queue list.
- Waiting tickets.
- Current ticket.
- Call next.
- Complete.
- Skip.
- Recall.

## Milestone 4 — USSD

Deliver:

- USSD entry point.
- Join queue flow.
- My ticket flow.
- Leave queue flow.
- Session handling.

## Milestone 5 — SMS

Deliver:

- Ticket confirmation.
- Approaching-turn notification.
- Counter notification.
- Notification event logging.

## Milestone 6 — Demo Integration

Deliver:

- Full golden path.
- Realistic test data.
- Error handling.
- Dashboard polish.
- Demo script.

## Milestone 7 — Presentation

Deliver:

- README.
- Pitch deck.
- Demo recording.
- Architecture diagram.
- Project explanation.

---

# 22. Suggested Agile Backlog

## Epic A — Queue Engine

```text
A1 Create queue model
A2 Create service model
A3 Create ticket model
A4 Implement FIFO queue
A5 Calculate position
A6 Calculate estimated wait
A7 Implement ticket state transitions
A8 Add queue event logging
```

## Epic B — USSD

```text
B1 Create USSD webhook
B2 Implement root menu
B3 Implement service selection
B4 Create ticket from USSD
B5 Implement My Ticket
B6 Implement Leave Queue
B7 Handle invalid input
B8 Handle timeout/session restart
```

## Epic C — SMS

```text
C1 Create SMS abstraction
C2 Send ticket confirmation
C3 Detect approaching threshold
C4 Send approaching notification
C5 Send counter assignment notification
C6 Log SMS events/failures
```

## Epic D — Staff Web

```text
D1 Queue dashboard layout
D2 Display waiting tickets
D3 Display current serving ticket
D4 Implement Call Next
D5 Implement counter assignment
D6 Implement Complete
D7 Implement Skip
D8 Implement Recall
```

## Epic E — Demo

```text
E1 Create seeded demo queue
E2 Verify USSD simulator flow
E3 Verify live SMS test
E4 Run golden path repeatedly
E5 Fix demo-breaking failures
E6 Record demo
```

---

# 23. Priority Order

When time is limited, build in exactly this order:

```text
1. Queue engine
2. Staff dashboard
3. USSD join queue
4. SMS ticket confirmation
5. Call next + counter SMS
6. Approaching-turn SMS
7. My Ticket / Leave Queue
8. Skip / Recall
9. UI polish
10. Optional extras
```

Do not let optional features delay the golden path.

---

# 24. Future Product Opportunities

After proving the MVP, Q-Less could evolve into:

### Multi-location queue platform

```text
Q-Less Platform
 |
 +-- Bank Branch A
 +-- Bank Branch B
 +-- Clinic A
 +-- Government Centre
 +-- Telco Shop
```

### Hybrid appointment + queue

Allow customers to book a time window while still supporting a live queue.

### Smarter wait prediction

Replace the fixed average with rolling service-time data.

### Customer feedback

Send a post-service SMS survey.

### Multi-language interactions

Support localized USSD/SMS wording where appropriate.

### Queue analytics

Show average wait, service time, peak periods, abandonment, and completed tickets.

---

# 25. Product Positioning

### One-line description

> **Q-Less lets customers join a service queue via USSD and receive SMS alerts when their turn approaches, while staff manage the queue from a web dashboard.**

### Short pitch

> **Q-Less turns a physical queue into a mobile queue. Customers don't need an app: they use USSD to get a digital ticket, receive SMS updates while they wait, and are notified when it is time to return and which counter to use. Staff get a simple web dashboard to manage the queue.**

### Core value proposition

```text
Traditional queue:
WAIT -> LISTEN -> GUESS -> WAIT

Q-Less:
JOIN -> KNOW -> GET NOTIFIED -> RETURN -> SERVE
```

---

# 26. Design Principles

### 1. Telecom-first

USSD and SMS are first-class product channels, not afterthoughts.

### 2. Simple for customers

A customer should not need an app, account creation flow, or technical knowledge to join the queue.

### 3. Simple for staff

A staff member should be able to understand the queue immediately and call the next ticket with minimal interaction.

### 4. Actionable notifications

Every SMS should tell the customer something useful and, when appropriate, what to do next.

### 5. Honest estimates

Waiting time is an estimate. Q-Less should not imply a guaranteed service time.

### 6. Build the smallest credible system

The hackathon goal is a working proof of concept, not a complete enterprise queue product.

---

# 27. Final Definition of Done

Q-Less MVP is **Done** when:

```text
Customer
   |
   | USSD
   v
Gets ticket
   |
   v
Sees queue position
   |
   v
Receives SMS
   |
   v
Staff advances queue
   |
   v
Customer is notified
   |
   v
Counter assigned
   |
   v
Customer served
```

The workflow must be demonstrable end-to-end, repeatable, and understandable without explaining the implementation details first.

---

# 28. ASCII System Diagram — Final

```text
                                  Q - L E S S
                     Telecom-Powered Virtual Queue

                                      +------------------+
                                      |     CUSTOMER     |
                                      | Basic phone /    |
                                      | smartphone       |
                                      +--------+---------+
                                               |
                            +------------------+------------------+
                            |                                     |
                         USSD                                   SMS
                            |                                     ^
                            v                                     |
                  +-------------------+                           |
                  | Africa's Talking |                           |
                  | USSD Channel /    |                           |
                  | Sandbox Simulator |                           |
                  +---------+---------+                           |
                            |                                     |
                         webhook                                  |
                            |                                     |
                            v                                     |
                    +-----------------------------------+
                    |          Q - L E S S              |
                    |            BACKEND                |
                    |                                   |
                    |  +-----------------------------+  |
                    |  |       Queue Engine          |  |
                    |  |                             |  |
                    |  | Ticket generation           |  |
                    |  | FIFO ordering               |  |
                    |  | Position calculation       |  |
                    |  | Wait-time estimation       |  |
                    |  | Ticket state management    |  |
                    |  +-------------+---------------+  |
                    |                |                  |
                    |  +-------------v---------------+  |
                    |  |      Notification Logic     |  |
                    |  +-------------+---------------+  |
                    +----------------|------------------+
                                     |
                           +---------+---------+
                           |                   |
                           v                   v
                  +----------------+   +------------------+
                  |    DATABASE    |   |   SMS SERVICE    |
                  | SQLite for PoC |   | Africa's Talking |
                  +----------------+   +--------+---------+
                                               |
                                               |
                                               v
                                     +-------------------+
                                     | CUSTOMER'S PHONE  |
                                     | SMS notifications |
                                     +-------------------+

                                      ^
                                      |
                                HTTP / REST API
                                      |
                         +------------+-------------+
                         |                          |
                         |      STAFF WEB APP       |
                         |        Next.js           |
                         |                          |
                         |  +--------------------+  |
                         |  | Queue Dashboard    |  |
                         |  |                    |  |
                         |  | NOW SERVING        |  |
                         |  | WAITING TICKETS    |  |
                         |  | CALL NEXT          |  |
                         |  | COUNTER            |  |
                         |  | COMPLETE / SKIP    |  |
                         |  +--------------------+  |
                         +--------------------------+


                  GOLDEN PATH

              USSD
                |
                v
          JOIN QUEUE
                |
                v
          CREATE TICKET
                |
                +----------------------+
                |                      |
                v                      v
         STAFF DASHBOARD             SMS
                |                      |
          CALL NEXT                   |
                |                      |
                +----------+-----------+
                           |
                           v
                    COUNTER ASSIGNMENT
                           |
                           v
                         SERVE
                           |
                           v
                       COMPLETE
```
