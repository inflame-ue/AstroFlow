import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
import random
from typing import List, Tuple, Dict
import math

class Orbit:
    def __init__(self, radius: float):
        self.radius = radius
        self.satellites = []
    
    def add_satellite(self, angle: float, speed: float):
        """Add a satellite to this orbit with initial angle and speed."""
        self.satellites.append({
            'angle': angle,  # radians
            'speed': speed,  # radians per time unit
            'last_refuel_time': 0
        })
    
    def update_satellites(self, time_step: float):
        """Update positions of all satellites in this orbit."""
        for sat in self.satellites:
            sat['angle'] = (sat['angle'] + sat['speed'] * time_step) % (2 * np.pi)

class LaunchPad:
    def __init__(self, radius: float, angle: float):
        self.radius = radius  # Distance from planet center
        self.angle = angle    # Position angle in radians
        self.x = radius * np.cos(angle)
        self.y = radius * np.sin(angle)
    
    def get_position(self):
        return (self.x, self.y)

class RefuelMission:
    def __init__(self, launch_pad: LaunchPad, orbits: List[Orbit], max_time: float = 1000.0):
        self.launch_pad = launch_pad
        self.orbits = orbits
        self.max_time = max_time
        
        # Mission parameters
        self.ascent_speed = 0.5  # Units per time step
        self.descent_speed = 0.7  # Units per time step
        self.orbital_transfer_speed = 0.4  # Units per time step
        
        # For tracking and visualization
        self.best_time = float('inf')
        self.best_schedule = []
        self.best_trajectory = []
    
    def calculate_transfer_time(self, orbit1_radius: float, angle1: float, 
                                orbit2_radius: float, angle2: float):
        """Calculate time to transfer between two orbital positions."""
        # Simplified orbital transfer - direct path
        dx = orbit2_radius * np.cos(angle2) - orbit1_radius * np.cos(angle1)
        dy = orbit2_radius * np.sin(angle2) - orbit1_radius * np.sin(angle1)
        distance = np.sqrt(dx**2 + dy**2)
        return distance / self.orbital_transfer_speed
    
    def calculate_ascent_time(self, target_orbit: Orbit, target_angle: float):
        """Calculate time to ascend from launch pad to target orbit at target angle."""
        pad_x, pad_y = self.launch_pad.get_position()
        target_x = target_orbit.radius * np.cos(target_angle)
        target_y = target_orbit.radius * np.sin(target_angle)
        
        distance = np.sqrt((target_x - pad_x)**2 + (target_y - pad_y)**2)
        return distance / self.ascent_speed
    
    def calculate_descent_time(self, orbit_radius: float, angle: float):
        """Calculate time to descend from orbit back to launch pad."""
        pad_x, pad_y = self.launch_pad.get_position()
        orbit_x = orbit_radius * np.cos(angle)
        orbit_y = orbit_radius * np.sin(angle)
        
        distance = np.sqrt((orbit_x - pad_x)**2 + (orbit_y - pad_y)**2)
        return distance / self.descent_speed
    
    def find_optimal_refuel_sequence(self):
        """Find the optimal sequence to refuel all satellites with minimum time."""
        # Starting at the pad
        current_location = ("pad", 0, self.launch_pad.angle)
        current_time = 0
        path = [current_location]
        trajectory = [(self.launch_pad.x, self.launch_pad.y, current_time)]
        
        # Copy satellites to track which ones we've refueled
        satellites_to_refuel = []
        for i, orbit in enumerate(self.orbits):
            for j, sat in enumerate(orbit.satellites):
                satellites_to_refuel.append({
                    'orbit_idx': i,
                    'sat_idx': j,
                    'refueled': False
                })
        
        # Continue until all satellites are refueled
        while any(not sat['refueled'] for sat in satellites_to_refuel):
            best_sat = None
            best_wait_time = 0
            best_total_time = float('inf')
            best_intercept_angle = 0
            
            for sat_info in satellites_to_refuel:
                if sat_info['refueled']:
                    continue
                    
                orbit_idx = sat_info['orbit_idx']
                sat_idx = sat_info['sat_idx']
                orbit = self.orbits[orbit_idx]
                satellite = orbit.satellites[sat_idx]
                
                # Try different wait times to find optimal interception
                for wait_time in np.linspace(0, 20, 40):  # Try various wait times
                    intercept_time = current_time + wait_time
                    # Calculate satellite position at intercept time
                    intercept_angle = (satellite['angle'] + satellite['speed'] * wait_time) % (2 * np.pi)
                    
                    transfer_time = 0
                    if current_location[0] == "pad":
                        # From pad to orbit
                        transfer_time = self.calculate_ascent_time(orbit, intercept_angle)
                    else:
                        # From one orbit to another
                        prev_orbit_radius = self.orbits[current_location[1]].radius
                        prev_angle = current_location[2]
                        transfer_time = self.calculate_transfer_time(
                            prev_orbit_radius, prev_angle,
                            orbit.radius, intercept_angle
                        )
                    
                    total_time = wait_time + transfer_time
                    if total_time < best_total_time:
                        best_sat = sat_info
                        best_wait_time = wait_time
                        best_total_time = total_time
                        best_intercept_angle = intercept_angle
            
            # Update with best satellite found
            if best_sat:
                # Wait if needed
                if best_wait_time > 0:
                    # If waiting in orbit, add orbital positions during wait
                    if current_location[0] == "orbit":
                        orbit_idx = current_location[1]
                        orbit = self.orbits[orbit_idx]
                        steps = math.ceil(best_wait_time)
                        for t in range(1, steps + 1):
                            wait_proportion = min(t, best_wait_time) / best_wait_time
                            wait_angle = (current_location[2] + wait_proportion * orbit.satellites[0]['speed'] * best_wait_time) % (2 * np.pi)
                            wait_x = orbit.radius * np.cos(wait_angle)
                            wait_y = orbit.radius * np.sin(wait_angle)
                            trajectory.append((wait_x, wait_y, current_time + wait_proportion * best_wait_time))
                
                current_time += best_total_time
                best_sat['refueled'] = True
                
                # Record the path and trajectory
                orbit_idx = best_sat['orbit_idx']
                orbit = self.orbits[orbit_idx]
                
                # Add trajectory points for transfer
                if current_location[0] == "pad":
                    # From pad to orbit
                    steps = 10  # Number of points in trajectory
                    pad_x, pad_y = self.launch_pad.get_position()
                    target_x = orbit.radius * np.cos(best_intercept_angle)
                    target_y = orbit.radius * np.sin(best_intercept_angle)
                    for i in range(1, steps + 1):
                        t = i / steps
                        x = pad_x + t * (target_x - pad_x)
                        y = pad_y + t * (target_y - pad_y)
                        point_time = current_time - best_total_time + t * self.calculate_ascent_time(orbit, best_intercept_angle)
                        trajectory.append((x, y, point_time))
                else:
                    # From orbit to orbit
                    steps = 10
                    prev_orbit_idx = current_location[1]
                    prev_orbit = self.orbits[prev_orbit_idx]
                    prev_angle = current_location[2]
                    
                    start_x = prev_orbit.radius * np.cos(prev_angle)
                    start_y = prev_orbit.radius * np.sin(prev_angle)
                    end_x = orbit.radius * np.cos(best_intercept_angle)
                    end_y = orbit.radius * np.sin(best_intercept_angle)
                    
                    for i in range(1, steps + 1):
                        t = i / steps
                        x = start_x + t * (end_x - start_x)
                        y = start_y + t * (end_y - start_y)
                        transfer_time = self.calculate_transfer_time(
                            prev_orbit.radius, prev_angle,
                            orbit.radius, best_intercept_angle
                        )
                        point_time = current_time - best_total_time + t * transfer_time
                        trajectory.append((x, y, point_time))
                
                current_location = ("orbit", orbit_idx, best_intercept_angle)
                path.append(current_location)
            else:
                break
        
        # Return to launch pad
        if current_location[0] == "orbit":
            orbit_idx = current_location[1]
            orbit = self.orbits[orbit_idx]
            angle = current_location[2]
            
            descent_time = self.calculate_descent_time(orbit.radius, angle)
            current_time += descent_time
            
            # Add trajectory points for descent
            steps = 10
            start_x = orbit.radius * np.cos(angle)
            start_y = orbit.radius * np.sin(angle)
            pad_x, pad_y = self.launch_pad.get_position()
            
            for i in range(1, steps + 1):
                t = i / steps
                x = start_x + t * (pad_x - start_x)
                y = start_y + t * (pad_y - start_y)
                point_time = current_time - descent_time + t * descent_time
                trajectory.append((x, y, point_time))
            
            path.append(("pad", 0, self.launch_pad.angle))
        
        self.best_time = current_time
        self.best_schedule = path
        self.best_trajectory = trajectory
        return current_time, path, trajectory

