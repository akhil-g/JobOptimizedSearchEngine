# Use the official Alpine image as a base
FROM alpine:3.16

# Install necessary packages
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    git \
    bash \
    vim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Upgrade pip and setuptools
#RUN pip3 install --no-cache --upgrade pip setuptools

WORKDIR /app

# Clone the repository
RUN git clone https://github.com/akhil-g/JobOptimizedSearchEngine.git .

# Create a directory for the application
#WORKDIR /app/JobOptimizedSearchEngine

RUN ls -la

# Install the dependencies
RUN pip3 install -r requirements.txt
#RUN pip3 install --break-system-packages -r requirements.txt

EXPOSE 8000

# Command to run your application (if applicable)
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
