import numpy as np
from satellite_module import Satellite, ServiceVehicle, cluster_satellites
from orbital_optimizer import optimize_multi_cluster_mission

def test_optimizer():
    print("Testing optimizer functions")
    
    # Create some test satellites
    satellites = [
        Satellite(id=1, orbit_radius=7e6, anomaly=0, inclination=0, fuel_level=10, fuel_capacity=100),
        Satellite(id=2, orbit_radius=7e6, anomaly=np.pi/4, inclination=0, fuel_level=20, fuel_capacity=100),
        Satellite(id=3, orbit_radius=10e6, anomaly=0, inclination=np.pi/6, fuel_level=30, fuel_capacity=100),
    ]
    
    # Create service vehicle and depot
    service_vehicle = ServiceVehicle(
        fuel_level=2000,
        fuel_capacity=2000,
        position=np.array([7e6, 0, 0]),
        velocity=np.zeros(3)
    )
    depot_position = np.array([7e6, 0, 0])
    
    # First test the cluster_satellites function directly
    print("\nTesting cluster_satellites:")
    clusters = cluster_satellites(satellites)
    print(f"Found {len(clusters)} clusters")
    
    # Test the optimizer
    print("\nTesting optimizer:")
    sequence = optimize_multi_cluster_mission(service_vehicle, satellites, depot_position)
    
    # Print results
    print(f"Optimization result: {len(sequence)} satellites in sequence")
    for i, sat in enumerate(sequence):
        print(f"  {i+1}. Satellite {sat.id}, orbit radius: {sat.orbit_radius}, inclination: {sat.inclination}")
    
    return sequence

if __name__ == "__main__":
    print("Starting optimizer test")
    test_optimizer()
    print("Test complete") 