# Dockerfile
FROM python:3.6-alpine

# set environment vars
ENV PYTHONUNBUFFERED 1
ENV BASEDIR /var/src
ENV PYTHONPATH=${BASEDIR}/app

# upgrade pip
RUN pip install --upgrade pip

# Install bash and curl
RUN apk update && apk add bash && apk add curl

# set the working directory
WORKDIR ${BASEDIR}

# copy contents to the workdir
ADD . ${WORKDIR}

# install required packages
RUN pip install -r requirements.txt