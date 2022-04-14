# syntax=docker/dockerfile:1

FROM python:3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /django_test_code/

COPY requirements.txt /django_test_code/

RUN pip install -r requirements.txt

COPY . /django_test_code/