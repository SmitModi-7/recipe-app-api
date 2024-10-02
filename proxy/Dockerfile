# using unprivileged version of Nginx
# The "unprivileged" version means that Nginx will run as a non-root user for security reasons.
FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="SmitM"

# Copying files from the build context/local machine into the container's file system
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

# Nginx will listen on port 8000.
ENV LISTEN_PORT=8000
# The hostname of the app service that Nginx will forward traffic to is app
ENV APP_HOST=app
# The port where the app service is running and where Nginx will proxy traffic is 9000
ENV APP_PORT=9000

# Temporarily switches to the root user to perform administrative tasks
USER root

# Commands for File Setup
RUN mkdir -p /vol/static && \
    chmod 755 /vol/static && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

# Volume Declaration
VOLUME /vol/static

# Switches back to the nginx user after performing the root-level operations
USER nginx

# This specifies the command that will be executed when the container starts. It runs the run.sh scripts
CMD ["/run.sh"]
