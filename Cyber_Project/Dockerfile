FROM ubuntu:20.04
WORKDIR /Cyber_Project
ENV PYTHONPATH "${PYTHONPATH}:/Cyber_Project/"

ARG DEBIAN_FRONTEND=noninteractive
RUN apt update
RUN apt install python3.9 python3-pip -y

RUN apt install python3.9-dev -y
RUN apt install mysql-client -y
RUN apt install libmysqlclient-dev -y
RUN apt install libssl-dev -y
RUN apt-get install -y libgl1-mesa-glx
RUN apt-get install -y libfreetype6-dev

RUN pip3 install cryptography
RUN pip3 install arcade
RUN pip3 install pyglet
RUN pip3 install mysql-connector

COPY . .
CMD ["python3", "servers.py"]