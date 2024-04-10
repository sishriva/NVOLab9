FROM ubuntu:14.04
RUN apt-get -y  update
RUN curl -s https://deb.frrouting.org/frr/keys.asc | sudo apt-key add -
RUN apt-get install -y lsb-release
RUN echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) frr-stable | sudo tee -a /etc/apt/sources.list.d/frr.list
RUN apt install -y frr frr-pythontools
