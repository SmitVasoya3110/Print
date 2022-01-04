FROM python:3.9-alpine3.15
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY ./requirement.txt /code/
RUN pip3 install -r requirement.txt
RUN apt install libreoffice
COPY . /code/

EXPOSE 8000
CMD ["python", "app.py"]
