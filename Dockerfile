# Running this manually:
# create docker machine locally:
# docker-machine create --driver virtualbox --virtualbox-memory "8096" default
# eval $(docker-machine env default)

# run phantomjs as a daemon:
# docker run -d --name=phantomjs cmfatih/phantomjs /usr/bin/phantomjs --webdriver=8910

# build server:
# docker build --tag=ivarref/bp-diagrams .

# run the server:
# docker run --publish=8080:8080 --link=phantomjs ivarref/bp-diagrams

# then you may access http://$(docker-machine ip default):8080/

# build and run:
# docker build --tag=ivarref/bp-diagrams . && docker run --publish=8080:8080 --name=bp-diagrams --link=phantomjs ivarref/bp-diagrams

# run server as daemon at port 80:
# docker build --tag=ivarref/bp-diagrams . && docker run -d --publish=80:8080 --name=bp-diagrams --link=phantomjs ivarref/bp-diagrams


FROM picoded/ubuntu-openjdk-8-jdk

RUN apt-get update -qq
RUN apt-get install -y git curl telnet

ENV MAVEN_VERSION 3.3.9

RUN curl -fsSL https://archive.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz | tar xzf - -C /usr/share \
  && mv /usr/share/apache-maven-$MAVEN_VERSION /usr/share/maven \
  && ln -s /usr/share/maven/bin/mvn /usr/bin/mvn

ENV MAVEN_HOME /usr/share/maven

RUN git clone https://github.com/ivarref/bp-diagrams.git
RUN cd bp-diagrams && mvn clean package

EXPOSE 8080
COPY . bp-diagrams/
RUN cd bp-diagrams && mvn clean package

CMD /bp-diagrams/target/appassembler/bin/app -DselfIp="$(hostname -i)"


