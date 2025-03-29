import numpy as np
import heapq
from typing import List, Dict
from satellite_module import Satellite, ServiceVehicle, cluster_satellites

def simple_optimize(satellites: List[Satellite]) -> Dict[int, List[Satellite]]:
    """Extremely simple function that just calls cluster_satellites"""
    print("In simple_optimize, about to call cluster_satellites")
    clusters = cluster_satellites(satellites)
    print(f"Called cluster_satellites, got {len(clusters)} clusters")
    return clusters

if __name__ == "__main__":
    # Create some test satellites
    satellites = [
        Satellite(id=1, orbit_radius=7e6, anomaly=0, inclination=0, fuel_level=10, fuel_capacity=100),
        Satellite(id=2, orbit_radius=7e6, anomaly=np.pi/4, inclination=0, fuel_level=20, fuel_capacity=100),
        Satellite(id=3, orbit_radius=10e6, anomaly=0, inclination=np.pi/6, fuel_level=30, fuel_capacity=100),
    ]
    
    print("Starting direct test")
    clusters = simple_optimize(satellites)
    print(f"Test complete, found {len(clusters)} clusters") 