class PlanetarySystem:
    def __init__(self, planet_radius: float):
        self.planet_radius = planet_radius
        self.orbits = []
        self.launch_pads = []
        
    def add_orbit(self, radius: float):
        """Add an orbit at specified radius."""
        orbit = Orbit(radius)
        self.orbits.append(orbit)
        return orbit
    
    def add_launch_pad(self, radius: float, angle: float):
        """Add a launch pad at specified polar coordinates."""
        pad = LaunchPad(radius, angle)
        self.launch_pads.append(pad)
        return pad
    
    def find_best_launch_pad(self):
        """Find the best launch pad with minimum refuel mission time."""
        best_pad = None
        best_time = float('inf')
        best_mission = None
        
        for pad in self.launch_pads:
            mission = RefuelMission(pad, self.orbits)
            time, path, trajectory = mission.find_optimal_refuel_sequence()
            
            if time < best_time:
                best_time = time
                best_pad = pad
                best_mission = mission
                
        return best_pad, best_time, best_mission
    
    def visualize_system(self):
        """Create a static visualization of the system."""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Draw planet
        planet = plt.Circle((0, 0), self.planet_radius, color='lightblue')
        ax.add_patch(planet)
        
        # Draw orbits
        for orbit in self.orbits:
            circle = plt.Circle((0, 0), orbit.radius, fill=False, color='gray', linestyle='--')
            ax.add_patch(circle)
            
            # Draw satellites
            for sat in orbit.satellites:
                x = orbit.radius * np.cos(sat['angle'])
                y = orbit.radius * np.sin(sat['angle'])
                satellite = plt.Circle((x, y), self.planet_radius * 0.1, color='gray')
                ax.add_patch(satellite)
        
        # Draw launch pads
        for pad in self.launch_pads:
            x, y = pad.get_position()
            launch_pad = plt.Circle((x, y), self.planet_radius * 0.15, color='red')
            ax.add_patch(launch_pad)
        
        # Set axis limits and properties
        limit = max(orbit.radius for orbit in self.orbits) * 1.1
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_aspect('equal')
        ax.grid(True)
        plt.title('Planetary System with Orbits, Satellites, and Launch Pads')
        plt.show()
    
    def animate_mission(self, mission: RefuelMission, save_animation: bool = False):
        """Create an animation of the refuel mission."""
        trajectory = mission.best_trajectory
        if not trajectory:
            print("No trajectory to animate. Run find_optimal_refuel_sequence first.")
            return
        
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Time range for animation
        start_time = trajectory[0][2]
        end_time = trajectory[-1][2]
        
        def update(frame):
            ax.clear()
            time = start_time + frame * (end_time - start_time) / 100
            
            # Draw planet
            planet = plt.Circle((0, 0), self.planet_radius, color='lightblue')
            ax.add_patch(planet)
            
            # Draw orbits
            for orbit in self.orbits:
                circle = plt.Circle((0, 0), orbit.radius, fill=False, color='gray', linestyle='--')
                ax.add_patch(circle)
            
            # Draw satellites at current time
            for i, orbit in enumerate(self.orbits):
                for j, sat in enumerate(orbit.satellites):
                    # Calculate satellite position at current time
                    current_angle = (sat['angle'] + sat['speed'] * (time - start_time)) % (2 * np.pi)
                    x = orbit.radius * np.cos(current_angle)
                    y = orbit.radius * np.sin(current_angle)
                    satellite = plt.Circle((x, y), self.planet_radius * 0.1, color='gray')
                    ax.add_patch(satellite)
            
            # Draw launch pads
            for pad in self.launch_pads:
                x, y = pad.get_position()
                launch_pad = plt.Circle((x, y), self.planet_radius * 0.15, color='red')
                ax.add_patch(launch_pad)
            
            # Draw refuel tanker
            # Find position at current time by interpolating trajectory
            pos_x, pos_y = None, None
            prev_t = None
            for point in trajectory:
                x, y, t = point
                if t >= time:
                    if prev_t is not None:
                        # Interpolate between previous and current point
                        prev_x, prev_y, prev_t = prev_t
                        ratio = (time - prev_t) / (t - prev_t) if t != prev_t else 0
                        pos_x = prev_x + ratio * (x - prev_x)
                        pos_y = prev_y + ratio * (y - prev_y)
                    else:
                        pos_x, pos_y = x, y
                    break
                prev_t = (x, y, t)
            
            if pos_x is not None and pos_y is not None:
                tanker = plt.Circle((pos_x, pos_y), self.planet_radius * 0.2, color='green')
                ax.add_patch(tanker)
            
            # Draw trajectory path
            path_x = [point[0] for point in trajectory if point[2] <= time]
            path_y = [point[1] for point in trajectory if point[2] <= time]
            if path_x and path_y:
                ax.plot(path_x, path_y, 'g-', alpha=0.5)
            
            # Set axis properties
            limit = max(orbit.radius for orbit in self.orbits) * 1.1
            ax.set_xlim(-limit, limit)
            ax.set_ylim(-limit, limit)
            ax.set_aspect('equal')
            ax.grid(True)
            ax.set_title(f'Refuel Mission Simulation (Time: {time:.1f})')
            
            return ax
        
        ani = FuncAnimation(fig, update, frames=100, interval=100, blit=False)
        
        if save_animation:
            ani.save('refuel_mission.gif', writer='pillow')
        
        plt.tight_layout()
        plt.show()

