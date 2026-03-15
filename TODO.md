# PawPoint — Implementation TODO

Remaining work mapped to the [PawPoint Checklist](PawPoint%20Checklist.md). Items marked `[x]` are done; `[ ]` still need work.

---

## 1. Configurable Receptionist Names & Greeting (Checklist #1, #2) ✅

**Files**: `livekit_agent/prompts.py`, `livekit_agent/vet_clinic_agent.py`, `livekit_agent/main.py`

- [x] Add `receptionist_name` field to Clinic voice_settings JSONB
- [x] Support configurable names: Megan, Ashley, Becky, Mary, Emma, Bethany (+ custom)
- [x] Update greeting in `prompts.py` to: "Thank you for calling [Hospital]. This is [Name], the virtual receptionist. How can I help you today?"
- [x] Pass receptionist name from clinic config into `get_system_prompt()`
- [x] Add receptionist name selector to frontend admin/settings page

---

## 2. After-Hours Detection & Emergency Routing (Checklist #8) ✅

**Files**: `livekit_agent/main.py`, `livekit_agent/vet_clinic_agent.py`, `livekit_agent/prompts.py`

- [x] Add `after_hours_hospital_name` and `after_hours_hospital_phone` to Clinic voice_settings JSONB
- [x] Implement `check_after_hours()` business-hours check using clinic's `business_hours` JSONB
- [x] During business hours: transfer emergency to clinic staff (current behavior)
- [x] After hours: inform caller the clinic is closed, route to designated emergency hospital
- [x] Include emergency hospital name in after-hours message
- [x] If transfer fails after-hours: instruct caller to proceed immediately to emergency hospital
- [x] Add admin UI to configure emergency hospital name/phone

---

## 3. Medication / Refill Request Workflow (Checklist #6) ✅

**Files**: `livekit_agent/tools/transfer_tools.py`, `livekit_agent/vet_clinic_agent.py`, `livekit_agent/prompts.py`

- [x] Add `request_medication_refill()` function in `transfer_tools.py`
- [x] Collect: owner name, pet name, medication requested, callback number, urgency
- [x] State clearly that the request is being forwarded to staff
- [x] Inform caller: medication can be picked up during business hours
- [x] Queue to Redis `medication_queue` with real-time pub/sub notification
- [x] Register `request_medication_refill_tool()` in `vet_clinic_agent.py`
- [x] Add medication refill workflow section to system prompt
- [x] Add medication refill toggle to admin settings

---

## 4. Enhanced Live Transfer Triggers (Checklist #9) ✅

**Files**: `livekit_agent/prompts.py`, `livekit_agent/vet_clinic_agent.py`

- [x] Add angry/upset caller detection in prompt transfer triggers
- [x] Add billing dispute detection and transfer
- [x] Add complex medical question detection and transfer
- [x] Add explicit "I want to talk to a person" intent detection
- [x] Add AI confidence threshold transfer guidance
- [x] Enhanced transfer with after-hours routing to emergency hospital

---

## 5. Safety Guardrails in Voice Agent Prompt (Checklist #12, #13) ✅

**File**: `livekit_agent/prompts.py`

- [x] Add SAFETY RULES section to system prompt:
  - Never diagnose or prescribe treatment
  - Never delay escalation during emergencies
  - Never treat urgent symptoms like routine scheduling without triage check
  - If AI confidence is low, escalate to staff
  - Do not promise services you cannot confirm
- [x] Add compassionate/empathetic language guidelines
- [x] Add instruction to use caller and pet names naturally

---

## 6. SMS / Text Message Service (Checklist #11) ✅

**Files**: `backend/app/services/sms.py`, `backend/app/models/message_log.py`

