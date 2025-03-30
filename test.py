import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from copy import deepcopy

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

    def predict_position(self, time_elapsed: float):
        new_angle = (self.angle + self.speed * time_elapsed) % (2 * np.pi)
        return (
            self.orbit.radius * np.cos(new_angle),
            self.orbit.radius * np.sin(new_angle)
        )
    
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
    trajectory: List[Tuple[float, float]] = None
    estimated_fuel: float = 0.0
    estimated_time: float = 0.0
    rendezvous_distance: float = float('inf')
    
    def __post_init__(self):
        self.position = (
            self.radius * np.cos(self.angle),
            self.radius * np.sin(self.angle)
        )
        if self.trajectory is None:
            self.trajectory = [self.position]

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
    pass

class MissionPlanner:
    def __init__(self, planet_radius: float, tanker: RefuelTanker, planet_mass: float = EARTH_MASS):
        self.planet_radius = planet_radius
        self.planet_mass = planet_mass
        self.mu = G * planet_mass
        self.orbits: List[Orbit] = []
        self.launch_pads: List[LaunchPad] = []
        self.tanker: RefuelTanker = tanker
        self.pad_trajectories: Dict[LaunchPad, List[Tuple[float, float]]] = {}
        
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
    
    def run_launch_simulation(self, tanker: RefuelTanker, target_orbit: Orbit):
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
        return tanker.position, steps
    
    def calculate_fuel_usage(self, pad: LaunchPad, target_orbit: Orbit) -> float:
        """Calculate estimated fuel usage for a launch from a specific pad"""
        # This is a simplified calculation - in reality would be more complex
        distance = target_orbit.radius - self.planet_radius
        launch_angle_diff = abs(np.sin(pad.angle)) * 0.2  # More fuel needed for non-equatorial launches
        
        # Basic formula: fuel = distance * (1 + angle_penalty)
        fuel_estimate = distance * (1 + launch_angle_diff)
        return fuel_estimate
    
    def run_simulation(self):
        if not self.orbits or not self.launch_pads:
            print("No orbits or launch pads defined")
            return
        
        target_orbit = self.orbits[0]  # Use first orbit as target
        
        # Simulate launch from each pad and track all trajectories
        all_satellites = []
        for satellite in target_orbit.satellites:
            all_satellites.append(satellite)

        # Calculate all possible pad-satellite combinations
        best_pad = None
        best_satellite = None
        min_distance = float('inf')
        min_fuel = float('inf')
        
        for satellite in all_satellites:
            for pad in self.launch_pads:
                # Clone the tanker to simulate from this pad
                test_tanker = deepcopy(self.tanker)
                test_tanker.position = pad.position
                test_tanker.trajectory = [pad.position]
                
                # Run simulation and store trajectory in the pad
                final_pos, time_steps = self.run_launch_simulation(test_tanker, target_orbit)
                pad.trajectory = test_tanker.trajectory.copy()
                
                # Calculate satellite position at arrival
                satellite_pos = satellite.predict_position(time_steps)
                
                # Calculate distance between tanker and satellite at arrival
                distance = np.sqrt((final_pos[0] - satellite_pos[0])**2 + 
                                  (final_pos[1] - satellite_pos[1])**2)
                
                # Estimate fuel usage
                fuel_usage = self.calculate_fuel_usage(pad, target_orbit)
                
                # Store metrics in pad
                pad.rendezvous_distance = distance
                pad.estimated_fuel = fuel_usage
                pad.estimated_time = time_steps
                
                # Track best combination based on minimum distance
                if distance < min_distance:
                    min_distance = distance
                    best_pad = pad
                    best_satellite = satellite
                
                # Also track minimum fuel usage
                if fuel_usage < min_fuel:
                    min_fuel = fuel_usage
        
        if best_pad and best_satellite:
            print(f"Best launch pad for minimum distance: angle={best_pad.angle:.2f} radians")
            print(f"Target satellite at angle: {best_satellite.angle:.2f} radians")
            print(f"Minimum distance at rendezvous: {min_distance:.2f} km")
            print(f"Estimated fuel usage: {best_pad.estimated_fuel:.2f} units")
            
            # Set tanker position to best launch pad
            self.tanker.position = best_pad.position
            self.tanker.trajectory = best_pad.trajectory.copy()
            
            # Visualize all trajectories
            self.visualize_all_trajectories(best_pad, best_satellite)
            
            # Show animation of the best launch
            self.animate_launch(best_pad, best_satellite)
        else:
            print("Could not find suitable launch parameters")
    
    def visualize_all_trajectories(self, best_pad, target_satellite):
        """Visualize all possible launch trajectories"""
        fig, ax = plt.subplots(figsize=(12, 12))
        ax.set_aspect('equal')
        
        # Plot planet
        planet = plt.Circle((0, 0), self.planet_radius, color='blue', alpha=0.3)
        ax.add_patch(planet)
        
        # Plot orbits
        for orbit in self.orbits:
            circle = plt.Circle((0, 0), orbit.radius, fill=False, color='grey', linestyle='--')
            ax.add_patch(circle)
            
            # Plot satellites in this orbit
            for satellite in orbit.satellites:
                ax.plot(satellite.position[0], satellite.position[1], 'ko', markersize=5)
        
        # Plot target satellite
        if target_satellite:
            ax.plot(target_satellite.position[0], target_satellite.position[1], 'yo', markersize=8)
        
        # Plot all launch pad trajectories
        for i, pad in enumerate(self.launch_pads):
            # Plot launch pad
            ax.plot(pad.position[0], pad.position[1], 'r^', markersize=8)
            
            # Plot trajectory if it exists
            if len(pad.trajectory) > 1:
                traj_x, traj_y = zip(*pad.trajectory)
                # Use different colors for different pads
                color = 'g' if pad == best_pad else plt.cm.tab10(i % 10)
                linestyle = '-' if pad == best_pad else '--'
                linewidth = 2 if pad == best_pad else 1
                ax.plot(traj_x, traj_y, color=color, linestyle=linestyle, linewidth=linewidth, 
                       label=f"Pad {i}: angle={pad.angle:.2f}, fuel={pad.estimated_fuel:.0f}, dist={pad.rendezvous_distance:.0f}km")
        
        # Set limits and labels
        max_radius = max(orbit.radius for orbit in self.orbits) * 1.1
        ax.set_xlim(-max_radius, max_radius)
        ax.set_ylim(-max_radius, max_radius)
        ax.set_xlabel('X Position (km)')
        ax.set_ylabel('Y Position (km)')
        ax.set_title('All Launch Trajectories')
        
        plt.grid(True)
        plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.05))
        plt.savefig('all_trajectories.png', bbox_inches='tight')
        plt.show()
    
    def visualize_simulation(self, best_pad, target_satellite):
        """Visualize the mission simulation"""
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')
        
        # Plot planet
        planet = plt.Circle((0, 0), self.planet_radius, color='blue', alpha=0.3)
        ax.add_patch(planet)
        
        # Plot orbits
        for orbit in self.orbits:
            circle = plt.Circle((0, 0), orbit.radius, fill=False, color='grey', linestyle='--')
            ax.add_patch(circle)
            
            # Plot satellites in this orbit
            for satellite in orbit.satellites:
                ax.plot(satellite.position[0], satellite.position[1], 'ko', markersize=5)
        
        # Plot launch pads
        for pad in self.launch_pads:
            ax.plot(pad.position[0], pad.position[1], 'r^', markersize=8)
        
        # Plot tanker trajectory
        traj_x, traj_y = zip(*self.tanker.trajectory)
        ax.plot(traj_x, traj_y, 'g-', linewidth=2)
        
        # Plot tanker final position
        ax.plot(self.tanker.position[0], self.tanker.position[1], 'go', markersize=8)
        
        # Plot target satellite
        if target_satellite:
            ax.plot(target_satellite.position[0], target_satellite.position[1], 'yo', markersize=8)
        
        # Set limits and labels
        max_radius = max(orbit.radius for orbit in self.orbits) * 1.1
        ax.set_xlim(-max_radius, max_radius)
        ax.set_ylim(-max_radius, max_radius)
        ax.set_xlabel('X Position (km)')
        ax.set_ylabel('Y Position (km)')
        ax.set_title('Orbital Mission Simulation')
        
        plt.grid(True)
        plt.savefig('mission_simulation.png')
        plt.show()
    
    def animate_launch(self, best_pad, target_satellite):
        """Create an animation of the launch sequence"""
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')
        
        # Set limits
        max_radius = max(orbit.radius for orbit in self.orbits) * 1.1
        ax.set_xlim(-max_radius, max_radius)
        ax.set_ylim(-max_radius, max_radius)
        
        # Plot static elements
        # Plot planet
        planet = plt.Circle((0, 0), self.planet_radius, color='blue', alpha=0.3)
        ax.add_patch(planet)
        
        # Plot orbits
        for orbit in self.orbits:
            circle = plt.Circle((0, 0), orbit.radius, fill=False, color='grey', linestyle='--')
            ax.add_patch(circle)
        
        # Plot launch pads
        for pad in self.launch_pads:
            ax.plot(pad.position[0], pad.position[1], 'r^', markersize=8)
        
        # Initialize elements that will be animated
        satellite_point, = ax.plot([], [], 'ko', markersize=5)
        tanker_point, = ax.plot([], [], 'go', markersize=8)
        trajectory_line, = ax.plot([], [], 'g-', linewidth=2)
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
        
        # Labels and title
        ax.set_xlabel('X Position (km)')
        ax.set_ylabel('Y Position (km)')
        ax.set_title('Launch Animation')
        plt.grid(True)
        
        # Calculate total frames and get trajectories
        frames = len(self.tanker.trajectory)
        trajectory = self.tanker.trajectory
        
        def init():
            """Initialize animation"""
            satellite_point.set_data([], [])
            tanker_point.set_data([], [])
            trajectory_line.set_data([], [])
            time_text.set_text('')
            return satellite_point, tanker_point, trajectory_line, time_text
        
        def update(frame):
            """Update animation for each frame"""
            # Update satellite position based on its speed
            sat_clone = deepcopy(target_satellite)
            sat_clone.update_position(frame)
            satellite_point.set_data([sat_clone.position[0]], [sat_clone.position[1]])
            
            # Update tanker position
            if frame < len(trajectory):
                current_pos = trajectory[frame]
                tanker_point.set_data([current_pos[0]], [current_pos[1]])
                
                # Update trajectory line
                traj_x = [pos[0] for pos in trajectory[:frame+1]]
                traj_y = [pos[1] for pos in trajectory[:frame+1]]
                trajectory_line.set_data(traj_x, traj_y)
                
                # Update time text
                time_text.set_text(f'Time: {frame} seconds')
            
            return satellite_point, tanker_point, trajectory_line, time_text
        
        # Create animation
        ani = FuncAnimation(fig, update, frames=frames,
                                   init_func=init, blit=True, interval=50)
        
        # Save animation
        try:
            ani.save('launch_animation.gif', writer='pillow', fps=15)
            print("Animation saved as launch_animation.gif")
        except Exception as e:
            print(f"Error saving animation: {e}")
        
        # Show animation
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
    for i in range(2):
        angle = i * 2 * np.pi / 5
        planner.add_satellite(low_orbit, angle + np.pi/2, 0.0015)  # Fast rotation

    # Add launch pads at different angles
    for i in range(5):
        angle = i * 2 * np.pi / 5
        planner.add_launch_pad(angle)
        
    # Run the simulation
    planner.run_simulation()

if __name__ == "__main__":
    run_example()
