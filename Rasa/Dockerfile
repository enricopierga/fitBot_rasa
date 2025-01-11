# Dockerfile for Rasa Bot
FROM rasa/rasa:latest

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN rasa train

# Expose port for Rasa server
EXPOSE 5005

# Start Rasa server
CMD ["run", "--enable-api", "--cors", "*"]
