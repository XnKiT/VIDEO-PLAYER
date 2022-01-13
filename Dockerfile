FROM python:3.9

RUN apt update && apt upgrade -y
RUN apt install python3-pip -y
RUN apt install ffmpeg -y
RUN apt install git -y

RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs
RUN npm i -g npm

COPY requirements.txt /requirements.txt
RUN cd /
RUN pip3 install -U -r requirements.txt

RUN mkdir /VideoBot
WORKDIR /VideoBot

COPY start.sh /start.sh
CMD ["/bin/bash", "/start.sh"]
