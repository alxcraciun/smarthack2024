from fastapi import FastAPI
from main2 import GameSimulator
from main2 import DailySummary
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    simulator = GameSimulator()
    logger = simulator.run()
    return logger

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8082)