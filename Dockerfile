#####################################################################################################################
# DUOLCA 1.0.0  
# DOCKERFILE
#
# This Dockerfile is used as a script to build the container that runs the Duolca App
# It runs the requirements.txt file and sets a specific no_proxy that ensures that the app runs under the Nokia proxy
#
# Duolca 1.0.0 \\ August 17th, 2018 \\ Areena Akhter
#####################################################################################################################

FROM ubuntu:16.04 
LABEL maintainer="Azure App Service Container Images <appsvc-images@microsoft.com>"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
EXPOSE 5000
ENV no_proxy="login.microsoftonline.com"
CMD ["runserver.py"]