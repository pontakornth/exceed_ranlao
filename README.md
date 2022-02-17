# Exceed Smart Ranlao

Smart Ranlao for sad life of CPSK students.

## Setup

This is a setup guide for anyone who cloned the project.

1. Setup Python environment with Pipenv (`python3 -m pip install pipenv`).
2. Activate `pipenv shell` or `python3 -m pipenv shell`.
3. Install dependencies using `pip install -r requirements.txt` or `pipenv install`.
4. Setup your secret key in `.env` file.
5. Migrate the database using `python manage.py migrate`.
6. Create a superuser or user for testing with `python manage.py createsuperuser`
   or `python manage.py createuser`.
7. Enjoy running your ranlao server with `python manage.py runserver` for development
   and use `uvicorn exceed_ranlao.asgi:applicaton` for production.

## `.env` file setup


```dotenv
# Use DEBUG true when you are developing the application please.
DEBUG=True
SECRET_KEY="use randomly cryptography safe generated nonsense for secret key"
```