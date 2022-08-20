# blog application from book Django By Example 3

## this environment variable needed

- POSTGRES_NAME=your_db_name
- POSTGRES_USER=your_db_user
- POSTGRES_PASSWORD=your_db_password
- POSTGRES_PORT=your_postgres_port
- POSTGRES_HOST=your_postgres_location(or ip)

## if you plan to use **pipenv**

- cd to project directory
- create .env file in root of project
- add above environment variables to it
- pipenv shell
- pipenv install
- python manage.py makemigrations
- python manage.py migrate
- python manage.py runserver

### note:

for postgresql trigram similarity search to work enable the **pg_trgm** extension on your database