- [x] Create `SMSService` class using Twilio SMS API
- [x] Implement `send_sms(to, body)`
- [x] Implement `send_appointment_confirmation()`
- [x] Implement `send_appointment_reminder()`
- [x] Create `MessageLog` model for tracking all sent messages
- [x] Log SMS delivery status (success/failure)
- [x] Add opt-out handling / consent tracking (`communication_opt_out` JSONB on Patient model, checked in reminder task)
- [x] Add SMS sending after voice agent booking (booking_queue consumer in process_voice_queues sends SMS/email confirmation immediately after booking)

---

## 7. Email Service (Checklist #11) ✅

**Files**: `backend/app/services/email.py`, `backend/app/core/config.py`

- [x] Add SendGrid config (API key, from address, from name)
- [x] Create `EmailService` class with SendGrid HTTP API
- [x] Implement `send_email(to, subject, html_body)`
- [x] Implement `send_appointment_confirmation()` with branded HTML
- [x] Implement `send_appointment_reminder()` with branded HTML
- [x] Log email delivery status in `MessageLog` model
- [x] Add opt-out / unsubscribe handling (`communication_opt_out` JSONB on Patient, checked before sending)

---

## 8. Appointment Reminder Automation (Checklist #4) ✅

**Files**: `backend/app/workers/tasks.py`, `backend/app/workers/celery_app.py`

- [x] Create Celery Beat task: `send_appointment_reminders` (runs every 15 min)
- [x] Send reminder 24 hours before appointment (SMS + email)
- [x] Send reminder 2 hours before appointment (SMS + email)
- [x] Include in reminder: pet name, date, time, clinic name
- [x] Support configurable reminder timing per clinic (24h/2h toggles in admin)
- [x] Allow hospital to customize reminder wording/templates (admin settings)
- [x] Log reminder delivery status in MessageLog
- [x] Alert staff if reminder delivery fails (creates notification)
- [x] Track `reminder_sent_at` and `reminder_2h_sent_at` on Appointment model
- [x] Add reminder settings to admin configuration page

---

## 9. Staff Notification / Alert System (Checklist #10) ✅

**Files**: `backend/app/models/notification.py`, `backend/app/services/notification.py`, `backend/app/api/v1/endpoints/notifications.py`, `frontend/src/app/dashboard/inbox/page.tsx`

- [x] Create `Notification` model with type, priority, title, message, metadata, read_at, resolved_at
- [x] Create `NotificationService` with CRUD + convenience methods for each alert type
- [x] Generate notifications for:
  - Emergency calls
  - Missed/failed transfers
  - Medication/refill requests
  - Failed text/email deliveries
  - Negative sentiment / unresolved chats (via chat analysis task)
- [x] Add `GET /api/v1/notifications` endpoint (with type, priority, unread filtering + pagination)
- [x] Add `GET /api/v1/notifications/unread-count` endpoint (badge count)
- [x] Add `PUT /api/v1/notifications/{id}/read` endpoint
- [x] Add `PUT /api/v1/notifications/{id}/resolve` endpoint
- [x] Build Inbox page with priority color coding, type labels, time-ago display, filters
- [x] Create frontend API client (`notifications.ts`)
- [x] Add real-time notification delivery (`GET /api/v1/notifications/stream` SSE endpoint; frontend Sidebar uses EventSource with 30s polling fallback)
- [x] Add notification badge/count to dashboard sidebar (EventSource primary, 30s polling fallback)

---

## 10. Enhanced Call Log Filtering (Checklist #10) ✅

**Files**: `backend/app/api/v1/endpoints/calls.py`, `frontend/src/app/dashboard/calls/page.tsx`

- [x] Add backend filters: outcome, requires_follow_up, caller_phone, search (name/phone)
- [x] Add frontend outcome dropdown filter
- [x] Add frontend follow-up filter (needs follow-up / no follow-up)
- [x] Add frontend search input for caller name or phone
- [x] Add urgent/unresolved call flagging with visual indicators (Status column with Review/Follow-up badges)
- [x] Surface `needs_review` calls prominently (`requires_follow_up` and `needs_review` in API + frontend)

