import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Tuple

# Constants
G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
M_EARTH = 5.972e24  # Earth mass (kg)
R_EARTH = 6371000  # Earth radius (m)

@dataclass
class Satellite:
    id: int
    orbit_radius: float  # m
    anomaly: float  # radians
    inclination: float  # radians
    fuel_level: float  # kg
    fuel_capacity: float  # kg
    
    def position(self, time: float = 0) -> np.ndarray:
        """Calculate position at a given time (assuming circular orbit)"""
        # Angular velocity based on orbit radius
        angular_velocity = np.sqrt(G * M_EARTH / (self.orbit_radius ** 3))
        current_anomaly = (self.anomaly + angular_velocity * time) % (2 * np.pi)
        
        # Position in orbital plane
        x_orbital = self.orbit_radius * np.cos(current_anomaly)
        y_orbital = self.orbit_radius * np.sin(current_anomaly)
        
        # Rotate to account for inclination
        x = x_orbital
        y = y_orbital * np.cos(self.inclination)
        z = y_orbital * np.sin(self.inclination)
        
        return np.array([x, y, z])

@dataclass
class ServiceVehicle:
    fuel_level: float  # kg
    fuel_capacity: float  # kg
    position: np.ndarray  # 3D position vector [x, y, z]
    velocity: np.ndarray  # 3D velocity vector [vx, vy, vz]
    
    def calculate_delta_v(self, target_satellite: Satellite, time: float = 0) -> float:
        """Simplified delta-V calculation for orbit transfer"""
        # In a real implementation, this would use the Lambert problem solver
        # or another orbital mechanics calculation
        
        # For this demo, we'll use a simplified model based on orbit radius difference
        r1 = np.linalg.norm(self.position)
        r2 = target_satellite.orbit_radius
        
        # Hohmann transfer approximation
        delta_v1 = np.sqrt(G * M_EARTH / r1) * (np.sqrt(2 * r2 / (r1 + r2)) - 1)
        delta_v2 = np.sqrt(G * M_EARTH / r2) * (1 - np.sqrt(2 * r1 / (r1 + r2)))
        
        return abs(delta_v1) + abs(delta_v2)
    
    def fuel_required(self, delta_v: float) -> float:
        """Calculate fuel required for a given delta-V using the rocket equation"""
        # Simplified: assuming constant exhaust velocity of 3000 m/s
        exhaust_velocity = 3000.0  # m/s
        initial_mass = 1000.0 + self.fuel_level  # kg (dry mass + fuel)
        
        final_mass = initial_mass * np.exp(-delta_v / exhaust_velocity)
        return initial_mass - final_mass
    
    def can_reach_and_return(self, satellite: Satellite, depot_position: np.ndarray) -> bool:
        """Check if vehicle can reach satellite and return to depot with current fuel"""
        delta_v_to_satellite = self.calculate_delta_v(satellite)
        
        # Create a temporary satellite object at depot position for delta-V calculation
        depot_sat = Satellite(
            id=-1, 
            orbit_radius=np.linalg.norm(depot_position),
            anomaly=np.arctan2(depot_position[1], depot_position[0]),
            inclination=np.arcsin(depot_position[2] / np.linalg.norm(depot_position)) if np.linalg.norm(depot_position) > 0 else 0,
            fuel_level=0, 
            fuel_capacity=0
        )
        
        # Calculate return delta-V from a position at the satellite's location
        temp_vehicle = ServiceVehicle(
            fuel_level=self.fuel_level,
            fuel_capacity=self.fuel_capacity,
            position=satellite.position(),
            velocity=np.zeros(3)
        )
        delta_v_return = temp_vehicle.calculate_delta_v(depot_sat)
        
        # Calculate total fuel required
        total_fuel_required = self.fuel_required(delta_v_to_satellite) + self.fuel_required(delta_v_return)
        
        # Add 20% margin for safety
        return total_fuel_required * 1.2 < self.fuel_level

def cluster_satellites(satellites: List[Satellite], epsilon: float = 5e5) -> Dict[int, List[Satellite]]:
    """Group satellites by orbits that are close to each other"""
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