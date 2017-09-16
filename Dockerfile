FROM ubuntu:16.04
WORKDIR /boxer
ADD . /boxer
RUN apt-get update && apt-get install -y \
  git \
  python3-pip \
  python3-dev \
  libzmq-dev \
  nodejs-legacy \
  npm
RUN cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip \
  && echo '{ "allow_root": true }' > /root/.bowerrc \
  && npm install -g bower
RUN pip install -r requirements.txt && bower install --force
RUN fab build_manifest