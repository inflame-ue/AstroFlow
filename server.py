from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Tuple
from path_calculator import PathCalculator
import uvicorn

app = FastAPI()
calculator = PathCalculator()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class SatellitePosition(BaseModel):
    x: float
    y: float
    z: float

class PathRequest(BaseModel):
    rocket_position: SatellitePosition
    satellites: List[SatellitePosition]

@app.get("/")
async def read_root():
    return {"message": "Welcome to Satellite Refueling API"}

@app.get("/satellites/random/{num_satellites}")
async def get_random_satellites(num_satellites: int):
    try:
        positions = calculator.generate_random_satellite_positions(num_satellites)
        return [{"x": x, "y": y, "z": z} for x, y, z in positions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calculate-path")
async def calculate_path(request: PathRequest):
    try:
        rocket_pos = (request.rocket_position.x, request.rocket_position.y, request.rocket_position.z)
        satellites = [(s.x, s.y, s.z) for s in request.satellites]
        
        path = calculator.calculate_refueling_path(rocket_pos, satellites)
        return [{"x": x, "y": y, "z": z} for x, y, z in path]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 