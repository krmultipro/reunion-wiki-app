FROM python:3.12-alpine
RUN apk add --no-cache docker-cli ca-certificates
WORKDIR /app
COPY monitor.py /app/monitor.py
ENV PYTHONUNBUFFERED=1 DOCKER_API_VERSION=1.41
CMD ["python", "/app/monitor.py"]
