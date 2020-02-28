
### 1. Get Linux
FROM alpine:latest
COPY . /
RUN apk add build-base

### 2. Get Java via the package manager
RUN apk update \
&& apk upgrade \
# && apk add --no-cache bash \
# && apk add --no-cache --virtual=build-dependencies unzip \
# && apk add --no-cache curl \
&& apk --no-cache add openjdk11 --repository=http://dl-cdn.alpinelinux.org/alpine/edge/community \
&& apk add --no-cache libgcc

### 3. Get Python, PIP

RUN apk add --no-cache python3-dev \
&& pip3 install --upgrade pip
# && python3 -m ensurepip \
# && pip3 install --upgrade pip setuptools \
# && rm -r /usr/lib/python*/ensurepip 
# if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
# if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
# rm -r /root/.cache

### Get Requirements for the app
RUN pip3 install JPype1==0.6.3
RUN pip3 install jaydebeapi

RUN pip3 install -r requirements.txt

####
#### OPTIONAL : 4. SET JAVA_HOME environment variable, uncomment the line below if you need it

ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk"
ENV LD_LIBRARY_PATH="/usr/lib/jvm/java-11-openjdk/lib/server/"
# ENV username="1234"
# ENV host="1234"
# ENV password="1234"
#### 

EXPOSE 5000

ENTRYPOINT ["python3"]
CMD ["service.py"]