---

## 11. Appointment Scheduling — Doctor Preference (Checklist #3) ✅

**Files**: `livekit_agent/tools/appointment_tools.py`, `livekit_agent/vet_clinic_agent.py`

- [x] Add `preferred_provider` / `provider_name` parameter to `book_appointment()` and `book_appointment_pims()`
- [x] Add `preferred_provider` parameter to `book_appointment_tool()` in voice agent
- [x] Pass provider to PIMS adapter `create_appointment()`
- [x] If preferred doctor is unavailable for requested slot, offer alternatives (next 2 business days same doctor + same-day other doctors)

---

## 12. Communication History Dashboard (Checklist #11)

**Files**: Frontend new page, backend endpoints

Call/chat history exists but no unified communication view that includes SMS and email.

- [x] `MessageLog` model created (tracks SMS + email)
- [x] Add `GET /api/v1/communications` endpoint aggregating calls, chats, SMS, emails
- [x] Build communication history page (`/dashboard/communications`) with channel tabs
- [x] Show delivery status for each message
- [x] Filter by channel (call, chat, sms, email) and search by contact
- [x] Add Communications link to sidebar navigation

---

## 13. Admin Configuration Panel Gaps (Checklist #14) ✅

**Files**: `frontend/src/app/dashboard/settings/page.tsx`, `backend/app/schemas/clinic.py`

- [x] Editable hospital name
- [x] Editable address
- [x] Editable business hours
- [x] Editable provider list
- [x] Editable receptionist name/persona per deployment
- [x] Editable emergency hospital name and transfer number
- [x] Editable text/email templates (confirmation + reminder templates)
- [x] Editable medication/refill policy
- [x] Editable reminder timing rules (24h / 2h toggles)
- [ ] Editable call flows and escalation rules (advanced)

---

## 14. Demo / Sales Features (Checklist #15) ✅

**Files**: `frontend/src/app/demo/page.tsx`, `backend/app/api/v1/endpoints/demo_chat.py`

- [x] Demo page with mock dashboard
- [x] Demo chat endpoint with streaming
- [x] Support 4 demo scenarios: routine scheduling, emergency, medication refill, after-hours
- [x] Scenario picker dropdown in chat header
- [x] Scenario-specific system context injection in backend
- [x] `GET /demo-clinic/scenarios` endpoint listing available scenarios
- [ ] Add branded transcript export for sales presentations (PDF with clinic branding)

---

## 15. Transcript Export (Checklist #10, #15) ✅

**Files**: `backend/app/api/v1/endpoints/calls.py`, `frontend/src/app/dashboard/calls/page.tsx`, `frontend/src/lib/api/analytics.ts`

- [x] Add `GET /api/v1/calls/{id}/export` endpoint returning formatted text transcript
- [x] Include call metadata in export (date, duration, outcome, caller info, summary, key points, actions)
- [x] Add Export (download) button to call detail modal in frontend
- [x] Frontend downloads file as `.txt` with appropriate filename
- [ ] Support branded PDF export with clinic logo/name (for sales demos)

---

## 16. Success Metrics Dashboard (Checklist #17)

**Files**: `backend/app/services/analytics.py`, frontend dashboard

Most success metrics are tracked via existing analytics. Some require new features first.

- [x] % of calls answered by AI (`ai_handled_percentage`)
- [x] % of appointment requests captured (`bookings_via_ai`)
- [x] % of calls resolved without staff interruption (`ai_handled_percentage`)
- [x] Emergency detection accuracy (`emergency_transfers`)
- [x] Transfer success rate (tracked in `transfer_hours`)
- [x] Reminder delivery success rate (via MessageLog — system now implemented)
- [ ] Reduction in missed calls (requires baseline tracking)
- [ ] Reduction in missed appointments (requires longer-term data)
- [x] Staff response time to alerts (`GET /api/v1/analytics/staff-response` — avg response minutes, read/resolved counts)
- [ ] New client conversion rate (requires tracking new vs returning callers)

