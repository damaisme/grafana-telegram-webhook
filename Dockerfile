FROM python:3.10-slim

EXPOSE 5000

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD python app.py

