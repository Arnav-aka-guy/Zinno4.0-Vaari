# Vaari Demo Setup Guide: From Cold Laptop to Phone over HTTPS

This guide walks through bringing up the complete Vaari operations demo from a cold laptop, connecting a phone over secure HTTPS to capture real GPS evidence, and handling venue network fallbacks.

---

### Step 1: Cold Start and Prerequisites
1. Open PowerShell / Terminal in the repository root directory (`varri/`).
2. Run setup (if first time or dependencies need syncing):
   ```bash
   python tasks.py setup
   ```
3. Connect your laptop and phone to the same venue Wi-Fi or mobile hotspot.

---

### Step 2: Clean Seed and Demo Reset
1. Reset the database to the verified rehearsal seed:
   ```bash
   python tasks.py reset
   ```
2. Confirm the output shows:
   - `Scheduled: 28`
   - `Will miss: 7`
   - `Needs info: 5`
   - Printed driver URLs for each active machine.

---

### Step 3: Start the Cloudflare HTTPS Tunnel
> **Passcode Safety Check:** `python tasks.py tunnel` refuses to start if `VAARI_DEMO_PASSCODE` is empty, `change-me`, or shorter than 12 characters. Set a strong passcode in `.env` before starting the tunnel.

1. In a separate terminal window, start the tunnel:
   ```bash
   python tasks.py tunnel
   ```
2. Once connected, copy the generated public HTTPS URL, for example:
   `https://random-words-here.trycloudflare.com`
3. Add this URL to your `.env` file so generated records and QR links point to HTTPS:
   ```env
   VAARI_PUBLIC_BASE_URL=https://random-words-here.trycloudflare.com
   ```

---

### Step 4: Launch the Unified Server
1. In your primary terminal, start serve mode (builds the web frontend and serves API + SPA together):
   ```bash
   python tasks.py serve
   ```
2. The terminal prints your local URL (`http://localhost:8000`), your LAN URL, and each machine's driver link.

---

### Step 5: Open the Desk on Laptop
1. In your laptop browser, navigate to:
   ```
   http://localhost:8000/desk
   ```
2. Enter the demo passcode: `change-me`.
3. Open the **Machines** tab. Under **Super Seeder 01**, you will see the full Driver Portal URL with a **Copy** button.

---

### Step 6: Connect the Driver Phone over HTTPS
1. On the phone browser (Safari / Chrome), open the tunnel link for the driver:
   ```
   https://random-words-here.trycloudflare.com/driver/<machine-token>
   ```
   *(Alternatively, copy from the Desk or use the phone's camera to scan a QR code).*
2. The phone will ask for **Camera** and **Location** permissions. Tap **Allow**.
3. Select **Job #1** (scheduled for today):
   - Tap **Camera**, take or select a field photo.
   - Tap **Start Job**. The status immediately transitions to *In Progress*.
   - Tap **Mark Done**, take a completion photo.
   - Tap **Complete Job**. The completion receipt provides a one-tap link to the signed audit record.

---

### Step 7: Fallback if Venue Wi-Fi or Tunnel Fails
If venue Wi-Fi blocks tunnels or outgoing UDP/TCP connections:
1. Do not panic: open the driver link directly in a new tab on the laptop browser:
   ```
   http://localhost:8000/driver/<machine-token>
   ```
2. Complete **Start** and **Done** from the laptop tab using sample photos from `tests/fixtures/sample_field.jpg`.
3. Because laptops lack real mobile GPS, the system cleanly logs `position_state = not_given` without blocking the demo.
4. On the resulting record page (`/record/<token>`), the audit timeline explicitly notes the position as self-reported / not checked, demonstrating graceful degradation without crashing.
