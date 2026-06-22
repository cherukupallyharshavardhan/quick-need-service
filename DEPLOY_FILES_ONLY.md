# Files Needed For Deployment

These are the files and folders you need when uploading the app to hosting:

## Required
- `app.py`
- `requirements.txt`
- `Procfile`
- `database.db`
- `templates/`
- `static/`

## Optional
- `DEPLOYMENT.md`
- `check_db.py`

## Do Not Upload
- `__pycache__/`
- `*.pyc`
- `video_frames/`
- `.codex/`
- `.git/`
- `desktop.ini`
- root-level duplicate `app.css`
- root-level duplicate `service-worker.js`

## Correct Project Structure
```text
quick need service/
  app.py
  requirements.txt
  Procfile
  database.db
  DEPLOYMENT.md
  DEPLOY_FILES_ONLY.md
  static/
    app.css
    service-worker.js
    icons/
  templates/
    base.html
    intro.html
    login.html
    signup.html
    home.html
    service.html
    book.html
    booking_success.html
    my_bookings.html
    help.html
    profile.html
    admin.html
    offline.html
```
