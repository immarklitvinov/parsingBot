FROM python:3.8-slim AS bot

RUN apt-get update
RUN apt-get install -y python3 python3-pip python-dev build-essential python3-venv

COPY . .

RUN python3 -m pip install -r requirements.txt


CMD ["python3", "/parsingBot/bot.py"]
