#Parent/Base Image
FROM python:3.9-alpine3.17

#Tells us who is maintaining this image
LABEL maintainer="SmitM"

# Defining environment variable for better performance
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#copying requirements.txt file from current directory/local machine to temp folder inside image
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
#copying app directory as well
COPY ./app /app
#setting working directory
WORKDIR /app
EXPOSE 8000

#This value will be overrided based on docker compose configurations
ARG DEV=false
#runs the run command on alipne image
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    # /py/bin/pip install -r /tmp/requirements.dev.txt && \
    if [ $DEV = "true" ]; \ 
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

#updating the path of environment variable
#whenever we run any python commands it will run automatically
    #from the virtual environment
ENV PATH="/py/bin:$PATH"

#switching to our newly created user from root user
USER django-user