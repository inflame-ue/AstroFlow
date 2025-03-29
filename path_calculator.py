import numpy as np
from typing import List, Tuple

class PathCalculator:
    def __init__(self):
        # Earth's radius in kilometers (simplified)
        self.earth_radius = 6371
        
    def generate_random_satellite_positions(self, num_satellites: int) -> List[Tuple[float, float, float]]:
        """Generate random satellite positions in 3D space."""
        positions = []
        for _ in range(num_satellites):
            # Generate random spherical coordinates
            radius = self.earth_radius + np.random.uniform(200, 1000)  # Altitude between 200-1000km
            theta = np.random.uniform(0, 2 * np.pi)  # Longitude
            phi = np.random.uniform(0, np.pi)  # Latitude
            
            # Convert to Cartesian coordinates
            x = radius * np.sin(phi) * np.cos(theta)
            y = radius * np.sin(phi) * np.sin(theta)
            z = radius * np.cos(phi)
            
            positions.append((x, y, z))
        return positions
    
    def calculate_simple_path(self, start_pos: Tuple[float, float, float], 
                            target_pos: Tuple[float, float, float], 
                            num_points: int = 100) -> List[Tuple[float, float, float]]:
        """Calculate a simple linear path between two points."""
        path = []
        for i in range(num_points):
            t = i / (num_points - 1)
            x = start_pos[0] + (target_pos[0] - start_pos[0]) * t
            y = start_pos[1] + (target_pos[1] - start_pos[1]) * t
            z = start_pos[2] + (target_pos[2] - start_pos[2]) * t
            path.append((x, y, z))
        return path
    
    def calculate_refueling_path(self, rocket_pos: Tuple[float, float, float],
                               satellites: List[Tuple[float, float, float]]) -> List[Tuple[float, float, float]]:
        """Calculate a simple path for refueling multiple satellites."""
        # This is a simplified version - just goes to each satellite in order
        full_path = []
        current_pos = rocket_pos
        
        for satellite in satellites:
            path_segment = self.calculate_simple_path(current_pos, satellite)
            full_path.extend(path_segment)
            current_pos = satellite
            
        return full_path 