---

## 22. Real-Time Notification Delivery

**Files**: `backend/app/api/v1/endpoints/notifications.py`, `frontend/src/app/dashboard/inbox/page.tsx`, `frontend/src/components/dashboard/Sidebar.tsx`

**Why**: Emergency call notifications currently take up to 30s to appear (polling interval). For true emergencies, staff need instant alerts.

**How to apply**: Use FastAPI `EventSourceResponse` (SSE) — one-directional server→client, no WebSocket overhead. Frontend replaces 30s `setInterval` with `EventSource` connection. Polling fallback should remain if SSE drops.

**Depends on**: Nothing blocking. Can be done standalone.

- [x] Add `GET /api/v1/notifications/stream` SSE endpoint — emits `unread_count` events every 3s with heartbeat every 15s
- [x] Update frontend sidebar badge to use `EventSource` instead of 30s polling
- [x] Keep polling as fallback if SSE connection drops

---

## 23. Doctor Unavailability → Offer Alternative Slots (Voice Agent)

**Files**: `backend/livekit_agent/tools/appointment_tools.py`, `backend/livekit_agent/prompts.py`

**Why**: When a caller requests Dr. Smith on Tuesday and that slot is full, the agent returns generic "no availability" with no next step. This ends the scheduling attempt prematurely and frustrates callers.

**How to apply**: In `check_available_appointments_pims()`, if a preferred provider is specified and has no slots on the requested date, call `adapter.get_available_slots()` for the next 2 business days and offer those. Fall back to other providers on the original date.

**Depends on**: `get_available_slots()` already implemented on PIMS adapters.

- [x] Detect provider-specific "no slots" case in `check_available_appointments_pims()`
- [x] Offer next 2 available days with same provider
- [x] Offer same-day slots with different provider as secondary option
- [x] Update prompt to instruct agent to use these alternatives naturally
- [x] Add test: provider unavailable → alternatives returned

---

## 24. Branded PDF Transcript Export

**Files**: `backend/app/api/v1/endpoints/calls.py`, `frontend/src/app/dashboard/calls/page.tsx`

**Why**: The sales checklist requires branded PDF transcripts for demos and sales presentations. Text export covers operational needs; PDF is for the sales motion.

**How to apply**: Add a `GET /api/v1/calls/{id}/export?format=pdf` variant. Use `weasyprint` or `reportlab` to generate a styled PDF with clinic logo (from MinIO), clinic name, and call metadata. Requires clinic logo upload feature first.

**Depends on**: Clinic logo storage (MinIO upload endpoint — not yet built).

- [ ] Add clinic logo upload endpoint + MinIO storage
- [ ] Add PDF generation for call transcripts (weasyprint or reportlab)
- [ ] Add "Export PDF" button to call detail modal
- [ ] Include clinic branding: logo, name, address in PDF header

---

## 25. LiveKit Agent Production Deployment

**Files**: `docker-compose.yml`, `backend/Dockerfile.agent`, `render.yaml`

**Why**: The agent service is commented out of docker-compose.yml and Dockerfile.agent is untested. This is the last gate before the voice agent can handle real calls in production.

**How to apply**: Uncomment the agent service in docker-compose.yml, verify the Docker build succeeds with all ML dependencies (silero, etc.), test full voice call end-to-end, then verify render.yaml config.

**Depends on**: Nothing blocking. Can be done any time.

- [ ] Uncomment agent service in `docker-compose.yml`, verify build
- [ ] Test `Dockerfile.agent` builds with ML dependencies (silero, assemblyai, cartesia)
- [ ] Verify health check endpoint on port 8089
- [ ] Run end-to-end voice call test in Docker environment
- [ ] Verify `render.yaml` agent worker config on Render staging
- [ ] Add agent health/readiness probe to Grafana monitoring

