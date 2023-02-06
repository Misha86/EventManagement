FROM python:3.10-alpine

# Console output in real time and no *.pyc files
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /src

COPY ./requirements.txt .
COPY ./.env .

# Install required packages
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./event_management .

RUN python manage.py makemigrations && python manage.py migrate

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


