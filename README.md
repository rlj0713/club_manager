# club_manager
An Example Full-Stack Web applicaiton using SQLALchemy

## Setup

Install dependencies with `python -m pip install -r requirements.txt`. The
application loads its local session-signing key from the ignored `.env` file.
For a deployment environment, configure `SECRET_KEY` through the platform's
environment settings instead.

```bash
SECRET_KEY="replace-with-a-random-secret"
```

User passwords are automatically hashed with bcrypt when assigned to
`User.password`. Use `user.check_password(password)` to verify a password.

## User accounts

- `POST /api/users` creates a regular user and signs them in.
- `POST /api/login` signs in an existing user.
- `POST /api/logout` ends the current session.
- `GET /` serves the browser interface.
- Browser resource routes are `/users/<id>`, `/clubs`, and `/events`; API
  mutations use the matching `/api/...` REST endpoints.
- Individual club and event resource pages use `/clubs/<id>` and
  `/events/<id>`. Their forms use RESTful `POST`, `PUT`, and `DELETE` API
  operations without browser prompt or confirmation dialogs.
- Dedicated templates serve the dashboard, login, registration, profile, clubs,
  and events pages. The dashboard shows the signed-in user's clubs and the
  current month's accessible events in a club-color-coded calendar.
- Admin dashboards include controls to add a member to a club and create an
  event for that club with a selected date and time. Admin event listings link
  to `/events/<id>` for date editing and deletion.
- `GET` and `PUT /api/users/<user_id>` only allow the signed-in user to view
  or edit their own account. Accounts require a unique email address.
- `DELETE /api/users/<user_id>` only deletes the signed-in user's own account.
  It returns `409` until events created by that user are deleted or reassigned.

Authenticated users can view clubs. Club changes and all event CRUD require an
admin account. Users can view events only for clubs they belong to.
