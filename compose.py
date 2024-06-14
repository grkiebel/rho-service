import os
import subprocess
from dotenv import load_dotenv

""" Run this script to build the and run the application in a Docker container """

# Set environment variables
load_dotenv()

try:
    # shut down any running containers
    subprocess.run(["docker", "compose", "down"], check=True)

    # remove the application image
    subprocess.run(["docker", "rmi", "service-app"], check=True)

    # Call docker compose
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

except subprocess.CalledProcessError as e:
    print(str(e))
    exit(1)
