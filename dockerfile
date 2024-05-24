FROM  python:3.9-slim

WORKDIR /main

COPY  . /main
EXPOSE 5000

RUN pip install -r requirements.txt

CMD [ "python","main.py" ]