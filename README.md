# Q-Less

> **"Your queue, on your phone."**

Q-Less is a telecom-powered virtual queue management system built for the **Africa's Talking Telecommunication Innovation Hackathon**.

- **Primary Category:** Customer Care & Support Automation
- **Secondary Track:** Digital Inclusion & Accessibility

---

## 🌟 Overview & Core Concept

In traditional service centers (banks, telecom shops, hospitals, government offices), customers are forced to wait in crowded physical waiting areas listening for ticket numbers to be called.

**Q-Less** turns physical waiting into a mobile, notification-driven experience using standard **USSD** and **SMS**:
1. **Join via USSD:** Customers dial a USSD shortcode (`*384#`) to pick a service and join the virtual queue without needing an app or internet connection.
2. **Digital Ticket:** The USSD response immediately displays their ticket number, live position, and estimated wait time, followed by a confirmation SMS.
3. **SMS Alerts:** As earlier tickets are served, Q-Less automatically triggers an "Approaching Turn" SMS when the customer reaches position <= 2, instructing them to return to the service area.
4. **Counter Assignment:** When staff call a customer from the web dashboard, an SMS is sent directing them to a specific counter (e.g. *"Q-Less: Ticket C01, please proceed to Counter 1"*).
5. **Staff Web Dashboard:** Staff manage queues, call next customers, complete, skip, recall, or assign counters using a real-time web interface.

---

## 📱 SMS Configuration

Q-Less supports both **Mock Mode** (for local development and testing) and **Live Mode** (for real SMS delivery to physical mobile phones via Africa's Talking).

### Mock Mode (Default)

```bash
AT_SMS_MODE=mock
```

- **Used for:** Local development and automated testing.
- **Behavior:** No external HTTP/API requests are made to Africa's Talking. Sent SMS messages appear in real-time in the Staff Web Dashboard's **Live SMS Feed** tagged as **Mock Provider**.

### Live Mode (Africa's Talking Production)

```bash
AT_SMS_MODE=live
AFRICASTALKING_USERNAME=your_live_username
AFRICASTALKING_API_KEY=your_live_api_key
AFRICASTALKING_SENDER_ID=
```

- **Used for:** Demonstrations and production testing where real SMS messages are sent to actual mobile phones.
- **Requirements:**
  - A production/live Africa's Talking account.
  - Live Africa's Talking Username (do **NOT** use `sandbox`).
  - Live Africa's Talking API Key.
  - Optional Sender ID (`AFRICASTALKING_SENDER_ID`). If omitted or empty, Q-Less will omit the sender parameter and allow Africa's Talking to use your account's default configuration or respond accordingly.

> **Note on USSD vs SMS:**
> For the Q-Less demo, USSD remains hosted on Africa's Talking Sandbox / Web Simulator, while SMS transitions to Live mode to deliver real SMS messages to actual mobile handsets.

---

## 🛠️ Local Setup & Development

### Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Configure `AT_SMS_MODE` and your Africa's Talking credentials in `.env`.

### Backend Setup

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run build
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🧪 Testing & Verification

### Running Automated Tests

Run backend tests:
```bash
python -m pytest backend/tests
```

Run frontend build check:
```bash
npm --prefix frontend run build
```

### Manual Live SMS Test Endpoint

You can test live SMS delivery independently of the queue flow using `POST /api/notifications/test`:

```bash
curl -X POST "http://localhost:8000/api/notifications/test"   -H "Content-Type: application/json"   -d '{
    "phone_number": "+254712345678",
    "message": "Q-Less live SMS test message."
  }'
```

---

## 🌐 Deploying to Render

Q-Less includes a preconfigured `render.yaml` Blueprint defining the API and Staff Dashboard web services. When deploying on Render, configure the required environment variables:
- `AT_SMS_MODE` (`mock` or `live`)
- `AFRICASTALKING_USERNAME`
- `AFRICASTALKING_API_KEY` (set as secret)
- `AFRICASTALKING_SENDER_ID` (optional)

---

## 🎬 Golden Path Demo Script

1. **Open Staff Dashboard:** Visit `http://localhost:3000`. Observe "Mombasa Service Centre" with empty queues.
2. **Join Queue via USSD:**
   - In the **USSD Phone Simulator** panel on the right, enter your real Kenyan phone number (e.g., `+2547XXXXXXXX` or `07XXXXXXXX`) and click **Dial *384#**.
   - Select option `1` (Join Queue) and click **Send**.
   - Select option `1` (Customer Care) and click **Send**.
   - The USSD screen returns `Ticket Created! Ticket Number: C01`.
3. **Observe Confirmation SMS:**
   - Ticket **C01** appears immediately under **Waiting Queue**.
   - In `AT_SMS_MODE=live`, a real SMS confirmation arrives on your mobile phone!
4. **Call Next Customer:**
   - On the Staff Dashboard, select **Counter 1** and click **📢 Call Next**.
   - Ticket **C01** moves to **Now Serving** at Counter 1.
   - An SMS notification is sent to your phone: *"Q-Less: Ticket C01, please proceed to Counter 1."*
5. **Complete Ticket:**
   - Click **✓ Complete** on Ticket C01.
