import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
import time

# Constants
G = 6.67430e-11  # Gravitational constant
EARTH_MASS = 5.972e24  # kg
EARTH_RADIUS = 6371  # km

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

class MissionPlanner:
    def __init__(self, planet_radius: float, tanker: RefuelTanker, planet_mass: float = EARTH_MASS):
        self.planet_radius = planet_radius
        self.planet_mass = planet_mass
        self.mu = G * planet_mass
        self.orbits: List[Orbit] = []
        self.launch_pads: List[LaunchPad] = []
        self.tanker: RefuelTanker = tanker
        
    def add_orbit(self, radius: float) -> Orbit:
        """Add a new orbit at specified radius"""
        orbit = Orbit(radius=radius)
        self.orbits.append(orbit)
        return orbit
    
    def add_satellite(self, orbit: Orbit, angle: float, speed: float) -> Satellite:
        """Add a satellite to a specific orbit"""
        satellite = Satellite(orbit=orbit, angle=angle, speed=speed)
        orbit.satellites.append(satellite)
        return satellite
    
    def add_launch_pad(self, angle: float) -> LaunchPad:
        """Add a launch pad at specified angle on planet surface"""
        pad = LaunchPad(radius=self.planet_radius, angle=angle)
        self.launch_pads.append(pad)
        return pad
    
    def calculate_best_launch_pad(self) -> Tuple[LaunchPad, float]:
        """Find the best launch pad based on minimum fuel consumption"""
        best_pad = None
        min_total_fuel = float('inf')
        
        for pad in self.launch_pads:
            # Calculate fuel needed for this pad to service all satellites
            fuel_needed = self.calculate_mission_fuel(pad)
            
            if fuel_needed < min_total_fuel:
                min_total_fuel = fuel_needed
                best_pad = pad
        
        return best_pad, min_total_fuel
    
    def calculate_mission_fuel(self, pad: LaunchPad) -> float:
        """Calculate fuel needed for a complete mission from a specific pad"""
        
        initial_fuel = self.tanker.fuel
        # Launch cost from planet to first orbit
        first_orbit = min(self.orbits, key=lambda o: o.radius)
        launch_dv = self.calculate_launch_cost(pad, first_orbit)
        self.tanker.consume_fuel(launch_dv)
        
        # Sort orbits by radius for sequential visits
        sorted_orbits = sorted(self.orbits, key=lambda o: o.radius)
        
        # Calculate inter-orbit transfers
        for i in range(len(sorted_orbits) - 1):
            r1 = sorted_orbits[i].radius
            r2 = sorted_orbits[i+1].radius
            # Use the updated method that returns a single delta-v value and consumes fuel
            HohmannTransfer.calculate_delta_v(r1, r2, self.tanker, self.mu)
        
        # Return to planet
        return_dv = self.calculate_reentry_cost(sorted_orbits[-1], pad)
        self.tanker.consume_fuel(return_dv)
        
        # Return total fuel consumed (initial - remaining)
        return initial_fuel - self.tanker.fuel
    
    def calculate_launch_cost(self, pad: LaunchPad, target_orbit: Orbit) -> float:
        """Calculate fuel cost to launch from pad to target orbit"""
        # Simple model: energy to reach orbital velocity + potential energy difference
        orbital_velocity = np.sqrt(self.mu / target_orbit.radius)
        return orbital_velocity
    
    def calculate_reentry_cost(self, orbit: Orbit, pad: LaunchPad) -> float:
        """Calculate fuel cost for reentry from orbit to landing pad"""
        # In reality, reentry can use atmosphere for braking
        # Here we use a simplified model
        orbital_velocity = np.sqrt(self.mu / orbit.radius)
        return orbital_velocity * 0.3  # Assume atmospheric braking reduces fuel needs
    
    def simulate_mission(self, best_pad: LaunchPad) -> None:
        """Simulate a complete mission from the best launch pad"""
        
        self.tanker.position = best_pad.position

        # Sort orbits by radius for sequential visits
        sorted_orbits = sorted(self.orbits, key=lambda o: o.radius)
        
        # Launch to first orbit
        self.simulate_launch(self.tanker, sorted_orbits[0])
        
        # Visit each orbit in sequence
        for i in range(len(sorted_orbits) - 1):
            # Service satellites in current orbit
            for satellite in sorted_orbits[i].satellites:
                # In a real simulation, we'd dock with each satellite
                pass
                
            # Transfer to next orbit
            self.simulate_hohmann_transfer(self.tanker, sorted_orbits[i], sorted_orbits[i+1])
        
        # Service satellites in the last orbit
        for satellite in sorted_orbits[-1].satellites:
            # In a real simulation, we'd dock with each satellite
            pass
            
        # Return to planet
        self.simulate_reentry(self.tanker, best_pad)
    
    def simulate_launch(self, tanker: RefuelTanker, target_orbit: Orbit) -> None:
        """Simulate launch from planet to first orbit"""
        # Start position
        start_x, start_y = tanker.position
        
        # Calculate launch angle (perpendicular to surface)
        launch_angle = math.atan2(start_y, start_x)
        
        # Generate a simple curved trajectory
        steps = 50
        for i in range(1, steps + 1):
            # Interpolate radius from planet radius to orbit radius
            t = i / steps
            r = self.planet_radius + t * (target_orbit.radius - self.planet_radius)
            
            # Add some curve to the trajectory
            angle = launch_angle + 0.5 * t
            
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            tanker.trajectory.append((x, y))
        
        # Update tanker position to orbit
        tanker.position = tanker.trajectory[-1]
    
    def simulate_hohmann_transfer(self, tanker: RefuelTanker, origin_orbit: Orbit, target_orbit: Orbit) -> None:
        """Simulate Hohmann transfer between orbits"""
        r1 = origin_orbit.radius
        r2 = target_orbit.radius
        
        # Get current position angle
        start_angle = math.atan2(tanker.position[1], tanker.position[0])
        
        # Calculate Hohmann trajectory
        transfer_trajectory = HohmannTransfer.calculate_hohmann_trajectory(
            r1, r2, start_angle, steps=50, mu=self.mu
        )
        
        # Perform the transfer and consume fuel
        HohmannTransfer.calculate_delta_v(r1, r2, tanker, self.mu)
        
        # Add to tanker's trajectory
        tanker.trajectory.extend(transfer_trajectory)
        
        # Update tanker position
        tanker.position = transfer_trajectory[-1]
    
    def simulate_reentry(self, tanker: RefuelTanker, target_pad: LaunchPad) -> None:
        """Simulate reentry from orbit to landing pad"""
        # Start position
        start_x, start_y = tanker.position
        
        # Target position
        end_x, end_y = target_pad.position
        
        # Calculate entry angle
        entry_angle = math.atan2(start_y, start_x)
        
        # Calculate distance
        start_r = math.sqrt(start_x**2 + start_y**2)
        
        # Generate curved reentry trajectory
        steps = 50
        for i in range(1, steps + 1):
            # Interpolate radius from orbit to planet
            t = i / steps
            r = start_r * (1 - t) + self.planet_radius * t
            
            # Add curve to trajectory with adjustment to land at pad
            target_angle = math.atan2(end_y, end_x)
            angle = entry_angle * (1 - t) + target_angle * t
            
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            tanker.trajectory.append((x, y))
        
        # Update tanker position to pad
        tanker.position = target_pad.position
    
    def visualize(self, animation: bool = True):
        """Visualize the mission planning simulation"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Set limits with some padding
        max_radius = max([o.radius for o in self.orbits], default=self.planet_radius * 2)
        limit = max_radius * 1.2
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_aspect('equal')
        
        # Draw planet
        planet = Circle((0, 0), self.planet_radius, color='blue', alpha=0.7)
        ax.add_patch(planet)
        
        # Draw orbits
        for orbit in self.orbits:
            circle = plt.Circle((0, 0), orbit.radius, fill=False, color='gray', linestyle='--')
            ax.add_patch(circle)
        
        # Draw launch pads
        pad_points = ax.scatter(
            [p.position[0] for p in self.launch_pads],
            [p.position[1] for p in self.launch_pads],
            color='red', s=100, zorder=3, label='Launch Pads'
        )
        
        # Get all satellites
        all_satellites = [s for orbit in self.orbits for s in orbit.satellites]
        
        # Initial satellite positions
        satellite_positions = np.array([s.position for s in all_satellites])
        satellite_points = ax.scatter(
            satellite_positions[:, 0], satellite_positions[:, 1],
            color='green', s=50, zorder=3, label='Satellites'
        )
        
        # Draw the best launch pad if calculated
        best_pad, fuel = self.calculate_best_launch_pad()
        if best_pad:
            best_pad_point = ax.scatter(
                best_pad.position[0], best_pad.position[1],
                color='yellow', s=150, zorder=4, label=f'Best Pad (Fuel: {fuel:.1f})'
            )
        
        # Draw tanker trajectory
        trajectory = np.array(self.tanker.trajectory)
        ax.plot(trajectory[:, 0], trajectory[:, 1], 'r-', linewidth=1.5, label='Tanker Trajectory')
            
        ax.set_title('Space Mission Planner - Optimal Refueling Strategy')
        ax.legend(loc='upper right')
        
        if animation:
            # Initialize tanker point
            tanker_point = ax.scatter([], [], color='orange', s=100, zorder=5, label='Tanker')
            
            def init():
                tanker_point.set_offsets(np.empty((0, 2)))
                satellite_points.set_offsets(np.empty((0, 2)))
                return satellite_points, tanker_point
            
            def animate(frame):
                # Update satellite positions
                time_elapsed = frame * 0.1  # Time step
                for satellite in all_satellites:
                    satellite.update_position(time_elapsed)
                
                new_positions = np.array([s.position for s in all_satellites])
                satellite_points.set_offsets(new_positions)
                
                # Update tanker position if applicable
                if frame < len(self.tanker.trajectory):
                    tanker_point.set_offsets([self.tanker.trajectory[frame]])
                
                return satellite_points, tanker_point
            
            # Create animation - use longer frames to give more time for satellite movement
            frames = max(200, len(self.tanker.trajectory))
            anim = FuncAnimation(
                fig, animate, init_func=init,
                frames=frames, interval=50, blit=True
            )
            plt.show()
        else:
            plt.show()


def run_example():
    
    # Create tanker starting at the planet surface (we'll update position based on launch pad)
    tanker = RefuelTanker(
        position=(EARTH_RADIUS, 0),  # Initial position, will be updated to launch pad
        velocity=(0, 0),
        fuel=1000.0,
        dry_mass=500.0
    )
    
    # Create mission planner with Earth-like planet
    planner = MissionPlanner(planet_radius=EARTH_RADIUS, tanker=tanker)
    
    # Add more orbits at different altitudes
    #very_low_orbit = planner.add_orbit(EARTH_RADIUS + 800)  # Very Low Earth Orbit
    low_orbit = planner.add_orbit(EARTH_RADIUS + 2000)  # Low Earth Orbit
    medium_low_orbit = planner.add_orbit(EARTH_RADIUS + 6000)  # Medium-Low orbit
    medium_orbit = planner.add_orbit(EARTH_RADIUS + 12000)  # Medium orbit
    medium_high_orbit = planner.add_orbit(EARTH_RADIUS + 24000)  # Medium-High orbit
    high_orbit = planner.add_orbit(EARTH_RADIUS + 40000)  # High orbit
    #very_high_orbit = planner.add_orbit(EARTH_RADIUS + 80000)  # Very High orbit
    
    # Add satellites to orbits with varying speeds (faster in lower orbits)
    
    # Very Low orbit satellites
    # for i in range(3):
    #     angle = i * 2 * np.pi / 4
    #     planner.add_satellite(very_low_orbit, angle, 0.0020)  # Fastest rotation
    
    # Low orbit satellites
    for i in range(2):
        angle = i * 2 * np.pi / 5
        planner.add_satellite(low_orbit, angle, 0.0015)  # Fast rotation
    
    # Medium-Low orbit satellites
    for i in range(3):
        angle = i * 2 * np.pi / 3
        planner.add_satellite(medium_low_orbit, angle, 0.0012)  # Medium-fast rotation
        
    # Medium orbit satellites
    for i in range(2):
        angle = i * 2 * np.pi / 4
        planner.add_satellite(medium_orbit, angle, 0.0008)  # Medium rotation
    
    # Medium-High orbit satellites
    for i in range(3):
        angle = i * np.pi
        planner.add_satellite(medium_high_orbit, angle, 0.0005)  # Medium-slow rotation
    
    # High orbit satellites
    for i in range(3):
        angle = i * 2 * np.pi / 3
        planner.add_satellite(high_orbit, angle, 0.0003)  # Slow rotation
    
    # Very High orbit satellite
    #planner.add_satellite(very_high_orbit, 0, 0.0001)  # Very slow rotation

    # Add launch pads at different positions
    for i in range(5):
        angle = i * 2 * np.pi / 5
        planner.add_launch_pad(angle)
    
    # Calculate the best launch pad
    best_pad, fuel = planner.calculate_best_launch_pad()
    print(f"Best launch pad angle: {best_pad.angle * 180 / np.pi:.1f}° with fuel: {fuel:.1f}")
    
    # Update tanker position to the best launch pad position
    tanker.position = best_pad.position
    tanker.trajectory = [tanker.position]  # Reset trajectory to start from the pad

    # Simulate mission from best pad
    planner.simulate_mission(best_pad)
    
    # Visualize results
    planner.visualize(animation=True)

def test_mission_planner():
    """Run tests on the mission planning algorithm"""
    print("Testing MissionPlanner...")
    
    # Test with different planet sizes
    planet_sizes = [EARTH_RADIUS, EARTH_RADIUS/2, EARTH_RADIUS*2]
    for radius in planet_sizes:
        # Create tanker for this test
        tanker = RefuelTanker(
            position=(radius, 0),  # Initial position at planet surface
            velocity=(0, 0),
            fuel=1000.0,
            dry_mass=500.0
        )
        
        planner = MissionPlanner(planet_radius=radius, tanker=tanker)
        
        # Add orbits and satellites
        orbit1 = planner.add_orbit(radius + 500)
        orbit2 = planner.add_orbit(radius + 2000)
        
        planner.add_satellite(orbit1, 0, 0.001)
        planner.add_satellite(orbit2, np.pi/2, 0.0005)
        
        # Add launch pads
        for i in range(4):
            planner.add_launch_pad(i * np.pi/2)
        
        # Find best pad
        best_pad, fuel = planner.calculate_best_launch_pad()
        print(f"Planet radius: {radius} km - Best pad angle: {best_pad.angle * 180/np.pi:.1f}° - Fuel: {fuel:.1f}")
    
    # Test with different orbit configurations
    # Create a tanker for evenly spaced orbits test
    tanker1 = RefuelTanker(
        position=(EARTH_RADIUS, 0),
        velocity=(0, 0),
        fuel=1000.0,
        dry_mass=500.0
    )
    planner = MissionPlanner(planet_radius=EARTH_RADIUS, tanker=tanker1)
    
    # Test 1: Evenly spaced orbits
    orbits1 = [planner.add_orbit(EARTH_RADIUS + r) for r in range(1000, 10001, 3000)]
    for orbit in orbits1:
        planner.add_satellite(orbit, np.random.random() * 2 * np.pi, 0.001)
    
    # Add pads to first test
    for i in range(8):
        angle = i * 2 * np.pi / 8
        planner.add_launch_pad(angle)
    
    best_pad1, fuel1 = planner.calculate_best_launch_pad()
    print(f"Evenly spaced orbits - Best pad angle: {best_pad1.angle * 180/np.pi:.1f}° - Fuel: {fuel1:.1f}")
        
    # Test 2: Clustered orbits
    # Create a new tanker for clustered orbits test
    tanker2 = RefuelTanker(
        position=(EARTH_RADIUS, 0),
        velocity=(0, 0),
        fuel=1000.0,
        dry_mass=500.0
    )
    planner = MissionPlanner(planet_radius=EARTH_RADIUS, tanker=tanker2)
    orbits2 = [planner.add_orbit(EARTH_RADIUS + r) for r in [500, 600, 700, 5000]]
    for orbit in orbits2:
        planner.add_satellite(orbit, np.random.random() * 2 * np.pi, 0.001)
    
    # Add same launch pads to test 2
    for i in range(8):
        angle = i * 2 * np.pi / 8
        planner.add_launch_pad(angle)
    
    best_pad2, fuel2 = planner.calculate_best_launch_pad()
    print(f"Clustered orbits - Best pad angle: {best_pad2.angle * 180/np.pi:.1f}° - Fuel: {fuel2:.1f}")
    
    print("Tests completed.")

if __name__ == "__main__":
    # Uncomment to run tests
    # test_mission_planner()
    
    # Run main example simulation
    run_example()