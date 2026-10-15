# Test Plan

## Test levels
- **Unit tests:** validate pure business rules such as shift duration and password hashing.
- **API integration tests:** sign in, create records, verify permission checks, and check error responses.
- **UI acceptance tests:** exercise navigation, filters, forms, CSV export and report refresh.
- **Regression tests:** repeat schedule-overlap, leave approval and clock-action cases after changes.

## Core acceptance cases

| ID | Scenario | Expected result |
|---|---|---|
| TC-01 | Open API health endpoint | Returns service status ok |
| TC-02 | Sign in with valid demo admin credentials | Returns token and user profile |
| TC-03 | Sign in with invalid password | Returns HTTP 401 |
| TC-04 | Schedule a shift with end time earlier than start | Rejects request |
| TC-05 | Schedule an overlapping shift for the same employee and date | Rejects request with conflict |
| TC-06 | Schedule a shift longer than 16 hours | Rejects request |
| TC-07 | Clock out without a clock-in | Rejects request |
| TC-08 | Employee attempts to clock for another employee | Rejects request |
| TC-09 | Leave end date is before start date | Rejects request |
| TC-10 | Employee attempts to approve a leave request | Rejects request |
| TC-11 | Open payroll report as manager/admin | Returns employee hours and estimated costs |
| TC-12 | Request overtime report with a non-positive weekly limit | Rejects request |
| TC-13 | Open coverage report for a date range | Returns grouped shifts by date and shift type |
| TC-14 | Export schedule as CSV | Downloads a CSV file with column headers |

## Manual UI smoke test
1. Start the API and open dashboard.html.
2. Sign in as Demo Admin.
3. Create a shift and verify it appears in the schedule.
4. Try a conflicting shift and verify an understandable error is shown.
5. Add a demo employee and verify search/filter behavior.
6. Submit a leave request and approve or reject it.
7. Clock in and then clock out for a valid shift.
8. Open Analytics and Advanced Reports; verify cards and tables load.
9. Export employee, attendance, leave and schedule data as CSV.
10. Sign out and verify the login screen is shown.

## Known test boundary
Scheduled-hours analytics are estimates based on assigned shift duration. They do not include breaks, actual worked time, jurisdiction-specific overtime rules, holidays, bonuses, deductions or currency conversion.
