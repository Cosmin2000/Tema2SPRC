FROM python:3.6
COPY requirements.txt /tmp
RUN pip install -U setuptools
RUN pip install -r /tmp/requirements.txt
WORKDIR /tmp/app
COPY . /tmp/app
RUN chmod 777 /tmp/app/wait-for-it.sh
EXPOSE 5000
CMD ["python", "tema.py"]
