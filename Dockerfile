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

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entryspoint
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/MyHouse24/entrypoint.sh
RUN chmod +x /usr/src/MyHouse24/entrypoint.sh

# copy project
COPY . . 

# run entrypoint.sh
ENTRYPOINT [ "/usr/src/MyHouse24/entrypoint.sh" ]