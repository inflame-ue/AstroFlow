import numpy as np
import matplotlib.pyplot as plt
import heapq
from typing import List, Dict

# Explicitly import all required functions from satellite_module
from satellite_module import (
    Satellite, 
    ServiceVehicle, 
    cluster_satellites,
    R_EARTH
)

def find_optimal_sequence(service_vehicle: ServiceVehicle, 
                         satellites: List[Satellite],
                         depot_position: np.ndarray) -> List[Satellite]:
    """
    Find optimal refueling sequence using a greedy algorithm
    with consideration for orbital mechanics and fuel constraints
    """
    remaining_satellites = satellites.copy()
    refueling_sequence = []
    
    # Start from depot
    current_position = depot_position.copy()
    
    # Create temporary vehicle for planning
    planning_vehicle = ServiceVehicle(
        fuel_level=service_vehicle.fuel_level,
        fuel_capacity=service_vehicle.fuel_capacity,
        position=current_position,
        velocity=np.zeros(3)
    )
    
    while remaining_satellites:
        # Find the next best satellite to visit
        best_satellite = None
        best_value = float('-inf')  # Initialize with negative infinity
        
        for satellite in remaining_satellites:
            # Skip if we can't reach this satellite and return to depot
            if not planning_vehicle.can_reach_and_return(satellite, depot_position):
                continue
                
            # Calculate delta-V to reach this satellite
            delta_v = planning_vehicle.calculate_delta_v(satellite)
            fuel_needed = planning_vehicle.fuel_required(delta_v)
            
            # Skip if we don't have enough fuel
            if fuel_needed >= planning_vehicle.fuel_level:
                continue
                
            # Value metric: prioritize satellites that need refueling more
            # and require less fuel to reach
            fuel_need_percentage = 1 - (satellite.fuel_level / satellite.fuel_capacity)
            value = fuel_need_percentage / (fuel_needed + 1)  # +1 to avoid division by zero
            
            if value > best_value:
                best_value = value
                best_satellite = satellite
        
        # If no viable satellite found, break
        if best_satellite is None:
            break
            
        # Add best satellite to sequence
        refueling_sequence.append(best_satellite)
        remaining_satellites.remove(best_satellite)
        
        # Update vehicle state (position and remaining fuel)
        delta_v = planning_vehicle.calculate_delta_v(best_satellite)
        fuel_used = planning_vehicle.fuel_required(delta_v)
        planning_vehicle.fuel_level -= fuel_used
        planning_vehicle.position = best_satellite.position()
        
        # Account for refueling operation (time spent and small amount of fuel)
        planning_vehicle.fuel_level -= 5  # Simplified: 5kg of fuel used during refueling operation
    
    return refueling_sequence

