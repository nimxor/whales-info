#Deriving the latest base image
FROM python:3.9.13
WORKDIR /usr/app/src
COPY *.py ./
COPY requirements.txt ./
RUN pip install -r requirements.txt
CMD [ "python", "-u", "./main.py"]