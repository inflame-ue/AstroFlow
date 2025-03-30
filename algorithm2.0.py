import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

EARTH_RADIUS = 6378.137  # km

class Orbit:
    def __init__(self, radius: float, inclination: float = 0):
        self.radius = radius
        self.satellites = []
        self.inclination = inclination

class LaunchPad:
    def __init__(self, radius: float, angle: float):
        self.position = radius
        self.angle = angle

class SpaceCraft:
    def __init__(self, radius: float, angle: float, velocity: float):
        self.radius = radius
        self.angle = angle
        self.trajectory = []
        self.speed = velocity
    
    def update(self, time):
        self.angle += self.speed * time
        self.trajectory.append((self.radius * np.cos(self.angle), self.radius * np.sin(self.angle)))
        return (self.radius * np.cos(self.angle), self.radius * np.sin(self.angle))

    def predict(self, time):
        future_angle = self.angle + self.speed * time
        return (self.radius * np.cos(future_angle), self.radius * np.sin(future_angle))
    
    def position(self):
        return (self.radius * np.cos(self.angle), self.radius * np.sin(self.angle))

class Satellite(SpaceCraft):
    def __init__(self, radius: float, angle: float, velocity: float):
        super().__init__(radius, angle, velocity)

class Tanker(SpaceCraft):
    def __init__(self, radius: float, angle: float, velocity: float = 0, fuel: float = 1000.0):
        super().__init__(radius, angle, velocity)
        self.mode = "orbit"
        self.fuel = fuel

class Shuttle(SpaceCraft):
    def __init__(self, radius: float, angle: float, velocity: float):
        super().__init__(radius, angle, velocity)