def run_simulation():
    # Create a planetary system
    system = PlanetarySystem(planet_radius=1.0)
    
    # Add orbits
    orbit1 = system.add_orbit(radius=3.0)
    orbit2 = system.add_orbit(radius=5.0)
    orbit3 = system.add_orbit(radius=7.0)
    
    # Add satellites to orbits
    # Orbit 1 satellites
    orbit1.add_satellite(angle=0.5, speed=0.05)
    orbit1.add_satellite(angle=2.0, speed=-0.03)
    orbit1.add_satellite(angle=4.0, speed=0.02)
    
    # Orbit 2 satellites
    orbit2.add_satellite(angle=1.0, speed=0.04)
    orbit2.add_satellite(angle=3.0, speed=-0.02)
    
    # Orbit 3 satellites
    orbit3.add_satellite(angle=0.0, speed=0.01)
    orbit3.add_satellite(angle=2.5, speed=-0.015)
    
    # Add launch pads
    for angle in np.linspace(0, 2*np.pi, 6, endpoint=False):
        system.add_launch_pad(radius=system.planet_radius, angle=angle)
    
    # Visualize the system
    system.visualize_system()
    
    # Find the best launch pad
    best_pad, best_time, best_mission = system.find_best_launch_pad()
    print(f"Best launch pad: radius={best_pad.radius}, angle={best_pad.angle*180/np.pi:.1f}°")
    print(f"Best mission time: {best_time:.2f} time units")
    
    # Animate the best mission
    system.animate_mission(best_mission)

