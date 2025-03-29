import numpy as np
from satellite_module import Satellite, cluster_satellites

def test_cluster_satellites():
    print("Testing cluster_satellites function")
    
    # Create some test satellites
    satellites = [
        Satellite(id=1, orbit_radius=7e6, anomaly=0, inclination=0, fuel_level=10, fuel_capacity=100),
        Satellite(id=2, orbit_radius=7e6, anomaly=np.pi/4, inclination=0, fuel_level=20, fuel_capacity=100),
        Satellite(id=3, orbit_radius=10e6, anomaly=0, inclination=np.pi/6, fuel_level=30, fuel_capacity=100),
    ]
    
    # Call the function directly
    clusters = cluster_satellites(satellites)
    
    # Print results
    print(f"Found {len(clusters)} clusters:")
    for cluster_id, sats in clusters.items():
        print(f"  Cluster {cluster_id}: {len(sats)} satellites")
        for sat in sats:
            print(f"    Satellite {sat.id}, orbit radius: {sat.orbit_radius}, inclination: {sat.inclination}")
    
    return clusters

if __name__ == "__main__":
    print("Starting module test")
    test_cluster_satellites()
    print("Test complete") 