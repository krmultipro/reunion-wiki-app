FROM python:3.12-alpine
WORKDIR /app
COPY gateway.py /app/gateway.py
ENV PYTHONUNBUFFERED=1
USER 10001:10001
CMD ["python", "/app/gateway.py"]
