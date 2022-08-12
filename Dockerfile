# Use an official Python runtime as a parent image
FROM python:3.6.3

# Set proxy server, replace host:port with values for your servers
ENV http_proxy http://child-prc.intel.com:913
ENV https_proxy http://child-prc.intel.com:913

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Upgrade pip
RUN pip install --upgrade pip -i https://pypi.douban.com/simple --trusted-host pypi.douban.com --proxy http://child-prc.intel.com:913

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt -i https://pypi.douban.com/simple --proxy http://child-prc.intel.com:913

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "main.py"]
