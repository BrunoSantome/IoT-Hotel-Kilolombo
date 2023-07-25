FROM python:3

COPY /app /etc/usr/src/app
WORKDIR /etc/usr/src/app
RUN pip install paho-mqtt
ENTRYPOINT ["python3"]
CMD ["digital_twin.py"]
