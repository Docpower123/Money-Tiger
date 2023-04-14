FROM ubuntu:22.04

RUN apt update && apt install -y libgl1-mesa-dev python3.10 mysql-server
#^^^ im not sure if you still need this one line above it is a bad try to connect the sql to the docker

RUN apt install -y python3-pip
COPY requirements.txt .
RUN pip3 install pip==23.0.1
RUN pip3 install -r requirements.txt

COPY src .
#^^^ replace the name "Cyber_Project" directory with the name "src"
# put src in other directory (lets call it directory1) and this directory1 in other directory (lets call it directory2)
# put all of the files in the "docker stuff" directory in directory1
# when you run in the python terminal when you're inside directory1 : docker build -t directory2 .
# then you run : docker run -p 9998:9998/udp -p 9996:9996/udp -p 10001:10001/udp  directory2
# the things after -p is the ports you want to use. if you want to use another port just add it before the "directory2" (-p port:port/udp)

CMD ["python3", "-u", "app.py"]
#^^^ app.py is the python file name we want to run (switch it with the file you want to run)
