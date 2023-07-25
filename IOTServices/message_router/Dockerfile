From python:3.7.3

COPY /app /etc/usr/src/app

WORKDIR /etc/usr/src/app
RUN pip install Flask Flask-Cors requests
RUN pip install paho-mqtt
RUN pip install requests
ENTRYPOINT ["python3"]
CMD ["message_router.py"]
