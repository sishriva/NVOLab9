FROM osrg/ryu:latest

# Update package lists and install necessary packages
RUN apt-get update && \
    apt-get install -y \
        openvswitch-switch \
        vim \
        iputils-ping && \
    rm -rf /var/lib/apt/lists/*

# Set the default command to run when the container starts
CMD ["/bin/bash"]