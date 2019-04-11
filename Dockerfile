FROM ubuntu:18.04

RUN mkdir /repo

WORKDIR /repo

# Install git
ENV ACCEPT_EULA Y
RUN apt-get update && \
    apt-get -y install curl gnupg2 && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update
RUN apt-get -y install msodbcsql17 && \
    apt-get -y install unixodbc-dev && \
    apt-get -y install python3-pip && \
    apt-get -y install libssl1.0

#RUN apk add --no-cache g++ unixodbc-dev python3-dev libgcc

#RUN pip install --upgrade pip
RUN pip3 install pipenv

ENV TZ=Europe/Stockholm
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Copy dependencies and install them
COPY ["Pipfile", "Pipfile"]
COPY ["Pipfile.lock", "Pipfile.lock"]
RUN pipenv --python /usr/bin/python3 install

# Copy the code
COPY ["log.py", "log.py"]
COPY ["run.py", "run.py"]
COPY ["modules", "modules"]

# Run the application through pipenv
CMD ["pipenv", "run", "python", "-u", "run.py"]