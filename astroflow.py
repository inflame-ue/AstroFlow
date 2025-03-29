import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle
import math
from typing import List, Tuple, Dict
import time

class Planet:
    def __init__(self, radius: float):
        self.radius = radius
        self.launch_pads = []

    def add_launch_pad(self, angle: float):
        """Add a launch pad at a given angle (radians) on the planet's surface"""
        pad = LaunchPad(self.radius, angle)
        self.launch_pads.append(pad)
        return pad

    def draw(self, ax):
        """Draw the planet on the given matplotlib axis"""
        planet_circle = Circle((0, 0), self.radius, color='blue', alpha=0.7)
        ax.add_patch(planet_circle)
        
        # Draw launch pads
        for pad in self.launch_pads:
            pad.draw(ax)


class LaunchPad:
    def __init__(self, radius: float, angle: float):
        self.radius = radius
        self.angle = angle
        self.x = radius * np.cos(angle)
        self.y = radius * np.sin(angle)
    
    def draw(self, ax):
        """Draw the launch pad on the given matplotlib axis"""
        ax.plot(self.x, self.y, 'ro', markersize=8)  # Red dot for launch pad


class Orbit:
    def __init__(self, radius: float):
        self.radius = radius
        self.satellites = []
    
    def add_satellite(self, angle: float, speed: float):
        """Add a satellite at a given angle with a given orbital speed"""
        satellite = Satellite(self.radius, angle, speed)
        self.satellites.append(satellite)
        return satellite
    
    def draw(self, ax):
        """Draw the orbit and its satellites on the given matplotlib axis"""
        theta = np.linspace(0, 2*np.pi, 100)
        x = self.radius * np.cos(theta)
        y = self.radius * np.sin(theta)
        ax.plot(x, y, 'k--', alpha=0.3)  # Dashed line for orbit
        
        # Draw satellites
        for satellite in self.satellites:
            satellite.draw(ax)


class Satellite:
    def __init__(self, orbit_radius: float, angle: float, speed: float):
        self.orbit_radius = orbit_radius
        self.angle = angle
        self.speed = speed  # radians per time unit
        self.x = self.orbit_radius * np.cos(self.angle)
        self.y = self.orbit_radius * np.sin(self.angle)
    
    def update_position(self, time_elapsed=0):
        """Update the satellite's position based on time elapsed"""
        self.angle = (self.angle + self.speed * time_elapsed) % (2 * np.pi)
        self.x = self.orbit_radius * np.cos(self.angle)
        self.y = self.orbit_radius * np.sin(self.angle)
    
    def draw(self, ax):
        """Draw the satellite on the given matplotlib axis"""
        ax.plot(self.x, self.y, 'go', markersize=6)  # Green dot for satellite


