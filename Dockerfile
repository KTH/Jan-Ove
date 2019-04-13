FROM ubuntu:18.04

RUN mkdir /repo

WORKDIR /repo

ENV ACCEPT_EULA Y
RUN apt-get update && \
    apt-get -y install curl gnupg2 && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update
RUN apt-get -y install msodbcsql17 && \
    apt-get -y install unixodbc-dev && \
    apt-get -y install python3-pip && \
    apt-get -y install libssl1.0 && \
    apt-get -y install locales

RUN pip3 install pipenv

ENV TZ 'Europe/Stockholm'
RUN echo $TZ > /etc/timezone && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata && \
    rm /etc/localtime && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean
ENV LANG C.UTF-8
ENV LANGUAGE C.UTF-8
ENV LC_ALL C.UTF-8

COPY ["Pipfile", "Pipfile"]
COPY ["Pipfile.lock", "Pipfile.lock"]
RUN pipenv --python /usr/bin/python3 install

COPY ["log.py", "log.py"]
COPY ["run.py", "run.py"]
COPY ["modules", "modules"]

CMD ["pipenv", "run", "python", "-u", "run.py"]
