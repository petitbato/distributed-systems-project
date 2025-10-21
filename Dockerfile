FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
COPY ./watch.sh /opt/script/watch.sh
RUN chmod +x /opt/script/watch.sh
ENTRYPOINT ["/opt/script/watch.sh"]