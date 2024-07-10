# Use an official Python runtime as a parent image
FROM python:3

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY ../sonic_sim_sw.py /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install -y net-tools
RUN apt-get install -y iproute2
RUN apt-get install -y tcpdump
RUN apt-get install -y tcpreplay


# Run script.py when the container launches
CMD ["python", "sonic_sim_sw.py", "&"]
