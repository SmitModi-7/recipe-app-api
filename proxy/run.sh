#!/bin/sh

# If any command fails then fail the whole script
set -e

# substitutes environment variables in a file
# Reading the template file and writing it to a new file with replaced environment values
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
# Starting the Nginx web server in the foreground
nginx -g 'daemon off;'
