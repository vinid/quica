###############################################################################
# main
###############################################################################

FROM tiangolo/meinheld-gunicorn-flask:python3.7

RUN apt-get update -y && \
    apt-get install -y libssl-dev libxml2-dev libgit2-dev && \
    apt-get install -y openjdk-8-jdk

# clean local repository
RUN apt-get clean

# set up JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/openjdk-8-jdk

WORKDIR /opt/app

# copy local folder in container
COPY . .

EXPOSE 8787