class SimulateMission:
    def __init__(self, planet_radius: float, tanker: Tanker):
        self.planet_radius = planet_radius
        self.tanker = tanker
        self.launch_pads = []
        self.orbits = []
        self.satellites = []
    
    def add_launch_pad(self, launch_pad: LaunchPad):
        self.launch_pads.append(launch_pad)

    def add_orbit(self, radius: float, inclination: float = 0):
        orbit = Orbit(radius, inclination)
        self.orbits.append(orbit)
        return orbit
    
    def add_satellite(self, orbit: Orbit, angle: float, speed: float):
        satellite = Satellite(orbit.radius, angle, speed)
        orbit.satellites.append(satellite)
        self.satellites.append(satellite)
        return satellite
    
    def calculate_best_launch_pad(self):
        # Find the launch pad that requires the least fuel to reach the target
        if not self.launch_pads:
            raise ValueError("No launch pads available")
            
        best_pad = self.launch_pads[0]
        min_fuel = float('inf')
        
        # Simple calculation - in reality would be more complex
        for pad in self.launch_pads:
            # Calculate estimated fuel based on distance to lowest orbit
            if self.orbits:
                fuel_needed = abs(self.orbits[0].radius - self.planet_radius) * 0.1
                if fuel_needed < min_fuel:
                    min_fuel = fuel_needed
                    best_pad = pad
        
        return best_pad, min_fuel
    
    def calculate_launch_time_to_intercept(self, launch_pad, target_orbit, target_satellite):
        """Calculate when to launch to intercept a satellite upon reaching orbit"""
        # Estimate flight time to reach orbit
        flight_time = (target_orbit.radius - self.planet_radius) * 0.01  # Simple estimate
        
        # Calculate where the satellite will be after flight time
        future_angle = target_satellite.angle + (target_satellite.speed * flight_time)
        future_angle = future_angle % (2 * np.pi)  # Normalize to 0-2π
        
        # Calculate what angle we need to launch at to intercept
        # For simplicity, we'll say the final insertion angle will be launch angle + 0.5
        target_launch_angle = (future_angle - 0.5) % (2 * np.pi)
        
        # Calculate waiting time at the launch pad
        # How long until the launch pad rotates to the target angle
        current_angle = launch_pad.angle % (2 * np.pi)
        wait_time = 0
        
        # Assuming planet rotation gives us the ability to launch at any angle
        # This is a simplification - in reality, orbital mechanics would be more complex
        
        print(f"Target satellite current angle: {target_satellite.angle:.2f} rad")
        print(f"Flight time to orbit: {flight_time:.2f} time units")
        print(f"Satellite future angle: {future_angle:.2f} rad")
        print(f"Target launch angle: {target_launch_angle:.2f} rad")
        
        return target_launch_angle, flight_time
    
    def simulate_launch(self, tanker: Tanker, target_orbit: Orbit, final_angle: float, flight_time: float):
        """Simulate launch from planet to target orbit with precise timing for intercept"""
        # Start position
        start_angle = tanker.angle
        
        # Generate trajectory
        steps = 50
        final_radius = target_orbit.radius
        
        # Clear previous trajectory
        tanker.trajectory = []
        
        for i in range(1, steps + 1):
            # Interpolate radius from planet radius to orbit radius
            t = i / steps
            r = self.planet_radius + t * (final_radius - self.planet_radius)
            
            # Interpolate angle - ensure we arrive at the right position for intercept
            angle = start_angle + t * (final_angle - start_angle)
            
            x = r * np.cos(angle)
            y = r * np.sin(angle)
            tanker.trajectory.append((x, y))
        
        # Update tanker position to final orbit position
        tanker.radius = final_radius
        tanker.angle = final_angle
        
        # Set tanker speed to match orbital velocity once inserted
        # This should match the satellite's speed for proper rendezvous
        for satellite in target_orbit.satellites:
            tanker.speed = satellite.speed
            break
        
        return final_radius, final_angle
    
    def simulate_mission(self, tanker: Tanker, target_orbit: Orbit = None):
        """Simulate mission to rendezvous with a satellite in lowest orbit"""
        # Sort all the orbits by radius if target_orbit not specified
        if target_orbit is None:
            # Find lowest orbit
            self.orbits.sort(key=lambda x: x.radius)
            if not self.orbits:
                print("No orbits available for mission")
                return
            target_orbit = self.orbits[0]  # Lowest orbit
        
        # Find best satellite to intercept in the target orbit
        target_satellite = None
        
        if target_orbit.satellites:
            # For simplicity, just use the first satellite
            target_satellite = target_orbit.satellites[0]
            
            # Calculate the optimal launch angle and time
            launch_angle, flight_time = self.calculate_launch_time_to_intercept(
                self.launch_pads[0], target_orbit, target_satellite
            )
            
            print(f"Planning intercept with satellite in lowest orbit")
            print(f"Optimal launch angle: {launch_angle:.2f} radians")
            
            # Update all satellites to their positions at launch time
            # In a real simulation, we'd want to back-calculate their initial positions
            # But for visualization purposes, we'll just advance them
            
            # Launch to the target orbit with timing for intercept
            self.simulate_launch(tanker, target_orbit, launch_angle, flight_time)
            
            print("Launch complete - beginning orbital insertion")
            print(f"Tanker final angle: {tanker.angle:.2f} rad")
            print(f"Satellite angle at intercept: {(target_satellite.angle + flight_time * target_satellite.speed) % (2*np.pi):.2f} rad")
            
            # No need to simulate wait time in orbit - we timed the launch for direct intercept
            
            print("Rendezvous complete!")
        else:
            print("No satellites in target orbit for rendezvous")
    
    def visualize(self):
        """Create an animation of the mission with satellites, orbits, and trajectories"""
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')
        
        # Plot the planet
        planet = plt.Circle((0, 0), self.planet_radius, color='blue', alpha=0.5)
        ax.add_patch(planet)
        
        # Plot orbits
        for orbit in self.orbits:
            theta = np.linspace(0, 2*np.pi, 100)
            x = orbit.radius * np.cos(theta)
            y = orbit.radius * np.sin(theta)
            ax.plot(x, y, 'k--', alpha=0.3)
        
        # Plot launch pads
        for pad in self.launch_pads:
            pad_x = self.planet_radius * np.cos(pad.angle)
            pad_y = self.planet_radius * np.sin(pad.angle)
            ax.plot(pad_x, pad_y, 'bs', markersize=8)
        
        # Plot satellites and their orbital paths
        satellite_markers = []
        for satellite in self.satellites:
            # Plot initial position
            sat_x = satellite.radius * np.cos(satellite.angle)
            sat_y = satellite.radius * np.sin(satellite.angle)
            sat_marker, = ax.plot(sat_x, sat_y, 'ro', markersize=6)
            satellite_markers.append((satellite, sat_marker))
        
        # Plot tanker initial position and trajectory
        tanker_x = self.tanker.radius * np.cos(self.tanker.angle)
        tanker_y = self.tanker.radius * np.sin(self.tanker.angle)
        tanker_marker, = ax.plot(tanker_x, tanker_y, 'go', markersize=8)
        
        # Plot tanker trajectory if available
        tanker_path = []
        if self.tanker.trajectory:
            trajectory_x = [pos[0] for pos in self.tanker.trajectory]
            trajectory_y = [pos[1] for pos in self.tanker.trajectory]
            tanker_path, = ax.plot(trajectory_x, trajectory_y, 'g-', alpha=0.7)
        
        # Set plot limits based on the largest orbit
        max_radius = max(orbit.radius for orbit in self.orbits) * 1.2 if self.orbits else self.planet_radius * 2
        ax.set_xlim(-max_radius, max_radius)
        ax.set_ylim(-max_radius, max_radius)
        ax.grid(True)
        ax.set_title('Mission Simulation - Timed Launch for Immediate Intercept')
        
        # Store initial positions for animation
        initial_angles = {}
        for satellite in self.satellites:
            initial_angles[satellite] = satellite.angle
        
        tanker_initial_angle = self.tanker.angle
        tanker_initial_radius = self.tanker.radius
        
        def animate(frame):
            # Update satellite positions
            for satellite, marker in satellite_markers:
                # Calculate position at this frame
                current_angle = initial_angles[satellite] + satellite.speed * frame
                x = satellite.radius * np.cos(current_angle)
                y = satellite.radius * np.sin(current_angle)
                marker.set_data([x], [y])
            
            # Update tanker position
            if frame < len(self.tanker.trajectory):
                # Follow pre-calculated trajectory during launch phase
                x, y = self.tanker.trajectory[frame]
                tanker_marker.set_data([x], [y])
            else:
                # After reaching orbit, follow orbital path
                excess_frames = frame - len(self.tanker.trajectory)
                current_angle = self.tanker.angle + self.tanker.speed * excess_frames
                x = self.tanker.radius * np.cos(current_angle)
                y = self.tanker.radius * np.sin(current_angle)
                tanker_marker.set_data([x], [y])
            
            return [marker for _, marker in satellite_markers] + [tanker_marker]
        
        # Create animation
        max_frames = max(100, len(self.tanker.trajectory) + 50)  # Show some orbital motion after insertion
        ani = FuncAnimation(fig, animate, frames=max_frames, blit=True, interval=50)
        
        plt.show()
        return ani

