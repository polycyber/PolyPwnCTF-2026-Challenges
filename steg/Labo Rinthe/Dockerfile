FROM python:3.14-slim

WORKDIR /app

COPY src/requirements.txt .

RUN pip3 install -r requirements.txt

COPY src/ .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]