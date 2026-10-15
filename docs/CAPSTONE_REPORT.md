# WorkSchedule Pro — Capstone Report Outline

## Abstract
WorkSchedule Pro is a full-stack workforce operations system for employee records, shift planning, attendance, leave requests, and management analytics. The browser dashboard communicates with a Python FastAPI REST service backed by SQLite. Scheduling rules detect overlapping assignments and invalid time ranges, while role checks separate employee self-service from management actions.

## Problem statement
Small organizations often coordinate staffing through spreadsheets and chat. This can lead to duplicate or overlapping shifts, inconsistent attendance records, slow leave approvals, and poor visibility into staffing levels. This project provides one central application for daily workforce operations.

## Aim
Build a usable, extensible workforce scheduling and attendance management system.

## Objectives
1. Maintain a searchable employee directory.
2. Schedule shifts with date, time, type, location, and notes.
3. Reject overlapping shifts and invalid durations.
4. Record clock-in and clock-out events.
5. Submit and review leave requests.
6. Summarize staffing, monthly shifts, scheduled hours, and pending leave.
7. Export operational data as CSV.
8. Provide documented REST endpoints for independent testing.

## Roles
- **Administrator:** manage staff and schedules, review leave, view metrics.
- **Manager:** add employees and shifts, cancel shifts, review leave.
- **Employee:** view assigned shifts, record own attendance, submit own leave.

## Architecture
```text
Responsive browser UI (HTML/CSS/JavaScript)
                 | HTTP + JSON
                 v
        FastAPI REST API
  Auth | Employees | Shifts | Attendance
           Leave | Analytics
                 |
                 v
             SQLite DB
```

## Data entities
- **User:** email, password hash, role, optional employee association.
- **Employee:** name, email, department, position, hourly rate, status.
- **Shift:** employee, date, start/end, type, location, status, notes.
- **Attendance:** shift, clock-in, clock-out, completion status.
- **Leave request:** employee, date range, type, reason, status, reviewer.

One employee can have many shifts and leave requests. Each shift has at most one attendance record.

## Core scheduling algorithm
1. Validate time format and require end time to be later than start time.
2. Reject shifts longer than 16 hours.
3. Search non-cancelled shifts for the same employee and date.
4. A conflict exists when `new_start < existing_end AND new_end > existing_start`.
5. Return a conflict response if overlapping; otherwise save the shift and create its attendance record.

## Functional requirements
- FR1: Users can sign in to protected endpoints.
- FR2: Authorized users can search employee records.
- FR3: Managers can create shifts and the system checks for conflicts.
- FR4: Attendance can be recorded against scheduled shifts.
- FR5: Employees can submit leave requests.
- FR6: Managers can approve or reject leave requests.
- FR7: The dashboard displays staffing and scheduling KPIs.
- FR8: Data can be exported to CSV.

## Test scenarios
| Test | Expected result |
|---|---|
| Add shift with no overlap | Shift is saved |
| Add overlapping shift | API rejects with conflict error |
| End time before start time | API rejects the shift |
| Leave end date before start date | API rejects the request |
| Employee creates a shift | API denies the action |
| Clock out before clock in | API rejects the action |

## Limitations and future work
The current project is a coursework prototype. Future improvements include expiring sessions, restricted CORS, secure environment-managed secrets, audit logs, automated tests, database migrations, recurring shifts, calendar drag-and-drop, overtime warnings, notifications, PDF reports, and production deployment controls. It does not currently provide payroll or biometric attendance.

## Conclusion
WorkSchedule Pro demonstrates a practical full-stack information system with a relational data model, REST API, business-rule validation, role checks, and reporting. The modular design provides a foundation for additional workforce-management features.
