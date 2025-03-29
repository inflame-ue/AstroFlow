import numpy as np
from satellite_module import Satellite, ServiceVehicle, R_EARTH
from orbital_optimizer import (
    optimize_multi_cluster_mission,
    simulate_mission,
    visualize_mission
)

def test_algorithm():
    """Test the algorithm with various scenarios"""
    results = []
    
    # Test scenarios with different orbit configurations
    test_cases = [
        {
            "name": "Single orbit cluster",
            "satellites": [
                Satellite(id=1, orbit_radius=7e6, anomaly=0, inclination=0, fuel_level=10, fuel_capacity=100),
                Satellite(id=2, orbit_radius=7e6, anomaly=np.pi/4, inclination=0, fuel_level=20, fuel_capacity=100),
                Satellite(id=3, orbit_radius=7e6, anomaly=np.pi/2, inclination=0, fuel_level=30, fuel_capacity=100),
                Satellite(id=4, orbit_radius=7e6, anomaly=3*np.pi/4, inclination=0, fuel_level=15, fuel_capacity=100),
                Satellite(id=5, orbit_radius=7e6, anomaly=np.pi, inclination=0, fuel_level=25, fuel_capacity=100),
            ],
            "service_vehicle": ServiceVehicle(
                fuel_level=2000,
                fuel_capacity=2000,
                position=np.array([7e6, 0, 0]),
                velocity=np.zeros(3)
            ),
            "depot_position": np.array([7e6, 0, 0])
        },
        {
            "name": "Two orbit clusters",
            "satellites": [
                # Cluster 1 (7000 km altitude)
                Satellite(id=1, orbit_radius=7e6 + R_EARTH, anomaly=0, inclination=0, fuel_level=10, fuel_capacity=100),
                Satellite(id=2, orbit_radius=7e6 + R_EARTH, anomaly=np.pi/4, inclination=0, fuel_level=20, fuel_capacity=100),
                Satellite(id=3, orbit_radius=7e6 + R_EARTH, anomaly=np.pi/2, inclination=0, fuel_level=30, fuel_capacity=100),
                # Cluster 2 (10000 km altitude)
                Satellite(id=4, orbit_radius=10e6 + R_EARTH, anomaly=0, inclination=np.pi/6, fuel_level=15, fuel_capacity=100),
                Satellite(id=5, orbit_radius=10e6 + R_EARTH, anomaly=np.pi/2, inclination=np.pi/6, fuel_level=25, fuel_capacity=100),
            ],
            "service_vehicle": ServiceVehicle(
                fuel_level=2000,
                fuel_capacity=2000,
                position=np.array([7e6 + R_EARTH, 0, 0]),
                velocity=np.zeros(3)
            ),
            "depot_position": np.array([7e6 + R_EARTH, 0, 0])
        },
        {
            "name": "Three orbit clusters with low fuel",
            "satellites": [
                # Cluster 1 (LEO)
                Satellite(id=1, orbit_radius=7e6 + R_EARTH, anomaly=0, inclination=0, fuel_level=10, fuel_capacity=100),
                Satellite(id=2, orbit_radius=7e6 + R_EARTH, anomaly=np.pi/3, inclination=0, fuel_level=20, fuel_capacity=100),
                # Cluster 2 (MEO)
                Satellite(id=3, orbit_radius=20e6 + R_EARTH, anomaly=0, inclination=np.pi/4, fuel_level=30, fuel_capacity=100),
                Satellite(id=4, orbit_radius=20e6 + R_EARTH, anomaly=np.pi/2, inclination=np.pi/4, fuel_level=15, fuel_capacity=100),
                # Cluster 3 (GEO)
                Satellite(id=5, orbit_radius=36e6 + R_EARTH, anomaly=0, inclination=0, fuel_level=5, fuel_capacity=100),
            ],
            "service_vehicle": ServiceVehicle(
                fuel_level=1000,  # Limited fuel
                fuel_capacity=1000,
                position=np.array([7e6 + R_EARTH, 0, 0]),
                velocity=np.zeros(3)
            ),
            "depot_position": np.array([7e6 + R_EARTH, 0, 0])
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}: {test_case['name']}")
        
        # Plan mission
        sequence = optimize_multi_cluster_mission(
            test_case["service_vehicle"],
            test_case["satellites"],
            test_case["depot_position"]
        )
        
        # Simulate mission
        metrics = simulate_mission(
            test_case["service_vehicle"],
            sequence,
            test_case["depot_position"]
        )
        
        # Print results
        print(f"Satellites serviced: {metrics['satellites_serviced']} / {len(test_case['satellites'])}")
        print(f"Total delta-V: {metrics['total_delta_v']:.2f} m/s")
        print(f"Total fuel used: {metrics['total_fuel_used']:.2f} kg")
        print(f"Remaining fuel: {metrics['remaining_fuel']:.2f} kg")
        print(f"Fuel efficiency: {metrics['fuel_efficiency']:.4f} satellites/kg")
        print(f"Mission success: {metrics['mission_success']}")
        
        # Visualize mission
        visualize_mission(test_case["satellites"], sequence, test_case["depot_position"])
        
        # Store results
        results.append({
            "test_case": test_case["name"],
            "satellites_total": len(test_case["satellites"]),
            "metrics": metrics,
            "sequence": [sat.id for sat in sequence]
        })
    
    return results

if __name__ == "__main__":
    print("Testing Orbital Refueling Mission Planning Algorithm")
    results = test_algorithm()
    
    # Summary of results
    print("\nSummary of Results:")
    for i, result in enumerate(results):
        print(f"\nTest Case {i+1}: {result['test_case']}")
        print(f"Satellites serviced: {result['metrics']['satellites_serviced']} / {result['satellites_total']}")
        print(f"Mission success: {result['metrics']['mission_success']}")
        print(f"Sequence: {result['sequence']}")
        print(f"Fuel efficiency: {result['metrics']['fuel_efficiency']:.4f} satellites/kg") 