import numpy as np
from typing import List, Tuple

# package imports
from astroalgo.astro_dataclasses import RefuelTanker
from astroalgo.constants import G, EARTH_MASS, EARTH_RADIUS

class HohmannTransfer:
    @staticmethod
    def calculate_delta_v(r1: float, r2: float, tanker: RefuelTanker = None, mu: float = G * EARTH_MASS) -> float:
        """
        Calculate delta-v for Hohmann transfer between circular orbits.
        If a tanker is provided, apply the rocket equation and consume fuel.
        Returns a single delta-v value.
        """
        # First burn (departure)
        v1 = np.sqrt(mu / r1)
        v_transfer_perigee = np.sqrt(mu * (2/r1 - 2/(r1+r2)))
        delta_v1 = abs(v_transfer_perigee - v1)
        
        # Second burn (insertion)
        v2 = np.sqrt(mu / r2)
        v_transfer_apogee = np.sqrt(mu * (2/r2 - 2/(r1+r2)))
        delta_v2 = abs(v2 - v_transfer_apogee)
        
        # Total theoretical delta-v
        total_delta_v = delta_v1 + delta_v2
        
        # If tanker is provided, apply rocket equation and consume fuel
        if tanker:
            # First burn
            actual_dv1 = tanker.consume_fuel(delta_v1)
            
            # Second burn - only if first burn was successful
            if actual_dv1 == delta_v1:
                actual_dv2 = tanker.consume_fuel(delta_v2)
                return actual_dv1 + actual_dv2
            else:
                return actual_dv1  # Partial first burn only
        
        return total_delta_v  # Return theoretical value if no tanker provided
    
    @staticmethod
    def calculate_transfer_time(r1: float, r2: float, mu: float = G * EARTH_MASS) -> float:
        """Calculate time for Hohmann transfer between circular orbits"""
        a = (r1 + r2) / 2  # Semi-major axis of transfer orbit
        return np.pi * np.sqrt(a**3 / mu)  # Half-orbit period
    
    @staticmethod
    def calculate_hohmann_trajectory(r1: float, r2: float, start_angle: float, 
                                   steps: int = 100, mu: float = G * EARTH_MASS) -> List[Tuple[float, float]]:
        """Calculate trajectory points for Hohmann transfer"""
        a = (r1 + r2) / 2  # Semi-major axis
        e = abs(r2 - r1) / (r2 + r1)  # Eccentricity
        
        trajectory = []
        for i in range(steps + 1):
            # True anomaly from 0 to π (half orbit)
            theta = i * np.pi / steps
            
            # Distance from focus (polar form of ellipse)
            r = a * (1 - e**2) / (1 + e * np.cos(theta))
            
            # Convert to Cartesian coordinates
            x = r * np.cos(theta + start_angle)
            y = r * np.sin(theta + start_angle)
            trajectory.append((x, y))
            
        return trajectory
