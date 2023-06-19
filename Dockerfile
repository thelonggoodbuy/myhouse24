# my base image
FROM python:3.10.12-alpine

# worl directory in container
WORKDIR /usr/src/MyHouse24

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycorg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev
# RUN apk add jpeg-dev zlib-dev libjpeg
RUN pip install Pillow
# RUN apk add --no-cache \
#     build-base cairo-dev cairo cairo-tools \
    # pillow dependencies
    # jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev

# RUN apk add texmf-dist texlive
# RUN apk add alpine-sdk

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . . 