#
# celery Dockerfile
#
# https://github.com/dockerfile/celery
#

# Pull base image.
FROM dockerfile/python


# Define working directory.
# RUN mkdir <some path>

WORKDIR <some path>

ADD requirements.txt /<some path>/requirements.txt

RUN pip install -r requirements.txt

ADD celery.py /<some path>/market/celery.py
# ADD any of the modules for celery specific to the project

ADD run /usr/local/bin/run

ENV REDIS_HOST redis
ENV REDIS_PORT 6379

RUN chmod +x /usr/local/bin/run

EXPOSE 6379

ENTRYPOINT ["/usr/local/bin/run"]
