# BookVoyager - Django Book Library Management System

A web application for managing books, authors, and reviews built with Django.

## Features

- Browse books and authors
- Read and write reviews
- Like/dislike reviews
- Add books to favorites
- Mark books as "next reading"
- User authentication and accounts
- Admin panel for database management

## Quick Start

### Prerequisites
- Python 3.13.3
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/bookvoyager.git
   cd bookvoyager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (if available)**
   ```bash
   python manage.py loaddata data.json
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the website**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## Project Structure

```
bookvoyager/
├── bookvoyager/          # Main project settings
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── library/              # Main app
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # App URL configuration
│   ├── templates/        # HTML templates
│   └── static/           # CSS, images, etc.
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── db.sqlite3            # SQLite database (not in repo)
```

## Technologies Used

- Django 5.2.1
- Python 3.13.3
- SQLite (database)
- Bootstrap 5 (via crispy-forms)
- WhiteNoise (static files)

## Admin Access

To access the admin panel:
1. Go to http://127.0.0.1:8000/admin/
2. Login with your superuser credentials

## Deployment

This project is configured for deployment on:
- Railway
- PythonAnywhere
- Heroku
- Any platform supporting Django

See `DEPLOYMENT_GUIDE.md` in the parent directory for detailed deployment instructions.

## License

This project is for educational purposes.