def optimize_multi_cluster_mission(service_vehicle: ServiceVehicle,
                                  satellites: List[Satellite],
                                  depot_position: np.ndarray) -> List[Satellite]:
    """
    Optimize mission across multiple clusters of satellites
    """
    # Explicitly use the imported cluster_satellites function
    print("About to call cluster_satellites in optimize_multi_cluster_mission")
    clusters = cluster_satellites(satellites)
    print(f"Called cluster_satellites, got {len(clusters)} clusters")
    
    # For each cluster, calculate value metric (satellites serviced / fuel used)
    cluster_values = []
    
    for cluster_id, cluster_satellites in clusters.items():
        # Create a temporary vehicle for planning
        planning_vehicle = ServiceVehicle(
            fuel_level=service_vehicle.fuel_level,
            fuel_capacity=service_vehicle.fuel_capacity,
            position=depot_position.copy(),
            velocity=np.zeros(3)
        )
        
        # Find optimal sequence within this cluster
        sequence = find_optimal_sequence(planning_vehicle, cluster_satellites, depot_position)
        
        # Skip if no satellites can be serviced in this cluster
        if not sequence:
            continue
            
        # Calculate total delta-V and fuel required for this cluster
        total_delta_v = 0
        total_fuel = 0
        
        # First, calculate delta-V to reach first satellite in sequence
        first_sat = sequence[0]
        delta_v = planning_vehicle.calculate_delta_v(first_sat)
        fuel = planning_vehicle.fuel_required(delta_v)
        total_delta_v += delta_v
        total_fuel += fuel
        
        # Calculate delta-V between satellites in sequence
        current_pos = first_sat.position()
        for i in range(1, len(sequence)):
            # Create temporary vehicle at current position
            temp_vehicle = ServiceVehicle(
                fuel_level=planning_vehicle.fuel_level - total_fuel,
                fuel_capacity=planning_vehicle.fuel_capacity,
                position=current_pos,
                velocity=np.zeros(3)
            )
            
            next_sat = sequence[i]
            delta_v = temp_vehicle.calculate_delta_v(next_sat)
            fuel = temp_vehicle.fuel_required(delta_v)
            total_delta_v += delta_v
            total_fuel += fuel
            current_pos = next_sat.position()
        
        # Calculate delta-V to return to depot
        temp_vehicle = ServiceVehicle(
            fuel_level=planning_vehicle.fuel_level - total_fuel,
            fuel_capacity=planning_vehicle.fuel_capacity,
            position=current_pos,
            velocity=np.zeros(3)
        )
        
        # Create a temporary satellite object at depot position for delta-V calculation
        depot_sat = Satellite(
            id=-1, 
            orbit_radius=np.linalg.norm(depot_position),
            anomaly=np.arctan2(depot_position[1], depot_position[0]),
            inclination=np.arcsin(depot_position[2] / np.linalg.norm(depot_position)) if np.linalg.norm(depot_position) > 0 else 0,
            fuel_level=0, 
            fuel_capacity=0
        )
        
        return_delta_v = temp_vehicle.calculate_delta_v(depot_sat)
        return_fuel = temp_vehicle.fuel_required(return_delta_v)
        total_delta_v += return_delta_v
        total_fuel += return_fuel
        
        # Calculate value: satellites serviced per unit of fuel
        value = len(sequence) / total_fuel if total_fuel > 0 else 0
        
        # Add to priority queue (negative value for max-heap behavior)
        heapq.heappush(cluster_values, (-value, cluster_id, sequence, total_fuel))
    
    # Greedy algorithm: service highest value clusters first until fuel runs out
    final_sequence = []
    remaining_fuel = service_vehicle.fuel_level
    
    while cluster_values and remaining_fuel > 0:
        _, cluster_id, sequence, fuel_required = heapq.heappop(cluster_values)
        
        # Skip if not enough fuel
        if fuel_required > remaining_fuel:
            continue
            
        # Add this cluster's sequence to final sequence
        final_sequence.extend(sequence)
        remaining_fuel -= fuel_required
    
    return final_sequence

