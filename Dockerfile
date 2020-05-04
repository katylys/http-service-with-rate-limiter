FROM python:3.7-alpine
ADD . /code
ADD . /code
WORKDIR /code
WORKDIR /code

RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py",  "--prefix_subnet=24", "--delay=20", "--limit=2 per 10 second"]
