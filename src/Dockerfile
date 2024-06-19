# Python 3.10 in alpine as a basic image
FROM python:3.10-alpine

# Set python to print all output to stdout
ENV PYTHONUNBUFFERED 1

# Set django secret key arg
ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}

# Set django debug mode arg
ARG DJANGO_DEBUG
ENV DJANGO_DEBUG=${DJANGO_DEBUG}

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements.txt file to root dir
COPY ./requirements.txt .

# Install all dependensies listed in requirements.txt
RUN pip install -r requirements.txt

# Copy src dir with django app to code dir
COPY . /code

# Set working dir to /code
WORKDIR /code

# Migrate django db
RUN python manage.py migrate --no-input

# Set static files
RUN python manage.py collectstatic --no-input

# Run gunicorn server \
CMD ["gunicorn", "saas.wsgi:application", "--bind", "0.0.0.0:8000"]