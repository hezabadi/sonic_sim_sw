"""
sudo docker inspect -f '{{.State.Pid}}' <container name>
sudo mkdir -p /var/run/netns
ln -sf /proc/<PID>/ns/net /var/run/netns/<YOUR DESIRED NETNS NAME FOR YOU CONTAINER>
sudo ip link add veth1_container type veth peer name veth1_root
sudo ifconfig veth1_container up
sudo ifconfig veth1_root up
sudo ip link set veth1_container netns <YOUR NETNS NAME>
sudo ip netns exec <YOUR NETNS NAME> ifconfig veth1_container up

docker run --rm --name my-container my-image

"""

import os, logging, time
import subprocess as sp
import docker

docker_start_timeout = 30

class DockerManager:
    def __init__(self,  contaimer_name=None, docker_image_name='sonic_sim_v1', interface_number: int = 12):
        # int(time.time() * 1000) % 100000  # it generate unique number that would stay unique for 3 hours
        self.docker_image_name = docker_image_name
        self.container_name = contaimer_name if contaimer_name else F'sonic_sim_{int(time.time() * 1000) % 100000}'
        self.interface_number = interface_number
        self.log = logging.getLogger('DockerManager')

    @staticmethod
    def start_container(image_name, container_name):
        # Initialize the Docker client
        log = logging.getLogger('start_container')
        client = docker.from_env()

        # Start the container
        try:
            container = client.containers.run(image_name, detach=True, name=container_name)
            log.info(f"Container '{container_name}' started.")
            return container.id
        except docker.errors.ImageNotFound:
            log.info(f"Image '{image_name}' not found.")
            return None
        except docker.errors.APIError as e:
            log.info(f"Error starting container '{container_name}': {e}")
            return None

    @staticmethod
    def check_container_health(container_name):
        # Initialize the Docker client
        client = docker.from_env()
        log = logging.getLogger('check_container_health')

        # Get the container object
        try:
            container = client.containers.get(container_name)
        except docker.errors.NotFound:
            log.info(f"Container '{container_name}' not found.")
            return False

        # Check if the container is running
        if container.status != 'running':
            log.info(f"Container '{container_name}' is not running.")
            return False

        # Check if the container is healthy
        health = container.attrs.get('State', {}).get('Health', {})
        if health.get('Status') == 'healthy':
            log.info(f"Container '{container_name}' is healthy.")
            return True
        else:
            log.info(f"Container '{container_name}' is not healthy.")
            return False

    @staticmethod
    def get_container_pid(container_name):
        # Initialize the Docker client
        client = docker.from_env()
        # Get all running containers
        containers = client.containers.list()

        # Iterate through the containers
        for container in containers:
            # Check if the container name matches
            if container.name == container_name:
                # Get the container's PID
                container_pid = container.attrs['State']['Pid']
                return container_pid

        # If the container is not found, return None
        return None

    @staticmethod
    def stop_and_remove_container(container_name):
        # Initialize the Docker client
        client = docker.from_env()
        log = logging.getLogger('check_container_health')

        # Get the container object
        try:
            container = client.containers.get(container_name)
        except docker.errors.NotFound:
            log.info(f"Container '{container_name}' not found.")
            return False

        # Stop the container
        try:
            container.stop(timeout=5)  # Timeout in seconds, adjust as needed
            log.info(f"Container '{container_name}' stopped.")
        except docker.errors.APIError as e:
            log.info(f"Error stopping container '{container_name}': {e}")
            return False

        # Remove the container
        try:
            container.remove()
            log.info(f"Container '{container_name}' removed.")
            return True
        except docker.errors.APIError as e:
            log.info(f"Error removing container '{container_name}': {e}")
            return False

    def start_sonic_sim(self):
        container_id = self.start_container(self.docker_image_name, self.container_name)
        if container_id is None:
            raise Exception('test could not start the container')

        start_time = time.time()
        is_healthy = False
        while not is_healthy:
            is_healthy = self.check_container_health(self.container_name)
            # Check if timeout has been reached
            if time.time() - start_time > docker_start_timeout:
                self.log.info("Timeout reached container is not running or not healthy. Exiting loop.")
                raise Exception('test could not run the sonic_sim docker container ')
        self.add_interfaces()

    def stop_sonic_sim(self):
        self.stop_and_remove_container(self.container_name)
        self.cleanup_interfaces()

    def add_interfaces(self):
        netns_path = "/var/run/netns"
        self.log.info("create the netns directory, directory would be unaltered if already exist ")
        os.makedirs(netns_path, exist_ok=True)
        container_pid = self.get_container_pid(self.container_name)
        if container_pid is None: raise Exception(f"Container '{self.container_name}' not found.")
        cmd = f"ln -sf /proc/{container_pid}/ns/net /var/run/netns/{self.container_name}_net"
        sp.Popen(cmd.split(), stdout=sp.PIPE, stderr=sp.PIPE)

        interface_prefix_container = f'veth_{container_pid}_c_'
        interface_prefix_host = f'veth_{container_pid}_h_'
        for i in range(1, self.interface_number+1):
            port_index = i + 1
            interface_command_list = [
                f'sudo ip link add {interface_prefix_container}{port_index} type veth peer name {interface_prefix_host}{port_index}',
                f'sudo ifconfig {interface_prefix_container}{port_index} up',
                f'sudo ifconfig {interface_prefix_host}{port_index} up',
                f'sudo ip link set %s netns {self.container_name}_net'
                f'sudo ip netns exec {self.container_name}_net ifconfig {interface_prefix_container}{port_index} up'
            ]
            for cmd in interface_command_list:
                sp.Popen(cmd.split(), stdout=sp.PIPE, stderr=sp.PIPE)
        return

    def cleanup_interfaces(self):
        pass



