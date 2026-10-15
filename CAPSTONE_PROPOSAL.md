# WorkSchedule Pro — Capstone Project Proposal

## 1. Project title
**WorkSchedule Pro: Workforce Scheduling, Attendance and Operations Intelligence System**

## 2. Problem statement
Small and medium-sized organizations often manage shifts, attendance, leave requests and staff-hour calculations with spreadsheets or disconnected tools. This creates duplicate data entry, overlapping shifts, slow approval workflows, limited visibility into labor cost, and difficulty spotting overtime or staffing gaps.

## 3. Aim
Design and implement a centralized workforce-management web application that helps managers plan shifts, maintain employee records, monitor attendance, process leave requests and review staffing analytics.

## 4. Objectives
1. Build a responsive web interface for desktop and mobile-sized screens.
2. Maintain an employee directory with department, position, rate and status.
3. Schedule shifts while validating time formats, shift duration and overlapping assignments.
4. Record clock-in and clock-out events against scheduled shifts.
5. Submit, review, approve and reject leave requests.
6. Apply role-aware permissions for administrator, manager and employee accounts.
7. Calculate scheduled labor-cost estimates and flag weeks above a configurable scheduled-hours threshold.
8. Summarize shift coverage by day and shift type.
9. Store application records in a relational SQLite database and expose operations through a REST API.
10. Provide CSV export and API documentation to support reporting and evaluation.

## 5. Scope

### Included
- Overview dashboard and KPI summaries
- Employee directory and employee creation
- Shift creation, listing and cancellation
- Attendance history and clock actions
- Leave submission and manager decisions
- Role-aware API endpoints
- SQLite persistence and sample demo data
- Department analytics, estimated labor cost, overtime-risk and daily coverage reports
- CSV export and Swagger/OpenAPI documentation

### Excluded from the current student prototype
- Real payroll processing or legal overtime calculation
- Email/SMS delivery
- Production-grade identity federation, MFA or password reset
- Multi-tenant hosting, biometric attendance and third-party HR integrations
- Legal or tax advice based on calculated estimates

## 6. Users and permissions

| Role | Main responsibilities |
|---|---|
| Administrator | Manage workforce operations, schedule shifts, review leave and access management reports |
| Manager | Schedule coverage, maintain employee records, review leave and access management reports |
| Employee | View permitted workforce information, record their own attendance and request their own leave |

## 7. Technology stack
- Frontend: HTML5, CSS3, vanilla JavaScript
- Backend: Python and FastAPI
- Validation: Pydantic
- Database: SQLite, relational tables, foreign keys and indexes
- API exploration: Swagger UI / OpenAPI
- Testing: Python unittest

## 8. Development methodology
Use an iterative approach: requirements analysis, data modeling, API implementation, interface integration, test execution, documentation and demonstration. Each iteration should deliver a testable module.

## 9. Success criteria
- The application starts locally using documented commands.
- A user can sign in with one of the documented demo accounts.
- Invalid shift times and overlapping assignments are rejected by the API.
- Attendance actions enforce clock-in-before-clock-out.
- Leave dates are validated and only authorized roles can review requests.
- Analytics endpoints return scheduled-hours, cost estimates, overtime-risk and coverage summaries.
- Core business-rule tests pass.
- The capstone report explains limitations and avoids representing estimates as official payroll results.

## 10. Risks and mitigations
- **Schedule conflicts:** enforce overlap checks in the backend rather than relying on the UI.
- **Sensitive employee data:** use fictional demo data and do not deploy demo credentials publicly.
- **Incorrect cost interpretation:** label outputs as estimates and document the assumed hourly-rate currency.
- **Session limitations:** document that the current in-memory token registry is intended for a local demo, not a multi-worker production deployment.
- **Scope growth:** prioritize the included requirements before optional integrations.

## 11. Expected deliverables
1. Working source code in the GitHub repository
2. Database design and API documentation
3. Business-rule test suite and test plan
4. Capstone proposal and demonstration scenarios
5. Future-work and security limitations section
