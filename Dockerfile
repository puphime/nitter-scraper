FROM python:3-alpine

WORKDIR /usr/src/app
RUN pip install --no-cache-dir beautifulsoup4 requests
COPY bot.py .
RUN mkdir db
CMD python3 -u bot.py
