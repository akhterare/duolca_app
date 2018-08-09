FROM ubuntu:16.04 
LABEL maintainer="Azure App Service Container Images <appsvc-images@microsoft.com>"
# ENV http_proxy="http://proxy.lbs.alcatel-lucent.com:8000"
# ENV https_proxy="https://proxy.lbs.alcatel-lucent.com:8000"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
EXPOSE 5000
ENV no_proxy="login.microsoftonline.com"
CMD ["runserver.py"]