class RefuelingTanker:
    def __init__(self, start_pad: LaunchPad):
        self.x = start_pad.x
        self.y = start_pad.y
        self.trajectory = [(self.x, self.y)]
        self.current_orbit = None
        self.current_angle = start_pad.angle
        self.in_transit = False
        self.transfer_start_time = 0
        self.transfer_duration = 0
        self.start_orbit_radius = 0
        self.target_orbit_radius = 0
        self.waiting = False
        self.waiting_for_satellite = None
        self.waiting_until = 0
        self.fuel_used = 0
        self.wait_fuel_rate = 0.05  # Fuel consumption per time unit while waiting
        
    def launch_to_orbit(self, orbit: Orbit, planet_radius: float, time: float):
        """Launch from pad to initial orbit"""
        self.start_orbit_radius = planet_radius
        self.target_orbit_radius = orbit.radius
        self.current_orbit = orbit
        
        # Calculate fuel needed for the transfer (simplified model)
        delta_v = self.calculate_hohmann_delta_v(planet_radius, orbit.radius)
        self.fuel_used += delta_v
        
        # Set up transfer parameters
        self.in_transit = True
        self.transfer_start_time = time
        # Transfer time is half the period of the transfer orbit
        self.transfer_duration = np.pi * np.sqrt(((planet_radius + orbit.radius)/2)**3 / 398600)
        
        return self.fuel_used
    
    def transfer_to_orbit(self, target_orbit: Orbit, time: float):
        """Transfer from current orbit to target orbit using Hohmann transfer"""
        if self.current_orbit is None:
            return 0
            
        self.start_orbit_radius = self.current_orbit.radius
        self.target_orbit_radius = target_orbit.radius
        
        # Calculate fuel needed for the transfer
        delta_v = self.calculate_hohmann_delta_v(self.current_orbit.radius, target_orbit.radius)
        self.fuel_used += delta_v
        
        # Set up transfer parameters
        self.in_transit = True
        self.transfer_start_time = time
        # Transfer time is half the period of the transfer orbit
        self.transfer_duration = np.pi * np.sqrt(((self.current_orbit.radius + target_orbit.radius)/2)**3 / 398600)
        
        self.current_orbit = target_orbit
        return delta_v
    
    def calculate_hohmann_delta_v(self, r1: float, r2: float) -> float:
        """Calculate the delta-v required for a Hohmann transfer between two circular orbits"""
        # Gravitational parameter (GM) - using Earth's value for example
        mu = 398600  # km^3/s^2
        
        # Initial orbit velocity
        v1 = np.sqrt(mu/r1)
        
        # Transfer orbit velocities
        v_perigee = np.sqrt(mu * (2/r1 - 2/(r1+r2)))
        v_apogee = np.sqrt(mu * (2/r2 - 2/(r1+r2)))
        
        # Final orbit velocity
        v2 = np.sqrt(mu/r2)
        
        # Delta-v calculations
        delta_v1 = abs(v_perigee - v1)
        delta_v2 = abs(v2 - v_apogee)
        
        return delta_v1 + delta_v2
    
    def wait_for_satellite(self, satellite, current_time, orbit_angular_speed):
        """Wait for optimal alignment with a satellite"""
        # Calculate angular distance
        angular_distance = abs(self.current_angle - satellite.angle)
        if angular_distance > np.pi:
            angular_distance = 2 * np.pi - angular_distance
        
        # Calculate wait time
        wait_time = angular_distance / orbit_angular_speed if orbit_angular_speed > 0 else 0
        
        self.waiting = True
        self.waiting_for_satellite = satellite
        self.waiting_until = current_time + wait_time
        
        # Return fuel cost of waiting
        return wait_time * self.wait_fuel_rate
    
    def update_position(self, time: float):
        """Update the tanker's position based on current state and time"""
        if self.in_transit:
            # Check if transfer is complete
            elapsed = time - self.transfer_start_time
            if elapsed >= self.transfer_duration:
                self.in_transit = False
                # Now in the target orbit
                self.x = self.target_orbit_radius * np.cos(self.current_angle)
                self.y = self.target_orbit_radius * np.sin(self.current_angle)
            else:
                # In transfer orbit - simplified interpolation
                progress = elapsed / self.transfer_duration
                r = self.start_orbit_radius + progress * (self.target_orbit_radius - self.start_orbit_radius)
                self.x = r * np.cos(self.current_angle)
                self.y = r * np.sin(self.current_angle)
        elif self.waiting:
            # Check if waiting is complete
            if time >= self.waiting_until:
                self.waiting = False
                self.waiting_for_satellite = None
            # While waiting, maintain position but update angle for visualization
            if self.current_orbit is not None:
                mu = 398600  # GM for Earth
                orbit_speed = np.sqrt(mu / self.current_orbit.radius) / self.current_orbit.radius
                self.current_angle = (self.current_angle + orbit_speed) % (2 * np.pi)
                self.x = self.current_orbit.radius * np.cos(self.current_angle)
                self.y = self.current_orbit.radius * np.sin(self.current_angle)
                
                # Consume fuel while waiting
                self.fuel_used += self.wait_fuel_rate * 0.1  # Scaled for visualization
        elif self.current_orbit is not None:
            # Update position in current orbit
            # Calculate orbital speed (simplified)
            mu = 398600  # GM for Earth
            orbit_speed = np.sqrt(mu / self.current_orbit.radius) / self.current_orbit.radius  # angular velocity
            self.current_angle = (self.current_angle + orbit_speed) % (2 * np.pi)
            self.x = self.current_orbit.radius * np.cos(self.current_angle)
            self.y = self.current_orbit.radius * np.sin(self.current_angle)
        
        self.trajectory.append((self.x, self.y))
    
    def draw(self, ax):
        """Draw the tanker and its trajectory"""
        # Draw current position
        ax.plot(self.x, self.y, 'mo', markersize=8)  # Magenta dot for tanker
        
        # Draw trajectory
        trajectory = np.array(self.trajectory)
        if len(trajectory) > 1:
            ax.plot(trajectory[:,0], trajectory[:,1], 'm-', alpha=0.5)


