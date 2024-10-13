FROM python

WORKDIR /app/


COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6000 5000



CMD ["python", "server.py"]