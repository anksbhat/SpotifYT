
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
	"""Health check endpoint."""
	return {"message": "SpotifYT API is running."}