class Simulation:
    def __init__(self):
        self.planet = Planet(6371)  # Earth radius in km
        self.orbits = []
        self.time = 0
        self.tanker = None
        self.best_pad = None
        self.best_fuel = float('inf')
        self.best_trajectory = []
        
    def add_orbit(self, radius: float):
        """Add an orbit at the given radius"""
        orbit = Orbit(radius)
        self.orbits.append(orbit)
        return orbit
    
    def update(self, dt: float):
        """Update the simulation by dt time"""
        self.time += dt
        
        # Update satellites
        for orbit in self.orbits:
            for satellite in orbit.satellites:
                satellite.update_position(dt)
        
        # Update tanker if it exists
        if self.tanker:
            self.tanker.update_position(self.time)
    
    def find_best_launch_pad(self):
        """Find the best launch pad that minimizes fuel usage for refueling all satellites"""
        for pad in self.planet.launch_pads:
            fuel_used = self.calculate_refueling_mission(pad)
            if fuel_used < self.best_fuel:
                self.best_fuel = fuel_used
                self.best_pad = pad
                
        print(f"Best launch pad: angle={self.best_pad.angle:.2f} rad, fuel={self.best_fuel:.2f}")
        return self.best_pad
    
    def calculate_refueling_mission(self, pad: LaunchPad) -> float:
        """Calculate fuel needed for a refueling mission from the given pad"""
        # Reset simulation
        test_tanker = RefuelingTanker(pad)
        test_time = 0
        total_fuel = 0
        waiting_fuel_rate = 0.05  # Fuel consumption per time unit while waiting
        
        # For simplicity, assume we visit orbits in order of increasing radius
        sorted_orbits = sorted(self.orbits, key=lambda o: o.radius)
        
        # Launch to first orbit
        if sorted_orbits:
            # Calculate launch time based on optimal alignment with satellites
            satellites_in_orbit = sorted_orbits[0].satellites
            if satellites_in_orbit:
                # Find optimal launch time to minimize waiting for closest satellite
                min_wait_time = float('inf')
                for sat in satellites_in_orbit:
                    # Predict satellite position at arrival time
                    arrival_time = np.pi * np.sqrt(((self.planet.radius + sorted_orbits[0].radius)/2)**3 / 398600)
                    sat_future_angle = (sat.angle + sat.speed * arrival_time) % (2 * np.pi)
                    
                    # Calculate angular distance between where tanker will arrive and satellite position
                    tanker_arrival_angle = pad.angle
                    angular_distance = abs(tanker_arrival_angle - sat_future_angle)
                    if angular_distance > np.pi:
                        angular_distance = 2 * np.pi - angular_distance
                    
                    # Calculate wait time based on angular distance and orbit speed
                    mu = 398600  # GM for Earth
                    orbit_angular_speed = np.sqrt(mu / sorted_orbits[0].radius) / sorted_orbits[0].radius
                    wait_time = angular_distance / orbit_angular_speed if orbit_angular_speed > 0 else float('inf')
                    
                    min_wait_time = min(min_wait_time, wait_time)
                
                # Add waiting fuel cost
                waiting_fuel = min_wait_time * waiting_fuel_rate
                total_fuel += waiting_fuel
            
            # Add transfer fuel
            total_fuel += test_tanker.launch_to_orbit(sorted_orbits[0], self.planet.radius, test_time)
            test_time += test_tanker.transfer_duration
            
            # Transfer between orbits
            for i in range(1, len(sorted_orbits)):
                current_orbit = sorted_orbits[i-1]
                target_orbit = sorted_orbits[i]
                
                # Calculate optimal transfer time based on satellite positions
                min_wait_time = float('inf')
                if target_orbit.satellites:
                    for sat in target_orbit.satellites:
                        # Calculate transfer duration
                        transfer_duration = np.pi * np.sqrt(((current_orbit.radius + target_orbit.radius)/2)**3 / 398600)
                        
                        # Predict satellite position at arrival time
                        sat_future_angle = (sat.angle + sat.speed * transfer_duration) % (2 * np.pi)
                        
                        # Calculate angular difference between arrival and satellite position
                        arrival_angle = test_tanker.current_angle
                        angular_distance = abs(arrival_angle - sat_future_angle)
                        if angular_distance > np.pi:
                            angular_distance = 2 * np.pi - angular_distance
                        
                        # Calculate wait time
                        mu = 398600  # GM for Earth
                        orbit_angular_speed = np.sqrt(mu / target_orbit.radius) / target_orbit.radius
                        wait_time = angular_distance / orbit_angular_speed if orbit_angular_speed > 0 else float('inf')
                        
                        min_wait_time = min(min_wait_time, wait_time)
                    
                    # Add waiting fuel cost
                    waiting_fuel = min_wait_time * waiting_fuel_rate
                    total_fuel += waiting_fuel
                
                # Add transfer fuel
                total_fuel += test_tanker.transfer_to_orbit(target_orbit, test_time)
                test_time += test_tanker.transfer_duration
            
            # Return to surface (simplified)
            total_fuel += test_tanker.calculate_hohmann_delta_v(sorted_orbits[-1].radius, self.planet.radius)
        
        return total_fuel
    
    def run_best_mission(self):
        """Run and animate the best refueling mission"""
        if self.best_pad is None:
            self.find_best_launch_pad()
            
        self.tanker = RefuelingTanker(self.best_pad)
        sorted_orbits = sorted(self.orbits, key=lambda o: o.radius)
        
        # Launch to first orbit
        if sorted_orbits:
            self.tanker.launch_to_orbit(sorted_orbits[0], self.planet.radius, self.time)
            
            # Set up mission plan
            self.mission_plan = []
            
            # For each orbit, determine if we need to wait for satellite alignment
            for i in range(1, len(sorted_orbits)):
                current_orbit = sorted_orbits[i-1]
                target_orbit = sorted_orbits[i]
                
                # If there are satellites in the target orbit, plan to wait
                if target_orbit.satellites:
                    # Add wait action before transfer
                    self.mission_plan.append(('wait', target_orbit.satellites[0], 0.0))
                
                # Add transfer to next orbit
                self.mission_plan.append(('transfer', target_orbit, 0.5))
            
            # Add return to surface
            self.mission_plan.append(('return', None, 1.0))
    
    def visualize(self, max_time=200, dt=0.5):
        """Visualize the simulation with an animation"""
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Set the axes limits based on the furthest orbit
        max_radius = max([orbit.radius for orbit in self.orbits], default=self.planet.radius * 2)
        ax.set_xlim(-max_radius*1.1, max_radius*1.1)
        ax.set_ylim(-max_radius*1.1, max_radius*1.1)
        ax.set_aspect('equal')
        ax.grid(True)
        ax.set_title('Orbital Refueling Mission Simulation')
        
        # Run the best mission if not already done
        if self.tanker is None:
            self.run_best_mission()
        
        # Initialize plot elements
        self.planet.draw(ax)
        for orbit in self.orbits:
            orbit.draw(ax)
        
        # Create a scatter plot for satellites and tanker that will be updated in animation
        sat_scatter = ax.scatter([], [], color='green', s=30)
        tanker_scatter = ax.scatter([], [], color='magenta', s=60)
        trajectory_line, = ax.plot([], [], 'm-', alpha=0.5)
        alignment_line, = ax.plot([], [], 'r-', alpha=0.7)  # Line to show target satellite
        
        # Text for displaying simulation info
        time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
        fuel_text = ax.text(0.02, 0.90, '', transform=ax.transAxes)
        status_text = ax.text(0.02, 0.85, '', transform=ax.transAxes)
        
        def init():
            sat_scatter.set_offsets(np.empty((0, 2)))
            tanker_scatter.set_offsets(np.empty((0, 2)))
            trajectory_line.set_data([], [])
            alignment_line.set_data([], [])
            time_text.set_text('')
            fuel_text.set_text('')
            status_text.set_text('')
            return sat_scatter, tanker_scatter, trajectory_line, alignment_line, time_text, fuel_text, status_text
        
        def animate(i):
            current_time = i * dt
            
            # Update mission status
            if self.tanker and hasattr(self, 'mission_plan') and self.mission_plan:
                action, target, delay = self.mission_plan[0]
                
                if not self.tanker.in_transit and not self.tanker.waiting and current_time > self.tanker.transfer_start_time + self.tanker.transfer_duration + delay:
                    if action == 'wait':
                        # Calculate orbital speed for waiting
                        mu = 398600  # GM for Earth
                        current_orbit = self.tanker.current_orbit
                        orbit_angular_speed = np.sqrt(mu / current_orbit.radius) / current_orbit.radius
                        
                        # Start waiting for satellite alignment
                        self.tanker.wait_for_satellite(target, current_time, orbit_angular_speed)
                        
                        # Remove this action
                        self.mission_plan.pop(0)
                    elif action == 'transfer':
                        self.tanker.transfer_to_orbit(target, current_time)
                        
                        # Remove this action
                        self.mission_plan.pop(0)
                    elif action == 'return':
                        # Simplified return - just show the trajectory
                        self.tanker.transfer_to_orbit(Orbit(self.planet.radius), current_time)
                        
                        # Remove the completed action
                        self.mission_plan.pop(0)
            
            # Update satellite positions
            for orbit in self.orbits:
                for satellite in orbit.satellites:
                    satellite.update_position(dt)
            
            # Collect satellite positions
            sat_positions = []
            for orbit in self.orbits:
                for satellite in orbit.satellites:
                    sat_positions.append([satellite.x, satellite.y])
            
            # Update satellite scatter plot
            if sat_positions:
                sat_scatter.set_offsets(np.array(sat_positions))
            
            # Update tanker if it exists
            if self.tanker:
                self.tanker.update_position(current_time)
                tanker_scatter.set_offsets(np.array([[self.tanker.x, self.tanker.y]]))
                
                # Update trajectory
                traj = np.array(self.tanker.trajectory)
                if len(traj) > 1:
                    trajectory_line.set_data(traj[:,0], traj[:,1])
            
            # Update alignment line if waiting
            if self.tanker.waiting and self.tanker.waiting_for_satellite:
                target_sat = self.tanker.waiting_for_satellite
                alignment_line.set_data([self.tanker.x, target_sat.x], [self.tanker.y, target_sat.y])
            else:
                alignment_line.set_data([], [])
            
            # Update text information
            time_text.set_text(f'Time: {current_time:.1f} s')
            if self.tanker:
                fuel_text.set_text(f'Fuel used: {self.tanker.fuel_used:.1f}')
                
                # Update status
                if self.tanker.in_transit:
                    status_text.set_text(f'Status: In transit to orbit (r={self.tanker.target_orbit_radius:.0f} km)')
                elif self.tanker.waiting:
                    remaining = self.tanker.waiting_until - current_time
                    status_text.set_text(f'Status: Waiting for satellite alignment ({remaining:.1f}s)')
                else:
                    status_text.set_text(f'Status: In orbit (r={self.tanker.current_orbit.radius if self.tanker.current_orbit else 0:.0f} km)')
            
            return sat_scatter, tanker_scatter, trajectory_line, alignment_line, time_text, fuel_text, status_text
        
        frames = int(max_time / dt)
        anim = FuncAnimation(fig, animate, frames=frames, init_func=init, blit=True, interval=100)
        
        plt.tight_layout()
        plt.show()
        
        return anim


def test_algorithm():
    """Test the algorithm with various configurations"""
    sim = Simulation()
    
    # Add launch pads at different angles
    for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
        sim.planet.add_launch_pad(angle)
    
    # Add orbits
    low_orbit = sim.add_orbit(12000)  # Low Earth Orbit
    medium_orbit = sim.add_orbit(20000)  # Medium Earth Orbit
    high_orbit = sim.add_orbit(36000)  # Geostationary Orbit
    
    # Add satellites to orbits
    for i in range(3):
        angle = np.random.uniform(0, 2*np.pi)
        speed = np.random.uniform(0.001, 0.005)
        low_orbit.add_satellite(angle, speed)
    
    for i in range(2):
        angle = np.random.uniform(0, 2*np.pi)
        speed = np.random.uniform(0.0005, 0.002)
        medium_orbit.add_satellite(angle, speed)
    
    high_orbit.add_satellite(np.pi/4, 0.0003)
    
    # Find best launch pad
    best_pad = sim.find_best_launch_pad()
    print(f"Best launch pad position: ({best_pad.x:.2f}, {best_pad.y:.2f})")
    
    # Visualize the simulation
    sim.visualize(max_time=300)


if __name__ == "__main__":
    test_algorithm() 