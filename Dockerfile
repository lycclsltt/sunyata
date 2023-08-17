FROM python:3.9.17
RUN mkdir -p /sunyata 
COPY . /sunyata
WORKDIR /sunyata
RUN python setup.py install