def visualize_mission(satellites: List[Satellite], 
                     sequence: List[Satellite], 
                     depot_position: np.ndarray):
    """Visualize the mission plan"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Plot Earth
    u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
    x = R_EARTH * np.cos(u) * np.sin(v)
    y = R_EARTH * np.sin(u) * np.sin(v)
    z = R_EARTH * np.cos(v)
    ax.plot_surface(x, y, z, color='blue', alpha=0.1)
    
    # Plot all satellite orbits
    for sat in satellites:
        theta = np.linspace(0, 2*np.pi, 100)
        x_orbit = sat.orbit_radius * np.cos(theta)
        y_orbit = sat.orbit_radius * np.sin(theta) * np.cos(sat.inclination)
        z_orbit = sat.orbit_radius * np.sin(theta) * np.sin(sat.inclination)
        ax.plot(x_orbit, y_orbit, z_orbit, 'gray', alpha=0.3)
    
    # Plot all satellites
    for sat in satellites:
        pos = sat.position()
        if sat in sequence:
            ax.scatter(pos[0], pos[1], pos[2], color='green', s=50)
        else:
            ax.scatter(pos[0], pos[1], pos[2], color='red', s=30)
    
    # Plot depot
    ax.scatter(depot_position[0], depot_position[1], depot_position[2], 
               color='blue', s=100, marker='*')
    
    # Plot mission path
    path_x, path_y, path_z = [depot_position[0]], [depot_position[1]], [depot_position[2]]
    for sat in sequence:
        pos = sat.position()
        path_x.append(pos[0])
        path_y.append(pos[1])
        path_z.append(pos[2])
    path_x.append(depot_position[0])
    path_y.append(depot_position[1])
    path_z.append(depot_position[2])
    
    ax.plot(path_x, path_y, path_z, 'k-', linewidth=2)
    
    # Annotate satellites in sequence
    for i, sat in enumerate(sequence):
        pos = sat.position()
        ax.text(pos[0], pos[1], pos[2], f"{i+1}", fontsize=12)
    
    # Set equal aspect ratio
    max_range = max([
        max(path_x) - min(path_x),
        max(path_y) - min(path_y),
        max(path_z) - min(path_z)
    ])
    
    mid_x = (max(path_x) + min(path_x)) / 2
    mid_y = (max(path_y) + min(path_y)) / 2
    mid_z = (max(path_z) + min(path_z)) / 2
    
    ax.set_xlim(mid_x - max_range/2, mid_x + max_range/2)
    ax.set_ylim(mid_y - max_range/2, mid_y + max_range/2)
    ax.set_zlim(mid_z - max_range/2, mid_z + max_range/2)
    
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title('Satellite Refueling Mission Plan')
    
    plt.tight_layout()
    plt.savefig('mission_visualization.png')
    plt.show()

def simulate_mission(service_vehicle: ServiceVehicle,
                    sequence: List[Satellite],
                    depot_position: np.ndarray) -> Dict:
    """
    Simulate the mission and return performance metrics
    """
    # Deep copy to avoid modifying originals
    vehicle = ServiceVehicle(
        fuel_level=service_vehicle.fuel_level,
        fuel_capacity=service_vehicle.fuel_capacity,
        position=depot_position.copy(),
        velocity=np.zeros(3)
    )
    
    metrics = {
        "satellites_serviced": 0,
        "total_delta_v": 0,
        "total_fuel_used": 0,
        "mission_success": True
    }
    
    current_position = depot_position.copy()
    
    # Process each satellite in sequence
    for sat in sequence:
        # Create temporary vehicle for delta-V calculation
        temp_vehicle = ServiceVehicle(
            fuel_level=vehicle.fuel_level,
            fuel_capacity=vehicle.fuel_capacity,
            position=current_position,
            velocity=np.zeros(3)
        )
        
        # Calculate delta-V to reach satellite
        delta_v = temp_vehicle.calculate_delta_v(sat)
        fuel_needed = temp_vehicle.fuel_required(delta_v)
        
        # Check if we have enough fuel
        if fuel_needed > vehicle.fuel_level:
            metrics["mission_success"] = False
            break
            
        # Update metrics
        metrics["total_delta_v"] += delta_v
        metrics["total_fuel_used"] += fuel_needed
        vehicle.fuel_level -= fuel_needed
        
        # Refuel satellite
        refuel_amount = sat.fuel_capacity - sat.fuel_level
        refuel_amount = min(refuel_amount, 50)  # Assuming 50kg max transfer
        
        # Small fuel cost for refueling operation
        vehicle.fuel_level -= 5  # Simplified: 5kg of fuel used during refueling
        
        # Update position and metrics
        current_position = sat.position()
        metrics["satellites_serviced"] += 1
    
    # Calculate return to depot
    temp_vehicle = ServiceVehicle(
        fuel_level=vehicle.fuel_level,
        fuel_capacity=vehicle.fuel_capacity,
        position=current_position,
        velocity=np.zeros(3)
    )
    
    # Create a temporary satellite at depot for delta-V calculation
    depot_sat = Satellite(
        id=-1, 
        orbit_radius=np.linalg.norm(depot_position),
        anomaly=np.arctan2(depot_position[1], depot_position[0]),
        inclination=np.arcsin(depot_position[2] / np.linalg.norm(depot_position)) if np.linalg.norm(depot_position) > 0 else 0,
        fuel_level=0, 
        fuel_capacity=0
    )
    
    return_delta_v = temp_vehicle.calculate_delta_v(depot_sat)
    return_fuel = temp_vehicle.fuel_required(return_delta_v)
    
    if return_fuel > vehicle.fuel_level:
        metrics["mission_success"] = False
    else:
        metrics["total_delta_v"] += return_delta_v
        metrics["total_fuel_used"] += return_fuel
        vehicle.fuel_level -= return_fuel
    
    metrics["remaining_fuel"] = vehicle.fuel_level
    metrics["fuel_efficiency"] = metrics["satellites_serviced"] / metrics["total_fuel_used"] if metrics["total_fuel_used"] > 0 else 0
    
    return metrics

# Simple test code
if __name__ == "__main__":
    # Test to verify the module can be run standalone
    print("Testing orbital_optimizer module")
    
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
    
    # Test with a direct call to cluster_satellites
    print("\nTesting standalone cluster_satellites call:")
    test_clusters = cluster_satellites(satellites)
    print(f"Direct call result: {len(test_clusters)} clusters")
    
    # Test the optimizer
    print("\nTesting optimize_multi_cluster_mission:")
    sequence = optimize_multi_cluster_mission(service_vehicle, satellites, depot_position)
    print(f"Optimization result: {len(sequence)} satellites in sequence")
    
    print("Module test complete") 