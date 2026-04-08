FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# We also install openenv for validation
RUN pip install --no-cache-dir openenv fastapi uvicorn

COPY . .
ENV PYTHONPATH="/app"
EXPOSE 7860

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
