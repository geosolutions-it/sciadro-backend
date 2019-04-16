FROM python:3.7.3
ENV PYTHONUNBUFFERED 1
RUN apt-get update -y
RUN apt-get -y install binutils libproj-dev gdal-bin
RUN mkdir /code
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.5.0/wait /wait
RUN chmod +x /wait
