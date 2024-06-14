import uvicorn
from dotenv import load_dotenv

""" Run this script to start the application """

# Set environment variables
load_dotenv()

if __name__ == "__main__":

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8080)