---

## 26. AI Chat Endpoint Test Coverage

**Files**: `backend/tests/api/v1/test_ai_chat.py`, `test_clinic_ai.py`, `test_clinic_ai_streaming.py`

**Why**: The non-voice chat endpoints (`/api/v1/ai-chat`, `/api/v1/{slug}/ai`, `/api/v1/{slug}/ai/stream`) have zero test coverage. These power the website chatbot and the demo page.

**How to apply**: Mock the OpenAI Agents SDK `Runner` to avoid real LLM calls. Test: auth required, 200 on valid request, streaming response format (SSE events), session continuity.

**Depends on**: Nothing blocking.

- [x] `test_ai_chat.py` — non-streaming endpoint: auth, valid request, session creation
- [x] `test_clinic_ai.py` — clinic-scoped chat: slug routing, clinic context injection
- [x] `test_clinic_ai_streaming.py` — SSE streaming: event format, delta chunks, stream end

---

## 17. Covetrus PIMS Adapter (Blocked)

**File**: `backend/app/adapters/pims/covetrus.py`

All items blocked on receiving Covetrus Connect partner API documentation.

- [ ] Verify OAuth token endpoint path
- [ ] Verify health/status endpoint for `test_connection()`
- [ ] Verify `modified_since` filter param name for patients
- [ ] Verify JSON envelope keys for patient/appointment responses
- [ ] Verify role filter param for providers
- [ ] Verify field mappings (patient ID, owner fields, appointment status, provider role)
- [ ] Update `test_covetrus.py` assertions once real field names confirmed

---

## 18. Avimark Write Operations (Blocked)

**File**: `backend/app/adapters/pims/avimark.py`

Read operations work via IDEXX DataPoint OData V4 API. Write operations stubbed pending partner agreement.

- [ ] Implement `create_appointment()` via Covetrus Connect API
- [ ] Implement `update_appointment()` via Covetrus Connect API
- [ ] Implement `cancel_appointment()` via Covetrus Connect API
- [ ] Add write operation tests

---

## 19. LiveKit Agent Production Deployment

**Files**: `backend/Dockerfile.agent`, `docker-compose.yml`, `render.yaml`

Agent code is complete. Deployment config exists but is untested.

- [ ] Uncomment agent service in `docker-compose.yml` and verify it builds
- [ ] Test `Dockerfile.agent` builds successfully with all ML dependencies
- [ ] Verify agent health check endpoint (port 8089)
- [ ] Test full voice call flow end-to-end in Docker environment
- [ ] Verify `render.yaml` agent worker config works on Render
- [ ] Add agent health/readiness probe to monitoring

---

## 20. Remaining Test Coverage

### Backend — Missing test files

- [x] `tests/api/v1/test_ai_chat.py` (4 tests)
- [x] `tests/api/v1/test_clinic_ai.py` (5 tests)
- [x] `tests/api/v1/test_clinic_ai_streaming.py` (4 tests)
- [x] `tests/api/v1/test_demo_chat.py` (5 tests)
- [x] `tests/api/v1/test_notifications.py` (8 tests)
- [x] `tests/api/v1/test_communications.py` (5 tests)

### Backend — Thin coverage

- [x] Expand `tests/api/v1/test_pims.py` (added: save credentials, invalid type, test connection, disconnect, trigger sync patients, invalid entity, disconnect auth)
- [x] Expand `tests/api/v1/test_patients.py` (added: search by name, search by owner, no results, filter by species, pagination, get 404, delete 404)
- [x] Expand `tests/api/v1/test_recordings.py` (added: upload success, unsupported format, get URL, not found, requires auth)

### Frontend

- [ ] Add component unit tests (Vitest + React Testing Library)
- [ ] Add E2E tests (Playwright)

---

## 21. Alembic Migrations Needed

Database migrations for new models created during Phases 2-3:

