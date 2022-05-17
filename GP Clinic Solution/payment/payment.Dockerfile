FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
ADD . /usr/src/app
CMD [ "python", "./invokes.py" ]
CMD [ "python", "./payment.py" ]
