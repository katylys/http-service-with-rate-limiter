FROM python:3.7-alpine
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["rate_limiter.py"]
