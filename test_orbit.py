import numpy as np
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Satellite:
    id: int
    orbit_radius: float
    inclination: float
    fuel_level: float
    fuel_capacity: float

def cluster_satellites(satellites: List[Satellite], epsilon: float = 5e5) -> Dict[int, List[Satellite]]:
    """Group satellites by orbits that are close to each other"""
    print("Inside cluster_satellites function")
    clusters = {}
    cluster_id = 0
    
    # Simplified clustering based on orbit radius and inclination
    for sat in satellites:
        assigned = False
        for cid, members in clusters.items():
            if (abs(members[0].orbit_radius - sat.orbit_radius) < epsilon and
                abs(members[0].inclination - sat.inclination) < 0.1):
                clusters[cid].append(sat)
                assigned = True
                break
        
        if not assigned:
            clusters[cluster_id] = [sat]
            cluster_id += 1
    
    return clusters

def optimize_mission(satellites: List[Satellite]) -> List[Satellite]:
    """Simple optimization that calls cluster_satellites"""
    print("Inside optimize_mission function")
    # Cluster satellites by orbit
    clusters = cluster_satellites(satellites)
    print(f"Found {len(clusters)} clusters")
    
    # Just return all satellites from first cluster
    if clusters:
        first_cluster_id = list(clusters.keys())[0]
        return clusters[first_cluster_id]
    return []

def test_simple():
    """Simple test function"""
    print("Starting simple test")
    
    # Create some test satellites
    satellites = [
        Satellite(id=1, orbit_radius=7e6, inclination=0, fuel_level=10, fuel_capacity=100),
        Satellite(id=2, orbit_radius=7e6, inclination=0, fuel_level=20, fuel_capacity=100),
        Satellite(id=3, orbit_radius=10e6, inclination=0.1, fuel_level=30, fuel_capacity=100),
        Satellite(id=4, orbit_radius=10e6, inclination=0.1, fuel_level=15, fuel_capacity=100),
    ]
    
    # Test direct call to cluster_satellites
    print("\nTesting direct call to cluster_satellites:")
    clusters = cluster_satellites(satellites)
    print(f"Direct call found {len(clusters)} clusters")
    
    # Test call through optimize_mission
    print("\nTesting call through optimize_mission:")
    sequence = optimize_mission(satellites)
    print(f"Got sequence of {len(sequence)} satellites")
    
    print("\nTest complete")

if __name__ == "__main__":
    test_simple() 