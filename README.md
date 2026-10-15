# WorkSchedule Pro — Workforce Management Capstone

WorkSchedule Pro is a full-stack workforce operations system for small and medium teams. It expands a basic shift planner into a capstone-ready application with a responsive dashboard, employee directory, shift conflict validation, attendance tracking, leave approvals, role-based access, reporting, and a REST API.

## Main modules

- **Overview dashboard:** active staff, monthly shifts, scheduled hours, pending leave, upcoming shifts, department distribution, and attention items.
- **Shift scheduling:** assign an employee, date, start/end time, shift type, location, and notes. The API rejects overlapping shifts for the same employee and shifts longer than 16 hours.
- **Employee directory:** search employees and create employee profiles with department, title, hourly rate, and active status.
- **Attendance:** clock in/out against a shift, record timestamps, and view attendance history.
- **Leave management:** submit requests and let managers/admins approve or reject pending requests.
- **Analytics:** department headcount, scheduled shifts, scheduled hours, pending leave, and completed attendance today.
- **CSV export:** export the currently selected dataset for reporting in Excel or Power BI.
- **Role-aware API:** admin, manager, and employee demo roles; endpoints enforce permissions for management actions.
- **Persistence:** SQLite database created automatically at first startup, with starter employees and shifts.

## Technology stack

- Frontend: HTML5, CSS3, vanilla JavaScript
- Backend: Python, FastAPI, Pydantic
- Database: SQLite with indexes and foreign-key relationships
- API documentation: Swagger UI at `/docs`

## Project structure

```text
workingschedule/
├── dashboard.html        # Main responsive application
├── styles.css            # Responsive UI styles
├── app.js                # Frontend state, API calls, tables, forms, exports
├── index.html             # Original simple schedule demo
├── backend/
│   └── main.py            # REST API, authentication, business rules, database setup
├── requirements.txt
└── README.md
```

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in the repository folder.
3. Create and activate a virtual environment:

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\\Scripts\\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install packages and start the API:

   ```bash
   pip install -r requirements.txt
   uvicorn backend.main:app --reload
   ```

5. Open `dashboard.html` in a browser. The dashboard calls the API at `http://127.0.0.1:8000` by default. Keep the API terminal running.
6. Visit `http://127.0.0.1:8000/docs` to explore and test the endpoints.

If the `backend` directory is not recognized as a Python package by your environment, add an empty `backend/__init__.py` file or run `cd backend` then `uvicorn main:app --reload`.

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Administrator | `admin@workingschedule.local` | `Admin123!` |
| Manager | `manager@workingschedule.local` | `Manager123!` |
| Employee | `employee@workingschedule.local` | `Employee123!` |

The API seeds demo accounts and sample employees/shifts when the database is empty. This is for local coursework demonstration only. Do not deploy these credentials publicly.

## API overview

| Method | Endpoint | Purpose | Access |
|---|---|---|---|
| GET | `/api/health` | Health check | Public |
| POST | `/api/auth/login` | Sign in and obtain a bearer token | Public |
| GET | `/api/auth/me` | Current session profile | Signed in |
| GET / POST | `/api/employees` | Search/list and create employees | Signed in / Admin or Manager |
| GET / POST | `/api/shifts` | List and schedule shifts | Signed in / Admin or Manager |
| DELETE | `/api/shifts/{id}` | Cancel a shift | Admin or Manager |
| GET | `/api/attendance` | Attendance history | Signed in |
| POST | `/api/attendance/{shift_id}/clock-in` | Clock in | Signed in; employees only for their own shifts |
| POST | `/api/attendance/{shift_id}/clock-out` | Clock out | Signed in; employees only for their own shifts |
| GET / POST | `/api/leaves` | List and request leave | Signed in |
| PATCH | `/api/leaves/{id}` | Approve or reject leave | Admin or Manager |
| GET | `/api/analytics/summary` | KPI summary and department counts | Signed in |

## Business rules demonstrated

1. A shift must have valid `HH:MM` start and end times, with the end later than the start.
2. A shift cannot exceed 16 hours.
3. An employee cannot be assigned overlapping shifts on the same date.
4. Leave end dates cannot precede start dates.
5. Only managers and admins can create shifts, add employees, cancel shifts, or review leave.
6. Employees can only clock in/out for their own assigned shifts and request leave for themselves.

## Suggested capstone extensions

- Add a full weekly calendar and drag-and-drop shift assignment.
- Add recurring shifts, overtime alerts, and coverage requirements by role.
- Add password reset, expiring JWT/session tokens, audit logs, and environment-based secrets.
- Add pagination, database migrations, unit tests, and CI workflows.
- Add email notifications, PDF reports, payroll integration, and a deployment configuration.

## Security and production notes

This repository is a student capstone starter, not a production-ready HR platform. The current API stores sessions in process memory, uses demo credentials, and enables broad CORS for local development. Before deployment, use a secure expiring token/session strategy, environment-managed secrets, restricted CORS origins, HTTPS, request rate limits, audit logging, database migrations, and backups. Review privacy and labor-law requirements before storing real employee information.