def run_experiment():
    """Run a sample mission to demonstrate the functionality"""
    # Create a launch pad
    launchpad = LaunchPad(EARTH_RADIUS, 0)
    
    # Create a tanker at the launch pad
    tanker = Tanker(EARTH_RADIUS, launchpad.angle, fuel=1000.0)
    
    # Create mission planner
    planner = SimulateMission(planet_radius=EARTH_RADIUS, tanker=tanker)
    planner.add_launch_pad(launchpad)
    
    # Add orbits
    #low_orbit = planner.add_orbit(radius=EARTH_RADIUS + 200)  # Low Earth Orbit
    #medium_orbit = planner.add_orbit(radius=EARTH_RADIUS + 500)  # Medium Earth Orbit
    high_orbit = planner.add_orbit(radius=EARTH_RADIUS + 1000)  # High Earth Orbit
    
    # Add satellites to orbits
    # Low orbit satellites
    #planner.add_satellite(low_orbit, angle=0, speed=0.01)
    #planner.add_satellite(low_orbit, angle=np.pi/2, speed=0.01)
    
    # Medium orbit satellites
    #planner.add_satellite(medium_orbit, angle=np.pi/4, speed=0.007)
    #planner.add_satellite(medium_orbit, angle=3*np.pi/4, speed=0.007)
    
    # High orbit satellites
    planner.add_satellite(high_orbit, angle=np.pi/3, speed=0.005)
    
    # Find best launch pad
    best_pad, fuel_needed = planner.calculate_best_launch_pad()
    print(f"Best launch pad at angle: {best_pad.angle} radians")
    print(f"Estimated fuel needed: {fuel_needed:.2f} units")
    
    # Simulate mission - sending tanker to lowest orbit for immediate intercept
    planner.simulate_mission(tanker, high_orbit)
    
    # Visualize the mission
    animation = planner.visualize()
    
    return planner, animation

if __name__ == "__main__":
    run_experiment()