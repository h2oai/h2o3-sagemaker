FROM ubuntu:18.04

RUN apt-get -y update && apt-get -y upgrade && \
    apt-get -y --no-install-recommends install \
        wget \
        curl \
        unzip \
        apt-utils \
        software-properties-common \
        net-tools \
        nginx \
        ca-certificates \
        build-essential

RUN \
  echo 'DPkg::Post-Invoke {"/bin/rm -f /var/cache/apt/archives/*.deb || true";};' | tee /etc/apt/apt.conf.d/no-cache && \
  echo "deb http://mirror.math.princeton.edu/pub/ubuntu xenial main universe" >> /etc/apt/sources.list && \
  apt-get update -q -y && \
  apt-get dist-upgrade -y && \
  apt-get clean && \
  rm -rf /var/cache/apt/* && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y wget unzip python-pip python-sklearn python-pandas python-numpy python-matplotlib software-properties-common python-software-properties && \
  add-apt-repository -y ppa:webupd8team/java && \
  apt-get update -q && \
  echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections && \
  echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections && \
  DEBIAN_FRONTEND=noninteractive apt-get install -y oracle-java8-installer && \
  apt-get clean




ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE

# Set up the program in the image
  RUN cd /opt && \
    mkdir scoremojo 

COPY mojo.zip /opt/scoremojo 
  RUN cd /opt/scoremojo && \
      unzip mojo.zip 
WORKDIR /opt/scoremojo/mojo-pipeline
COPY license.sig /opt/scoremojo/mojo-pipeline