def run_test_cases():
    """Run various test cases to validate the algorithm."""
    print("Running test cases...")
    
    # Test case 1: Simple system with one orbit and one satellite
    def test_case_1():
        system = PlanetarySystem(planet_radius=1.0)
        orbit = system.add_orbit(radius=4.0)
        orbit.add_satellite(angle=0.0, speed=0.1)
        
        # Add pads at opposite sides
        system.add_launch_pad(radius=system.planet_radius, angle=0.0)
        system.add_launch_pad(radius=system.planet_radius, angle=np.pi)
        
        best_pad, best_time, _ = system.find_best_launch_pad()
        print(f"Test Case 1: Best pad angle = {best_pad.angle*180/np.pi:.1f}°, Time = {best_time:.2f}")
        return best_pad.angle*180/np.pi < 90  # Expect the pad at 0 degrees to be better
    
    # Test case 2: Multiple orbits with satellites in same direction
    def test_case_2():
        system = PlanetarySystem(planet_radius=1.0)
        orbit1 = system.add_orbit(radius=3.0)
        orbit2 = system.add_orbit(radius=6.0)
        
        orbit1.add_satellite(angle=0.0, speed=0.05)
        orbit2.add_satellite(angle=0.0, speed=0.03)
        
        # Add pads at different points
        for angle in np.linspace(0, 2*np.pi, 4, endpoint=False):
            system.add_launch_pad(radius=system.planet_radius, angle=angle)
        
        best_pad, best_time, _ = system.find_best_launch_pad()
        print(f"Test Case 2: Best pad angle = {best_pad.angle*180/np.pi:.1f}°, Time = {best_time:.2f}")
        return best_time < float('inf')
    
    # Test case 3: Complex system with multiple orbits and satellites
    def test_case_3():
        system = PlanetarySystem(planet_radius=1.0)
        
        # Add orbits at different distances
        orbits = [system.add_orbit(radius=r) for r in [2.5, 4.0, 6.0, 8.0]]
        
        # Add satellites with different speeds and positions
        for i, orbit in enumerate(orbits):
            for j in range(i+1):
                angle = j * 2*np.pi/(i+1)
                speed = 0.05 * (-1)**(i+j)  # Alternate directions
                orbit.add_satellite(angle=angle, speed=speed)
        
        # Add 8 launch pads evenly distributed
        for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
            system.add_launch_pad(radius=system.planet_radius, angle=angle)
        
        best_pad, best_time, best_mission = system.find_best_launch_pad()
        print(f"Test Case 3: Best pad angle = {best_pad.angle*180/np.pi:.1f}°, Time = {best_time:.2f}")
        
        # Visualize the best mission
        system.animate_mission(best_mission)
        return True
    
    # Run all test cases
    tests = [test_case_1, test_case_2, test_case_3]
    results = [test() for test in tests]
    
    print(f"Test results: {results.count(True)}/{len(results)} tests passed")

if __name__ == "__main__":
    # Run the test cases
    run_test_cases()
    
    # Run the main simulation
    run_simulation()