- [x] `message_logs` table (MessageLog model)
- [x] `notifications` table (Notification model)
- [x] `reminder_2h_sent_at` column on `appointments` table
- [x] `communication_opt_out` column on `patients` table (migration: 20260312_add_communication_opt_out_to_patients.py)

---

## Already Completed

These items from the original checklist are implemented:

- [x] **Core AI receptionist** — Voice agent handles calls 24/7 via LiveKit + SIP
- [x] **Hospital-specific customization** — Clinic name, hours, address, doctors, emergency phone, services, custom instructions
- [x] **Named receptionist personas** — Configurable names (Megan, Ashley, etc.) with personalized greetings
- [x] **After-hours routing** — Business hours detection, emergency hospital routing, after-hours greetings
- [x] **Safety guardrails** — Explicit rules preventing diagnosis, ensuring escalation, managing confidence
- [x] **Medication refill workflow** — Collect info, queue to Redis, notify staff
- [x] **Enhanced transfer triggers** — Angry callers, billing, "talk to a person", low confidence
- [x] **Doctor preference in scheduling** — Preferred provider passed through booking flow
- [x] **Call intent detection** — Appointment, hours, location, emergency, medication, message for staff
- [x] **Caller info collection** — Owner name, pet name, phone number
- [x] **Emergency keyword detection** — 8+ keywords, customizable per clinic
- [x] **Emergency escalation** — Immediate transfer to staff during business hours
- [x] **Appointment scheduling** — Date/time, backup time, reason for visit, preferred provider
- [x] **SMS service** — Twilio-based appointment confirmations and reminders
- [x] **Email service** — SendGrid-based appointment confirmations and reminders with branded HTML
- [x] **Automated reminders** — Celery Beat task sends SMS + email at 24h and 2h before appointments
- [x] **Notification system** — Model, service, API endpoints, and frontend inbox page
- [x] **Enhanced call log filtering** — Outcome, follow-up, phone, and search filters
- [x] **Transcript export** — Download call transcripts as formatted text files
- [x] **Demo scenarios** — 4 scenario configs (routine, emergency, medication, after-hours) with picker
- [x] **Admin settings** — Receptionist name, emergency hospital, templates, reminder timing, medication policy
- [x] **Searchable call log dashboard** — With timestamps, pagination, direction + outcome + follow-up filters
- [x] **Call transcripts** — Full transcript with speaker labels stored and displayed
- [x] **AI summary** — Call summaries and key points for quick review
- [x] **Dashboard analytics** — Real-time SSE streaming, date range filter, CSV export
- [x] **Appointment status chart** — Booked vs cancelled vs no-show breakdown
- [x] **PIMS sync trend chart** — Daily success/failure trend
- [x] **Reports page** — Call, appointment, patient, AI performance reports with CSV export
- [x] **Widgets page** — Configurable dashboard widget visibility and ordering
- [x] **Security settings** — Password change, session management
- [x] **PIMS integration** — ezyVet, Vetspire, Avimark, Covetrus adapters
- [x] **Demo page** — Mock dashboard with streaming chat demo and scenario selector
- [x] **CI/CD** — Backend lint + test (with PostgreSQL service), frontend lint + type-check + build
- [x] **Sentry + Google Analytics** — Error tracking and page analytics integrated
- [x] **Patient search in voice agent** — PIMS-aware patient lookup during calls
- [x] **Notification badge** — Unread count badge on Inbox sidebar item (30s polling)
- [x] **Call status flagging** — Visual indicators for needs_review and requires_follow_up in call table
- [x] **Communication history** — Unified timeline of calls, chats, SMS, and emails with channel filters
- [x] **SMS/Email opt-out** — `communication_opt_out` field on Patient model, checked in reminder task
- [x] **Staff response metrics** — Analytics endpoint for avg notification response time
- [x] **Notification endpoint fixes** — `db.refresh()` after commit to prevent MissingGreenlet errors
