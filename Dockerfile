FROM python:3.8-slim
ENV PYTHONUNBUFFERED 1
ENV TZ=Asia/Dhaka
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app
ADD requirements.txt /app/
RUN pip3 install -r requirements.txt
COPY ./src/ /app