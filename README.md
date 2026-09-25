# Q-Less

> **"Your queue, on your phone."**

Q-Less is a telecom-powered virtual queue management system built for the **Africa's Talking Telecommunication Innovation Hackathon**.

- **Primary Category:** Customer Care & Support Automation
- **Secondary Track:** Digital Inclusion & Accessibility

---

## 🌟 Overview & Core Concept

In traditional service centers (banks, telecom shops, hospitals, government offices), customers are forced to wait in crowded physical waiting areas listening for ticket numbers to be called.

**Q-Less** turns physical waiting into a mobile, notification-driven experience using standard **USSD** and **SMS**:
1. **Join via USSD:** Customers dial a USSD shortcode () to pick a service and join the virtual queue without needing an app or internet connection.
2. **Digital Ticket:** The USSD response immediately displays their ticket number, live position, and estimated wait time, followed by a confirmation SMS.
3. **SMS Alerts:** As earlier tickets are served, Q-Less automatically triggers an "Approaching Turn" SMS when the customer reaches position <= 2, instructing them to return to the service area.
4. **Counter Assignment:** When staff call a customer from the web dashboard, an SMS is sent directing them to a specific counter (e.g. *"Q47, please proceed to Counter 2"*).
5. **Staff Web Dashboard:** Staff manage queues, call next customers, complete, skip, recall, or assign counters using a real-time web interface.

---

## 📐 Architecture



---

## 🚀 Key Features

- **Standard USSD Integration:** Compatible with Africa's Talking USSD protocol ( /  responses).
- **Multi-Mode SMS Service:** Configurable for  (local testing UI feed), , and  Africa's Talking environments.
- **Smart Notification Engine:** Prevents notification spam by tracking  and only triggering alerts when position thresholds or counter calls occur.
- **Duplicate Ticket Prevention:** Blocks multiple active tickets for the same phone number until previous tickets are completed/cancelled.
- **Interactive USSD Simulator:** Built directly into the Staff Web Dashboard for seamless local hackathon demonstrations.

---

## 🛠️ Local Setup & Development

### Backend Setup

1. Navigate to backend:

2. Create and activate virtual environment:

3. Install dependencies:

4. Run server:


### Frontend Setup

1. Navigate to frontend:

2. Install dependencies:

3. Run dev server:

4. Open http://localhost:3000 in your browser.

---

## 🧪 Running Automated Tests

Run backend tests:


Run frontend build check:

> frontend@0.1.0 build
> next build

▲ Next.js 16.3.6 (Turbopack)
✓ Running next.config.ts took 40ms

  Creating an optimized production build ...
✓ Compiled successfully in 7.3s
  Running TypeScript ...
  Finished TypeScript in 2.6s ...
  Collecting page data using 3 workers ...
  Generating static pages using 3 workers (0/4) ...
  Generating static pages using 3 workers (1/4)
  Generating static pages using 3 workers (2/4)
  Generating static pages using 3 workers (3/4)
✓ Generating static pages using 3 workers (4/4) in 276ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
└ ○ /_not-found


○  (Static)  prerendered as static content

---

## 🌐 Deploying to Render

Q-Less includes a preconfigured  Blueprint defining two independent Docker web services ( and ) on the                total        used        free      shared  buff/cache   available
Mem:         8150116      763880     5704200         540     1975092     7386236
Swap:              0           0           0 plan in .

---

## 🎬 Golden Path Demo Script

1. **Open Staff Dashboard:** Visit . Observe "Mombasa Service Centre" with empty queues.
2. **Join Queue via USSD:**
   - In the **USSD Phone Simulator** panel on the right, keep phone number  and click **Dial *384#**.
   - Select option  (Join Queue) and click **Send**.
   - Select option  (Customer Care) and click **Send**.
   - The USSD screen returns .
3. **Observe Ticket & Confirmation SMS:**
   - Ticket **C01** appears immediately under **Waiting Queue**.
   - In the **Live SMS Feed**, observe the Ticket Confirmation SMS.
4. **Join Second Customer:**
   - Change phone number in simulator to  and dial  ->  -> .
   - Ticket **C02** is generated at Position 2.
5. **Call Next Customer:**
   - On the Staff Dashboard, select **Counter 1** and click **📢 Call Next**.
   - Ticket **C01** moves to **Now Serving** at Counter 1.
   - An SMS notification is sent to : *"Q-Less: Ticket C01, please proceed to Counter 1."*
   - Ticket **C02** moves to Position 1, triggering an "Approaching Turn" SMS alert.
6. **Complete Ticket:**
   - Click **✓ Complete** on Ticket C01.
