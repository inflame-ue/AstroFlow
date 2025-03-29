import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, PathPatch
from matplotlib.path import Path
import math
from typing import List, Tuple, Dict, Optional
import random

# Constants
G = 6.67430e-11  # Gravitational constant
PLANET_MASS = 5.972e24  # Earth mass in kg
PLANET_RADIUS = 6371  # Earth radius in km
MAX_FUEL = 1000  # Maximum fuel for the tanker
FUEL_CONSUMPTION_RATE = 0.2  # Reduced to prevent over-consumption
REFUEL_THRESHOLD = 20  # Distance threshold for refueling
COLLECTION_THRESHOLD = 10  # Distance threshold for collecting shuttles
TIME_STEP = 5.0  # Increased time step for faster simulation

class CelestialObject:
    def __init__(self, x: float, y: float, vx: float = 0, vy: float = 0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        
    @property
    def position(self) -> Tuple[float, float]:
        return (self.x, self.y)
    
    @property
    def velocity(self) -> Tuple[float, float]:
        return (self.vx, self.vy)
    
    def distance_to(self, other: 'CelestialObject') -> float:
        return np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def angle_to(self, other: 'CelestialObject') -> float:
        return math.atan2(other.y - self.y, other.x - self.x)

class Satellite(CelestialObject):
    def __init__(self, orbit_radius: float, angle: float, speed: float):
        # Convert polar to Cartesian coordinates
        x = orbit_radius * math.cos(angle)
        y = orbit_radius * math.sin(angle)
        
        # Calculate orbital velocity
        orbital_speed = speed
        vx = -orbital_speed * math.sin(angle)
        vy = orbital_speed * math.cos(angle)
        
        super().__init__(x, y, vx, vy)
        self.orbit_radius = orbit_radius
        self.angle = angle
        self.speed = speed
        self.is_refueled = False
    
    def update_position(self):
        # Update angle based on angular velocity
        angular_velocity = self.speed / self.orbit_radius
        self.angle += angular_velocity * TIME_STEP
        
        # Update Cartesian coordinates
        self.x = self.orbit_radius * math.cos(self.angle)
        self.y = self.orbit_radius * math.sin(self.angle)
        
        # Update velocity components
        self.vx = -self.speed * math.sin(self.angle)
        self.vy = self.speed * math.cos(self.angle)

class RefuelShuttle(CelestialObject):
    def __init__(self, x: float, y: float, orbit_radius: float, vx: float = 0, vy: float = 0):
        super().__init__(x, y, vx, vy)
        self.orbit_radius = orbit_radius
        self.is_deployed = True
        self.is_collected = False
        
        # Calculate angle in orbit
        self.angle = math.atan2(y, x)
        
        # Calculate orbital velocity
        orbital_speed = np.sqrt(G * PLANET_MASS / (orbit_radius * 1000))  # Convert km to m
        self.speed = orbital_speed / 1000  # Convert m/s to km/s
        
        # Set velocity components for circular orbit
        self.vx = -self.speed * math.sin(self.angle)
        self.vy = self.speed * math.cos(self.angle)
    
    def update_position(self):
        if not self.is_collected:
            # Update angle based on angular velocity
            angular_velocity = self.speed / self.orbit_radius
            self.angle += angular_velocity * TIME_STEP
            
            # Update Cartesian coordinates
            self.x = self.orbit_radius * math.cos(self.angle)
            self.y = self.orbit_radius * math.sin(self.angle)
            
            # Update velocity components
            self.vx = -self.speed * math.sin(self.angle)
            self.vy = self.speed * math.cos(self.angle)

class LaunchPad:
    def __init__(self, angle: float):
        self.angle = angle
        self.x = PLANET_RADIUS * math.cos(angle)
        self.y = PLANET_RADIUS * math.sin(angle)
    
    @property
    def position(self) -> Tuple[float, float]:
        return (self.x, self.y)

class Tanker(CelestialObject):
    def __init__(self, launch_pad: LaunchPad):
        super().__init__(launch_pad.x, launch_pad.y)
        self.fuel = MAX_FUEL
        self.shuttles: List[RefuelShuttle] = []
        self.trajectory: List[Tuple[float, float]] = [(launch_pad.x, launch_pad.y)]
        self.current_target = None
        self.is_returning = False
        self.is_in_orbit = False
        self.current_orbit_radius = None
        self.angle = launch_pad.angle
        self.speed = 0
        self.waiting = False
        self.wait_time = 0
        
    def move_to(self, target_x: float, target_y: float):
        # Simple linear movement towards the target
        dx = target_x - self.x
        dy = target_y - self.y
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            step_size = min(5, distance)  # Increased step size for faster movement
            self.x += (dx / distance) * step_size
            self.y += (dy / distance) * step_size
            self.fuel -= step_size * FUEL_CONSUMPTION_RATE
            
        self.trajectory.append((self.x, self.y))
    
    def enter_orbit(self, orbit_radius: float):
        # Calculate distance from planet center
        r = np.sqrt(self.x**2 + self.y**2)
        
        # If close to desired orbit, adjust to perfect circle
        if abs(r - orbit_radius) < 20:  # Increased threshold
            # Calculate current angle
            current_angle = math.atan2(self.y, self.x)
            
            # Set position to exact orbit
            self.x = orbit_radius * math.cos(current_angle)
            self.y = orbit_radius * math.sin(current_angle)
            
            # Calculate orbital velocity
            orbital_speed = np.sqrt(G * PLANET_MASS / (orbit_radius * 1000))  # Convert km to m
            self.speed = orbital_speed / 1000  # Convert m/s to km/s
            
            # Set velocity components for circular orbit
            self.vx = -self.speed * math.sin(current_angle)
            self.vy = self.speed * math.cos(current_angle)
            
            self.current_orbit_radius = orbit_radius
            self.angle = current_angle
            self.is_in_orbit = True
            return True
        
        # Otherwise, move toward the orbit
        target_x = (self.x / r) * orbit_radius
        target_y = (self.y / r) * orbit_radius
        self.move_to(target_x, target_y)
        return False
    
    def update_position_in_orbit(self):
        if self.is_in_orbit and not self.waiting:
            # Update angle based on angular velocity
            angular_velocity = self.speed / self.current_orbit_radius
            self.angle += angular_velocity * TIME_STEP
            
            # Update Cartesian coordinates
            self.x = self.current_orbit_radius * math.cos(self.angle)
            self.y = self.current_orbit_radius * math.sin(self.angle)
            
            # Update velocity components
            self.vx = -self.speed * math.sin(self.angle)
            self.vy = self.speed * math.cos(self.angle)
            
            self.trajectory.append((self.x, self.y))

    def perform_hohmann_transfer(self, target_orbit: float):
        if not self.is_in_orbit:
            return False
            
        r1 = self.current_orbit_radius
        r2 = target_orbit
        
        # Calculate delta-v for first burn (departure)
        v1 = self.speed
        v_transfer_periapsis = v1 * np.sqrt(2 * r2 / (r1 + r2))
        delta_v1 = abs(v_transfer_periapsis - v1)
        
        # Apply first burn
        self.speed = v_transfer_periapsis
        self.vx = -self.speed * math.sin(self.angle)
        self.vy = self.speed * math.cos(self.angle)
        
        # Simulate half-elliptical transfer
        # Using simplified version for faster simulation
        transfer_time = np.pi * np.sqrt(((r1 + r2) / 2)**3 / (G * PLANET_MASS / 1e9))
        steps = max(3, int(transfer_time / TIME_STEP))  # Reduced steps for faster simulation
        
        # Simplified transfer (in a real simulation, would solve Kepler's equations)
        for _ in range(steps):
            # Update angle - this is a simplification
            transfer_angular_velocity = self.speed / ((r1 + r2) / 2)
            self.angle += transfer_angular_velocity * TIME_STEP
            
            # Gradually increase radius
            radius_increment = (r2 - r1) / steps
            current_radius = self.current_orbit_radius + radius_increment
            
            # Update position
            self.x = current_radius * math.cos(self.angle)
            self.y = current_radius * math.sin(self.angle)
            self.trajectory.append((self.x, self.y))
            
            self.current_orbit_radius = current_radius
        
        # Calculate delta-v for second burn (insertion)
        v2_orbit = np.sqrt(G * PLANET_MASS / (r2 * 1000)) / 1000
        v_transfer_apoapsis = v1 * np.sqrt(2 * r1 / (r1 + r2))
        delta_v2 = abs(v2_orbit - v_transfer_apoapsis)
        
        # Apply second burn
        self.speed = v2_orbit
        self.vx = -self.speed * math.sin(self.angle)
        self.vy = self.speed * math.cos(self.angle)
        
        # Update position to be exactly on the target orbit
        self.x = r2 * math.cos(self.angle)
        self.y = r2 * math.sin(self.angle)
        self.current_orbit_radius = r2
        
        # Consume fuel for both delta-vs
        total_delta_v = delta_v1 + delta_v2
        self.fuel -= total_delta_v * FUEL_CONSUMPTION_RATE * 10  # Reduced for better efficiency
        
        return True
    
    def deploy_shuttle(self):
        if self.is_in_orbit:
            shuttle = RefuelShuttle(
                self.x, self.y, 
                self.current_orbit_radius,
                self.vx, self.vy
            )
            self.shuttles.append(shuttle)
            return shuttle
        return None
    
    def wait_in_orbit(self, time: int):
        self.waiting = True
        self.wait_time = time
    
    def update_wait_time(self):
        if self.waiting and self.wait_time > 0:
            self.wait_time -= TIME_STEP
            if self.wait_time <= 0:
                self.waiting = False
                self.wait_time = 0

class SpaceSimulation:
    def __init__(self):
        self.planet_radius = PLANET_RADIUS
        self.launch_pads: List[LaunchPad] = []
        self.orbits: List[float] = []
        self.satellites: List[Satellite] = []
        self.tanker: Optional[Tanker] = None
        self.best_pad: Optional[LaunchPad] = None
        self.best_time = float('inf')
        self.best_trajectory: List[Tuple[float, float]] = []
        self.simulation_time = 0
        
    def add_launch_pad(self, angle: float):
        self.launch_pads.append(LaunchPad(angle))
        
    def add_orbit(self, radius: float):
        self.orbits.append(radius)
        
    def add_satellite(self, orbit_radius: float, angle: float, speed: float):
        # Verify orbit exists
        if orbit_radius not in self.orbits:
            self.add_orbit(orbit_radius)
        self.satellites.append(Satellite(orbit_radius, angle, speed))
        
    def calculate_best_pad(self):
        best_pad = None
        best_time = float('inf')
        best_trajectory = []
        
        for pad in self.launch_pads:
            time, trajectory = self.simulate_mission(pad)
            if time < best_time:
                best_time = time
                best_pad = pad
                best_trajectory = trajectory
                
        self.best_pad = best_pad
        self.best_time = best_time
        self.best_trajectory = best_trajectory
        
        return best_pad, best_time
    
    def simulate_mission(self, launch_pad: LaunchPad) -> Tuple[float, List[Tuple[float, float]]]:
        # Create a tanker at the launch pad
        tanker = Tanker(launch_pad)
        
        # Create a copy of satellites for simulation
        satellites = [Satellite(sat.orbit_radius, sat.angle, sat.speed) for sat in self.satellites]
        
        # Sort orbits by distance
        sorted_orbits = sorted(self.orbits)
        
        time = 0
        max_time = 300  # Reduced max time
        
        # Launch and enter first orbit
        while not tanker.is_in_orbit and time < max_time:
            if tanker.enter_orbit(sorted_orbits[0]):
                tanker.is_in_orbit = True
            
            # Update satellite positions
            for sat in satellites:
                sat.update_position()
                
            time += TIME_STEP
            
        # Visit each orbit, deploy shuttles, and refuel satellites
        for i, orbit_radius in enumerate(sorted_orbits):
            # If not in the target orbit, perform transfer
            if tanker.current_orbit_radius != orbit_radius:
                tanker.perform_hohmann_transfer(orbit_radius)
                
            # Deploy shuttle for satellites in this orbit
            orbit_satellites = [sat for sat in satellites if sat.orbit_radius == orbit_radius]
            
            # Continue orbiting until all satellites in this orbit are refueled
            while any(not sat.is_refueled for sat in orbit_satellites) and time < max_time:
                # Deploy a shuttle if we haven't yet
                if not any(shuttle.orbit_radius == orbit_radius and not shuttle.is_collected 
                           for shuttle in tanker.shuttles):
                    shuttle = tanker.deploy_shuttle()
                
                # Update positions
                tanker.update_position_in_orbit()
                
                # Update all shuttles
                for shuttle in tanker.shuttles:
                    shuttle.update_position()
                
                # Update all satellites
                for sat in satellites:
                    sat.update_position()
                
                # Check for refueling
                for shuttle in tanker.shuttles:
                    if shuttle.orbit_radius == orbit_radius and not shuttle.is_collected:
                        for sat in orbit_satellites:
                            if not sat.is_refueled and shuttle.distance_to(sat) < REFUEL_THRESHOLD:
                                sat.is_refueled = True
                
                time += TIME_STEP
                
                # Break early if all refueled
                if all(sat.is_refueled for sat in orbit_satellites):
                    break
        
        # Return to planet
        tanker.is_returning = True
        
        # Collect all shuttles
        for orbit_radius in reversed(sorted_orbits):
            # If not in the target orbit, perform transfer
            if tanker.current_orbit_radius != orbit_radius:
                tanker.perform_hohmann_transfer(orbit_radius)
            
            # Find shuttles in this orbit
            orbit_shuttles = [s for s in tanker.shuttles if s.orbit_radius == orbit_radius and not s.is_collected]
            
            # Collect all shuttles in this orbit
            while any(not shuttle.is_collected for shuttle in orbit_shuttles) and time < max_time:
                tanker.update_position_in_orbit()
                
                # Update all shuttles
                for shuttle in tanker.shuttles:
                    shuttle.update_position()
                
                # Check for collection
                for shuttle in orbit_shuttles:
                    if tanker.distance_to(shuttle) < COLLECTION_THRESHOLD:
                        shuttle.is_collected = True
                
                time += TIME_STEP
                
                # Break early if all collected
                if all(shuttle.is_collected for shuttle in orbit_shuttles):
                    break
        
        # Return to surface (close to launch pad)
        while tanker.distance_to(launch_pad) > 10 and time < max_time:
            tanker.move_to(launch_pad.x, launch_pad.y)
            time += TIME_STEP
            
        # Store the remaining fuel amount for later use
        self.remaining_fuel = tanker.fuel
        
        return time, tanker.trajectory
    
    def run_real_simulation(self):
        if self.best_pad is None:
            self.calculate_best_pad()
            
        # Create the tanker at the best pad
        self.tanker = Tanker(self.best_pad)
        
        # Create the animation
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_xlim(-self.orbits[-1] * 1.1, self.orbits[-1] * 1.1)
        ax.set_ylim(-self.orbits[-1] * 1.1, self.orbits[-1] * 1.1)
        ax.set_aspect('equal')
        
        # Draw the planet
        planet = Circle((0, 0), self.planet_radius, color='blue', alpha=0.7)
        ax.add_patch(planet)
        
        # Draw the orbits
        for orbit_radius in self.orbits:
            orbit = Circle((0, 0), orbit_radius, fill=False, color='gray', linestyle='--')
            ax.add_patch(orbit)
        
        # Draw the launch pads
        pad_markers = []
        for pad in self.launch_pads:
            marker, = ax.plot([pad.x], [pad.y], 'ro', markersize=8)
            pad_markers.append(marker)
        
        # Highlight the best pad
        if self.best_pad:
            best_pad_marker, = ax.plot([self.best_pad.x], [self.best_pad.y], 'go', markersize=10)
        
        # Draw the satellites
        satellite_markers = []
        for sat in self.satellites:
            marker, = ax.plot([sat.x], [sat.y], 'yo', markersize=6, alpha=0.7)
            satellite_markers.append((sat, marker))
        
        # Tanker marker
        tanker_marker, = ax.plot([self.tanker.x], [self.tanker.y], 'ko', markersize=8)
        
        # Shuttle markers (initially empty)
        shuttle_markers = []
        
        # Trajectory line (empty initially)
        trajectory_line, = ax.plot([], [], 'r-', alpha=0.5, linewidth=1)
        trajectory_x = []
        trajectory_y = []
        
        def init():
            trajectory_line.set_data([], [])
            tanker_marker.set_data([self.tanker.x], [self.tanker.y])
            for sat, marker in satellite_markers:
                marker.set_data([sat.x], [sat.y])
            return [trajectory_line, tanker_marker] + [marker for _, marker in satellite_markers]
        
        def animate(i):
            # Advance simulation time
            self.simulation_time += TIME_STEP
            
            # Simulate tanker movement based on mission logic
            if not self.tanker.is_in_orbit and self.tanker.current_orbit_radius is None:
                # Launch and enter first orbit
                self.tanker.enter_orbit(min(self.orbits))
            else:
                # Tanker is in orbit
                if self.tanker.waiting:
                    self.tanker.update_wait_time()
                else:
                    # Check if we need to move to another orbit
                    current_orbit_idx = self.orbits.index(self.tanker.current_orbit_radius)
                    
                    # If all satellites in current orbit are refueled, move to next orbit
                    current_orbit_sats = [sat for sat, _ in satellite_markers 
                                         if sat.orbit_radius == self.tanker.current_orbit_radius]
                    
                    if all(sat.is_refueled for sat in current_orbit_sats):
                        # If there are more orbits, move to the next one
                        if current_orbit_idx < len(self.orbits) - 1 and not self.tanker.is_returning:
                            next_orbit = self.orbits[current_orbit_idx + 1]
                            self.tanker.perform_hohmann_transfer(next_orbit)
                        elif self.tanker.is_returning and current_orbit_idx > 0:
                            # Going back down in orbits
                            prev_orbit = self.orbits[current_orbit_idx - 1]
                            self.tanker.perform_hohmann_transfer(prev_orbit)
                        elif self.tanker.is_returning and current_orbit_idx == 0:
                            # Return to launch pad
                            if self.tanker.distance_to(self.best_pad) > 10:
                                self.tanker.move_to(self.best_pad.x, self.best_pad.y)
                                self.tanker.is_in_orbit = False
                    else:
                        # We're still working on this orbit
                        self.tanker.update_position_in_orbit()
                        
                        # Check if we should deploy a shuttle
                        if not any(s.orbit_radius == self.tanker.current_orbit_radius and not s.is_collected 
                                for s in self.tanker.shuttles):
                            shuttle = self.tanker.deploy_shuttle()
                            if shuttle:
                                marker, = ax.plot([shuttle.x], [shuttle.y], 'go', markersize=5)
                                shuttle_markers.append((shuttle, marker))
            
            # Update satellite positions
            for sat, marker in satellite_markers:
                sat.update_position()
                marker.set_data([sat.x], [sat.y])
                
                # Update satellite color based on refuel status
                if sat.is_refueled:
                    marker.set_color('green')
                else:
                    marker.set_color('lightgreen')
            
            # Update shuttle positions
            for shuttle, marker in shuttle_markers:
                if not shuttle.is_collected:
                    shuttle.update_position()
                    marker.set_data([shuttle.x], [shuttle.y])
                else:
                    marker.set_visible(False)
            
            # Update tanker position
            tanker_marker.set_data([self.tanker.x], [self.tanker.y])
            
            # Check for refueling
            for shuttle, _ in shuttle_markers:
                if not shuttle.is_collected:
                    for sat, _ in satellite_markers:
                        if not sat.is_refueled and shuttle.orbit_radius == sat.orbit_radius and shuttle.distance_to(sat) < REFUEL_THRESHOLD:
                            sat.is_refueled = True
            
            # Check for shuttle collection
            if self.tanker.is_returning:
                for shuttle, marker in shuttle_markers:
                    if not shuttle.is_collected and self.tanker.distance_to(shuttle) < COLLECTION_THRESHOLD:
                        shuttle.is_collected = True
                        marker.set_visible(False)
            
            # Check if all satellites are refueled
            if all(sat.is_refueled for sat, _ in satellite_markers) and not self.tanker.is_returning:
                self.tanker.is_returning = True
            
            # Update trajectory
            trajectory_x.append(self.tanker.x)
            trajectory_y.append(self.tanker.y)
            trajectory_line.set_data(trajectory_x, trajectory_y)
            
            return [trajectory_line, tanker_marker] + [marker for _, marker in satellite_markers] + [marker for _, marker in shuttle_markers]
        
        # Set up animation
        ani = animation.FuncAnimation(
            fig, animate, init_func=init,
            frames=200, interval=20, blit=True
        )
        
        plt.title(f"Space Refueling Mission - Best Pad at Angle: {self.best_pad.angle:.2f} radians")
        plt.grid(True)
        
        # Save the animation as a gif
        try:
            ani.save('space_refueling_mission.gif', writer='pillow', fps=30)
            print("Animation saved as space_refueling_mission.gif")
        except Exception as e:
            print(f"Could not save animation: {e}")
        
        plt.show()
        
        return ani

def run_test():
    # Create simulation
    sim = SpaceSimulation()
    
    # Add launch pads at different positions
    for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
        sim.add_launch_pad(angle)
    
    # Add orbits with reasonable spacing
    for radius in [10000, 15000, 20000, 25000]:
        sim.add_orbit(radius)
    
    # Add satellites to different orbits
    for orbit_radius in sim.orbits:
        for angle in np.linspace(0, 2*np.pi, 3, endpoint=False):
            # Calculate appropriate orbital speed for this radius
            orbital_speed = np.sqrt(G * PLANET_MASS / (orbit_radius * 1000)) / 1000  # Convert to km/s
            sim.add_satellite(orbit_radius, angle, orbital_speed * 0.8)  # Slightly slower for visibility
    
    # Calculate the best pad
    best_pad, best_time = sim.calculate_best_pad()
    print(f"Best launch pad is at angle {best_pad.angle:.2f} radians")
    print(f"Mission time: {best_time:.2f} time units")
    
    if hasattr(sim, 'remaining_fuel'):
        print(f"Fuel used: {MAX_FUEL - sim.remaining_fuel:.2f} units")
    else:
        print("Fuel information not available (mission may not have completed)")
    
    # Run animation
    sim.run_real_simulation()

if __name__ == "__main__":
    run_test()
