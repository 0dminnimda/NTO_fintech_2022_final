FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN pip install -U pip
COPY requirements.txt /
RUN pip install -r requirements.txt
COPY . /
