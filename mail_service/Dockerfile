FROM python:3.12-slim

WORKDIR /mail_service
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["faststream", "run", "main:app"]
