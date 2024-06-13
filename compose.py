import os
import subprocess
from dotenv import load_dotenv

# Set environment variables
load_dotenv()


# Call docker compose
subprocess.run(["docker", "compose", "up", "-d"])
