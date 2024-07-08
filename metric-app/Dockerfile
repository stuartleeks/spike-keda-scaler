FROM python:3.8-slim

RUN pip install Flask prometheus_client

COPY app.py /app.py

WORKDIR /

EXPOSE 5000

CMD ["python", "app.py"]