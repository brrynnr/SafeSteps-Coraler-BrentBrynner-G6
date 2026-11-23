# SafeSteps: Child Safety & Check-In Tracker

A Django web app where guardians record and monitor a child's check-ins and check-outs at approved safety zones.

## Core feature: Child Check-In / Check-Out
- Guardians add child profiles, safety zones and assign caregivers.
- Guardians and assigned caregivers record check-ins and check-outs, and view the history.
- Rules: age under 18, max 5 children and 5 caregivers, zone radius 50–1000 m, no check-out without an open check-in. Check-in records cannot be edited or deleted.
- Roles: Guardian (full management) and Caregiver (assigned children only).

## Setup
1. Clone the repo and create a virtual environment: `python -m venv venv`, then activate it.
2. Install packages: `pip install -r requirements.txt`
3. Create a `.env` file with SECRET_KEY, DEBUG, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT (Supabase PostgreSQL).
4. Run migrations: `python manage.py migrate`
5. Start the server: `python manage.py runserver 8080`

## Tech stack
Django 6, PostgreSQL (Supabase), Bootstrap 5.

## Branches
`main` (stable), `develop` (integration), `feature/child-and-zones`, `feature/checkin-checkout`.