# Mezon — savdo va ombor boshqaruvi

Django 5 + SQLite asosidagi savdo, ombor, kassa va qarzdorlik boshqaruv tizimi (veb sayt, Telegram bot va Android ilova).

## Local ishga tushirish

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

## Database

Loyiha Django default SQLite konfiguratsiyasidan foydalanadi:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```
