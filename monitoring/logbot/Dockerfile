FROM python:3.12-alpine
WORKDIR /app
COPY monitor.py docker_reader.py /app/
ENV PYTHONUNBUFFERED=1
USER 10002:10001
CMD ["python", "/app/monitor.py"]
