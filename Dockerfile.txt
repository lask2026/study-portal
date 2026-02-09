# Use a slim Python image to keep things fast
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements first (this makes building faster)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your project files (including books and images)
COPY . .

# Koyeb uses port 8000 by default
EXPOSE 8000

# The command to run your app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "flask_app:app"]