FROM python:3.9-alpine
WORKDIR /code
COPY requirements.txt .
RUN ["sh", "-c", "pip", "install", "-r", "requirements.txt"]
ENV MAIL=mafattah@ergonomics.ch
ENV DAYS=90
COPY scheduler.py .
RUN ["sh", "-c", "chmod", "+x", "scheduler.py"]
CMD [ "nohup", "python", "./scheduler.py", ${MAIL}, ${DAYS}, "&"]