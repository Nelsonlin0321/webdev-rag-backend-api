FROM python:3.10-bullseye

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the working directory
COPY requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set the entrypoint command to run train.py
ENTRYPOINT ["sh","./boot.sh"]