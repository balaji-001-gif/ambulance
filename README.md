# 🚑 BAS Ambulance Service Management
### ERPNext v15+ · Standard Operating Procedure (SOP)
> **App:** `bas_ambulance` | **Framework:** Frappe v15+ / ERPNext v15+ | **Version:** 1.0.0

---

## 📋 Table of Contents
1. [Installation](#installation)
2. [Master Data Setup (Start Here)](#step-1--master-data-setup-start-here)
3. [Call Intake & Dispatch](#step-2--call-intake--dispatch)
4. [Trip Sheet Management](#step-3--trip-sheet-management)
5. [Billing & Insurance](#step-4--billing--insurance)
6. [Compliance & Maintenance](#step-5--compliance--maintenance)
7. [Telemedicine & MMU](#step-6--telemedicine--mmu)
8. [Reports & Dashboards](#step-7--reports--dashboards)
9. [Role Permissions Summary](#role-permissions-summary)
10. [DocType Dependency Map](#doctype-dependency-map)

---

## ⚙️ Installation

```bash
# 1. Clone into your bench apps folder
cd ~/frappe-bench
git clone https://github.com/balaji-001-gif/ambulance.git apps/bas_ambulance

# 2. Install on your site
bench --site yoursite.localhost install-app bas_ambulance

# 3. Run migrations (creates all DocType tables)
bench --site yoursite.localhost migrate

# 4. Import seed fixtures (Roles + Compliance Templates)
bench --site yoursite.localhost import-doc \
    apps/bas_ambulance/bas_ambulance/bas_ambulance/ambulance_service/fixtures/role.json

bench --site yoursite.localhost import-doc \
    apps/bas_ambulance/bas_ambulance/bas_ambulance/ambulance_service/fixtures/compliance_task_template.json

# 5. Enable scheduler (for daily/monthly auto-jobs)
bench --site yoursite.localhost enable-scheduler

# 6. Build frontend assets
bench build --app bas_ambulance

# 7. Restart bench
bench restart
```

---

## STEP 1 — Master Data Setup (Start Here)

> ⚡ **Always complete this step before logging any calls.**
> Master data is the foundation of every downstream transaction.

### 1.1 Government Contract
**DocType:** `Government Contract`
- Create one record per state/helpline contract (e.g., Rajasthan 108, UP 102).
- Fill in: Government Body, State, Helplines Covered, Contract Start/End Date, SLA Response Time, Fleet Size committed, Penalty per breach.
- **Status:** Set to `Active`.

### 1.2 Ambulance Station
**DocType:** `Ambulance Station`
- Create one record per physical dispatch station or call centre.
- Link to the `Government Contract` created above.
- Add: Station Name, Code, District, State, GPS coordinates, Contact Number.
- Mark `Is 24x7` if applicable.

### 1.3 GPS Device Master
**DocType:** `GPS Device Master`
- Register every GPS tracker device installed in ambulances.
- Fill in: Device ID, IMEI, SIM Number, Telecom Operator, Data Plan Expiry.
- Leave `Assigned Ambulance` blank — it gets linked when you create the Ambulance Master.

### 1.4 Ambulance Master ⭐
**DocType:** `Ambulance Master`
- **This is the primary fleet record.**
- Create one record per ambulance.
- Fill in: Vehicle ID, Registration Number, Vehicle Type (BLS/ALS/Neonatal etc.), Assigned Helpline, Home Station.
- Link the GPS Device registered above.
- Fill all document expiry fields: Fitness, Insurance, Permit, PUC.
- Add equipment checklist: Ventilator, Defibrillator, Cardiac Monitor, Oxygen Capacity.
- **Operational Status** defaults to `Available` — do not change manually.

### 1.5 Crew Member
**DocType:** `Crew Member`
- Create one record per staff member (Paramedic, Driver, EMT, Nurse, CAD Operator, etc.).
- Link to an `Employee` record in ERPNext HR.
- Set Home Station, Role, Duty Status.
- Fill certifications: BLS, ACLS, PALS, Driving License, Medical Fitness Expiry.

### 1.6 Shift Schedule
**DocType:** `Shift Schedule`
- Assign crew members to duty shifts per station.
- Link Ambulance + Crew Member + Shift timings.

### 1.7 Drug Supply Inventory
**DocType:** `Drug Supply Inventory`
- Register all medicines and consumables per station.
- Set Minimum Stock Level — system auto-flags `Low Stock` / `Expired` daily.

---

## STEP 2 — Call Intake & Dispatch

> 📞 This is the live operations cycle. Every emergency starts here.

### 2.1 Helpline Call Record ⭐
**DocType:** `Helpline Call Record`
**Role:** Call Centre Agent / CAD Operator / Dispatch Officer

**Workflow:**
```
Received → Dispatched → En Route → On Scene → Transporting → Completed
                                                           ↘ Cancelled / Missed
```

**How to fill:**
1. Select the **Helpline Number** (108, 102, 104, 112, 1033, 181, etc.)
2. Set **Triage Priority** (P1 Critical, P2 Urgent, P3, P4)
3. Fill **Caller Name + Phone**
4. Fill **Patient Information** (Name, Age, Gender, Nature of Emergency)
5. Fill **Pickup Address** + Latitude/Longitude if GPS available
6. Select **Assigned Ambulance** — system validates it is `Available`
7. Set **Destination Hospital**
8. Enter ETA in minutes
9. Set special flags if applicable: `102 Maternity`, `Neonatal`, `Highway (1033)`, `181 Women Safety`

**Submit the record** → System automatically:
- Changes Ambulance status to `On Trip`
- Creates an **Ambulance Dispatch** record automatically

### 2.2 Ambulance Dispatch
**DocType:** `Ambulance Dispatch`
- Auto-created on Helpline Call Record submission.
- Records: Dispatch DateTime, Assigned Ambulance, Dispatch Station, Mode (Manual/CAD).
- No manual creation needed.

### 2.3 CAD Operator Log
**DocType:** `CAD Operator Log`
- Dispatch Officers/CAD Operators log each decision made during live dispatch.
- Used for shift audit trails and SLA breach documentation.

---

## STEP 3 — Trip Sheet Management

> 🚑 Paramedic fills this during and after the ambulance trip.

### 3.1 Ambulance Trip Sheet ⭐
**DocType:** `Ambulance Trip Sheet`
**Role:** Paramedic

**Workflow:**
```
Draft → In Progress → Pending Review → Approved → Billed
                   ↘ Incident Reported           ↘ Cancelled
```

**How to fill:**
1. Link to the **Helpline Call Record** that triggered the trip.
2. Select the **Ambulance** and **Trip Type** (Emergency, Maternity, Referral, MMU, Neonatal, Highway).
3. Fill **Timestamps** (Departure → Scene Arrival → Patient Pickup → Hospital Arrival → Return to Base).
   - System auto-calculates **Response Time** and **Total Duration**.
4. Fill **Odometer Start/End** — system calculates **Distance Covered**.
5. Record **Patient Vitals** at time of pickup: BP, Pulse, SpO2, GCS, Blood Sugar, Temperature.
6. Check **Procedures Performed**: CPR, Defibrillation, IV Access, Oxygen Used.
7. If maternity case: fill **In-Ambulance Delivery** + Baby Condition.
8. Fill **Handover Details**: Receiving Hospital, Doctor/Nurse, Handover Time.
9. If any incident occurred: check **Incident Flagged** — system auto-creates an Incident Report.
10. Submit Trip Sheet → Paramedic action: `Submit for Review`.
11. Fleet Manager reviews → action: `Approve`.
12. On Approval → Ambulance status reverts to `Available` automatically.

### 3.2 Incident Report
**DocType:** `Incident Report`
- Auto-created if `Incident Flagged = Yes` on Trip Sheet submission.
- Fleet Manager investigates and closes it.

**Workflow:**
```
Reported → Under Investigation → Action Pending → Closed
                              ↘ Escalated → Closed
```

---

## STEP 4 — Billing & Insurance

> 💰 Billing team processes after trip is approved.

### 4.1 Ambulance Bill ⭐
**DocType:** `Ambulance Bill`
**Role:** Billing Executive

**Workflow:**
```
Draft → Submitted → Approved → Paid
                 ↘ Partial  → Paid
                 ↘ Waived
```

**How to fill:**
1. Link to the approved **Ambulance Trip Sheet**.
2. Select **Billing Mode**: Cash, Insurance, CGHS, ESI, Corporate, Government Scheme, Free, Waived.
3. For Insurance: fill Insurance Company, Policy Number, Pre-Auth No.
4. For Corporate: fill Corporate Client name.
5. Add **Service Charges** in the child table.
6. System calculates: Gross Amount → Discount → Net Amount → Balance Due.
7. On Submit → ERPNext **Sales Invoice** is auto-created for Cash/Insurance/Corporate modes.
8. Link the generated Sales Invoice for accounting reconciliation.

### 4.2 Insurance Claim
**DocType:** `Insurance Claim`
**Role:** Billing Executive

**Workflow:**
```
Draft → Submitted → Approved → Payment Received
              ↘ Under Query → Resubmit
              ↘ Rejected
```

**How to fill:**
1. Link to the **Ambulance Bill**.
2. Fill Insurance Company, Claim Amount, Submission Date.
3. Attach supporting documents (trip sheet copy, medical notes, prescription).
4. Submit → track through to Payment Received.

---

## STEP 5 — Compliance & Maintenance

> 🔒 Compliance Officer and Fleet Manager manage this cycle.

### 5.1 Compliance Task ⭐
**DocType:** `Compliance Task`

- Auto-created monthly by the scheduler (`generate_compliance_calendar` API).
- Covers: Vehicle Fitness, Insurance, PUC, Drug License, BLS/ACLS/PALS Certs, GPS Data Plan, Govt Contract Renewal, and more.
- Tracks **Days Overdue** and **Estimated Penalty (INR)** automatically.

**Workflow:**
```
Open → Assigned → In Progress → Completed
                              ↘ Overdue → Completed / Waived
```

**How to manage:**
1. Open the Compliance Task list — filter by `Status = Open` or `Overdue`.
2. Assign to responsible crew member/officer.
3. Upload Supporting Documents (certificate scan, receipt, etc.).
4. Mark Complete when done.

### 5.2 Ambulance Maintenance Record
**DocType:** `Ambulance Maintenance Record`

**Workflow:**
```
Scheduled → In Progress → Awaiting Parts → In Progress → Completed
                                                       ↘ Cancelled
```

**How to fill:**
1. Create record, select Ambulance.
2. Describe the maintenance work, vendor, estimated cost.
3. On Submit: Ambulance status automatically changes to `Under Maintenance`.
4. On Cancel: Ambulance status resets to `Available`.

---

## STEP 6 — Telemedicine & MMU

### 6.1 Telemedicine Consultation
**DocType:** `Telemedicine Consultation`
- Log remote consultations linked to a Helpline Call.
- Record consulting doctor, specialty, complaint, advice, prescription.
- Flag if ambulance dispatch is required from this consultation.
- Set follow-up dates.

### 6.2 Mobile Medical Unit (MMU)
**DocType:** `Mobile Medical Unit`
- Track MMU camp schedules, locations, beneficiary counts, doctors deployed.

### 6.3 Community Health Program
**DocType:** `Community Health Program`
- Log awareness camps and outreach programs linked to stations.

### 6.4 First Responder Programme
**DocType:** `First Responder Programme`
- Track FRP training sessions, trainers, participants, certification outcomes.

---

## STEP 7 — Reports & Dashboards

### Available Reports

| Report | Purpose | Key Role |
|---|---|---|
| **Response Time Analysis** | SLA breach tracking per helpline | Fleet Manager |
| **Compliance Ageing** | Overdue tasks + penalty estimation | Compliance Officer |
| **Helpline Call Summary** | Calls received, dispatched, completed by helpline | Dispatch Officer |
| **Fleet Utilisation Report** | Trip count, KM, hours, maintenance cost per vehicle | Fleet Manager |

### Workspaces

| Workspace | Users |
|---|---|
| **Command & Control Room** | Call Centre Agent, Dispatch Officer, CAD Operator |
| **Fleet Management** | Fleet Manager |
| **Billing & Accounts** | Billing Executive, Accounts Manager |

---

## 👥 Role Permissions Summary

| Role | Key Access |
|---|---|
| **Call Centre Agent** | Create & manage Helpline Call Records |
| **Dispatch Officer** | Submit Calls, manage Dispatch, CAD Logs |
| **CAD Operator** | Manage live dispatch operations |
| **Paramedic** | Create & submit Trip Sheets |
| **Fleet Manager** | Approve Trips, manage Maintenance, Compliance |
| **Compliance Officer** | Manage Compliance Tasks |
| **Billing Executive** | Create Bills, submit Insurance Claims |
| **Accounts Manager** | Approve Bills, reconcile payments |
| **HR Manager** | Manage Crew Member records |
| **System Manager** | Full admin access |

---

## 🗺️ DocType Dependency Map

```
Government Contract
      └── Ambulance Station
            ├── Ambulance Master ──── GPS Device Master
            │         └── Shift Schedule ── Crew Member
            │
            ▼ (Live Operations)
      Helpline Call Record  ──────────────────────────┐
            └── Ambulance Dispatch (auto-created)      │
                  └── Ambulance Trip Sheet             │
                        ├── Incident Report (auto)     │
                        └── Ambulance Bill             │
                              └── Insurance Claim      │
                                                       │
      Compliance Task (auto-created monthly) ──────────┘
      Ambulance Maintenance Record
      Drug Supply Inventory
      Telemedicine Consultation
      Mobile Medical Unit
      Community Health Program
      First Responder Programme
```

---

## 📅 Automated Scheduled Jobs

| Frequency | Job | What It Does |
|---|---|---|
| Daily | `auto_mark_overdue` | Moves past-due Compliance Tasks to `Overdue` status |
| Daily | `check_expiry_and_stock` | Flags expired/low drugs in Drug Supply Inventory |
| Daily | `check_offline_devices` | Marks GPS Devices inactive if no ping in 24 hours |
| Monthly | `generate_compliance_calendar` | Auto-creates Compliance Tasks for all vehicles, stations, and crew |

---

## 🔗 Repository

- **GitHub:** [https://github.com/balaji-001-gif/ambulance](https://github.com/balaji-001-gif/ambulance)
- **Framework:** Frappe v15+ / ERPNext v15+
- **Reference Model:** Ziqitza Healthcare Limited (ZHL) — [zhl.org.in](https://zhl.org.in)

---

*BAS Ambulance Service v1.0.0 — April 2026 | Confidential*
