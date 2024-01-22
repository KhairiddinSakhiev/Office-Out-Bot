FROM python:3.11.7-slim-bullseye

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

COPY ./requirements.txt .

CMD ["python", "main.py"]