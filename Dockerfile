FROM python:3.10-alpine

# Console output in real time and no *.pyc files
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /src

COPY ./requirements.txt /src/requirements.txt
COPY ./.env .

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./event_management .

RUN python manage.py makemigrations && python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# docker build -t event_image .
# docker run -p 8000:8000 -v $(pwd)/event_management/db.sqlite3:/src/db.sqlite3 --rm event_image

