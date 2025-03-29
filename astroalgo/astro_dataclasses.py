from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np

@dataclass
class Orbit:
    radius: float  # km
    satellites: List['Satellite'] = None
    
    def __post_init__(self):
        if self.satellites is None:
            self.satellites = []

@dataclass
class Satellite:
    orbit: Orbit
    angle: float  # radians
    speed: float  # radians per second
    position: Tuple[float, float] = None
    
    def __post_init__(self):
        self.update_position()
    
    def update_position(self, time_elapsed: float = 0):
        """Update satellite position based on orbital parameters"""
        self.angle = (self.angle + self.speed * time_elapsed) % (2 * np.pi)
        self.position = (
            self.orbit.radius * np.cos(self.angle),
            self.orbit.radius * np.sin(self.angle)
        )

@dataclass
class LaunchPad:
    radius: float  # Distance from planet center
    angle: float  # radians
    position: Tuple[float, float] = None
    
    def __post_init__(self):
        self.position = (
            self.radius * np.cos(self.angle),
            self.radius * np.sin(self.angle)
        )

@dataclass
class RefuelTanker:
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    fuel: float = 1000.0
    dry_mass: float = 500.0  # kg - mass of the tanker without fuel
    trajectory: List[Tuple[float, float]] = None
    waiting: bool = False
    target_satellite: Optional[Satellite] = None
    specific_impulse: float = 300.0  # seconds - typical for chemical propulsion
    
    def __post_init__(self):
        if self.trajectory is None:
            self.trajectory = [self.position]
    
    @property
    def total_mass(self) -> float:
        """Total mass of the tanker including fuel"""
        return self.dry_mass + self.fuel
    
    def consume_fuel(self, delta_v: float) -> float:
        """
        Consume fuel based on the rocket equation and return actual delta_v achieved.
        If not enough fuel is available, the maximum possible delta_v is returned.
        """
        # Rocket equation: delta_v = Isp * g0 * ln(m0/m1)
        # Rearranged: m1 = m0 / exp(delta_v / (Isp * g0))
        g0 = 9.81  # m/s²
        
        # Calculate final mass after burn
        m0 = self.total_mass
        m1 = m0 / np.exp(delta_v / (self.specific_impulse * g0))
        
        # Calculate fuel consumed
        fuel_consumed = m0 - m1
        
        # Check if we have enough fuel
        if fuel_consumed > self.fuel:
            # Not enough fuel, calculate maximum achievable delta_v
            max_m1 = self.dry_mass
            max_delta_v = self.specific_impulse * g0 * np.log(m0 / max_m1)
            self.fuel = 0
            return max_delta_v
        else:
            # Enough fuel, consume it
            self.fuel -= fuel_consumed
            return delta_v

@dataclass
class Shuttle:
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    fuel: float = 1000.0
    trajectory: List[Tuple[float, float]] = None
    deployed: bool = False

    def __post_init__(self):
        if self.trajectory is None:
            self.trajectory = [self.position]
