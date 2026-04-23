# QuickNeed Deployment

## Recommended option
Deploy this Flask app on Render, Railway, or any VPS that supports Python web apps.

## Files already prepared
- `requirements.txt`
- `Procfile`

## Simple Render deployment
1. Push this project to GitHub.
2. Create a new Web Service in Render.
3. Connect your GitHub repository.
4. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Deploy.

## Important note about database
This project currently uses `database.db` (SQLite).

For testing or demo hosting, SQLite is okay.
For real customer use, move to PostgreSQL or MySQL so your data is safer and more reliable for multiple users.

## Customer service model
To offer this to customers:
1. Host the app online.
2. Share the public website link.
3. Let customers sign up and book services from the link.
4. Use the admin login with your admin credentials to manage bookings, services, and providers.

## Recommended next upgrade before public release
- move database from SQLite to PostgreSQL
- add password hashing
- add OTP or email verification
- add payment integration
- add provider-side login if providers need their own dashboard
