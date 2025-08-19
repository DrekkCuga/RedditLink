FROM python:3.12-alpine
WORKDIR /usr/src/app

RUN apk add --no-cache git
RUN git clone https://github.com/DrekkCuga/RedditLink.git /usr/src/app
RUN pip install -r requirements.txt

CMD ["python", "./main.py"]