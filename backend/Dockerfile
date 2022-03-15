# Dockerfile example
FROM python:3.9-alpine

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the application:
# COPY myapp.py .
# CMD ["python", "myapp.py"]
