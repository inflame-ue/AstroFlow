import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import List, Tuple, Dict
import math

class Planet:
    def __init__(self, radius: float, GM: float):
        self.radius = radius  # Planet radius
        self.GM = GM  # Gravitational parameter
        
class LaunchPad:
    def __init__(self, angle: float, planet: Planet):
        self.angle = angle  # Angle in radians
        self.planet = planet
        self.position = (planet.radius * np.cos(angle), planet.radius * np.sin(angle))
        
class Orbit:
    def __init__(self, radius: float, planet: Planet):
        self.radius = radius
        self.planet = planet
        self.angular_velocity = np.sqrt(planet.GM / (radius**3))  # ω = sqrt(GM/r³)
        
class Satellite:
    def __init__(self, orbit: Orbit, initial_angle: float):
        self.orbit = orbit
        self.initial_angle = initial_angle  # Initial position angle in radians
        self.angle = initial_angle
        
    def position_at_time(self, time: float) -> Tuple[float, float]:
        """Calculate satellite position at given time"""
        angle = self.initial_angle + self.orbit.angular_velocity * time
        x = self.orbit.radius * np.cos(angle)
        y = self.orbit.radius * np.sin(angle)
        return (x, y)
    
    def update_position(self, time: float):
        """Update satellite position to time t"""
        self.angle = self.initial_angle + self.orbit.angular_velocity * time
        
class TransferOrbit:
    def __init__(self, r1: float, r2: float, planet: Planet):
        """Hohmann transfer orbit from radius r1 to r2"""
        self.r1 = r1
        self.r2 = r2
        self.planet = planet
        self.semi_major_axis = (r1 + r2) / 2
        
        # Calculate delta-v for the transfer
        v1_circular = np.sqrt(planet.GM / r1)
        v2_circular = np.sqrt(planet.GM / r2)
        
        v1_transfer = np.sqrt(planet.GM * (2/r1 - 1/self.semi_major_axis))
        v2_transfer = np.sqrt(planet.GM * (2/r2 - 1/self.semi_major_axis))
        
        self.delta_v1 = abs(v1_transfer - v1_circular)
        self.delta_v2 = abs(v2_circular - v2_transfer)
        self.total_delta_v = self.delta_v1 + self.delta_v2
        
        # Calculate transfer time (half an elliptical orbit)
        self.transfer_time = np.pi * np.sqrt(self.semi_major_axis**3 / planet.GM)

class Mission:
    def __init__(self, planet: Planet, pads: List[LaunchPad], 
                 satellites: List[Satellite], transfer_orbit_radius: float):
        self.planet = planet
        self.pads = pads
        self.satellites = satellites
        self.transfer_orbit_radius = transfer_orbit_radius
        self.transfer_orbit = Orbit(transfer_orbit_radius, planet)
        
    def calculate_optimal_launch_time(self, pad: LaunchPad) -> Dict:
        """
        Calculate the optimal launch time for a given pad that minimizes mission time
        Returns a dictionary with mission details
        """
        # Launch from surface to transfer orbit
        surface_to_orbit = TransferOrbit(self.planet.radius, self.transfer_orbit_radius, self.planet)
        
        # Initial position of tanker on transfer orbit after launch (aligned with pad angle)
        initial_tanker_angle = pad.angle
        
        # Time to reach transfer orbit
        launch_time = surface_to_orbit.transfer_time
        
        # Track mission events and timeline
        events = []
        
        # Initial position of tanker on transfer orbit
        tanker_angle = initial_tanker_angle + np.pi  # Arriving on opposite side after half-orbit transfer
        
        # For each satellite, calculate optimal departure time for shuttle
        shuttle_missions = []
        for sat_idx, satellite in enumerate(self.satellites):
            # Simulate to find optimal departure time
            best_departure_time = None
            best_roundtrip_time = float('inf')
            
            # Check different departure times by sweeping through waiting periods
            for wait_time in np.linspace(0, 2*np.pi/self.transfer_orbit.angular_velocity, 50):
                departure_time = launch_time + wait_time
                
                # Tanker position at departure
                tanker_angle_at_departure = initial_tanker_angle + np.pi + self.transfer_orbit.angular_velocity * wait_time
                
                # Satellite position at departure
                sat_angle_at_departure = satellite.initial_angle + satellite.orbit.angular_velocity * departure_time
                
                # Hohmann transfer from tanker orbit to satellite orbit
                to_sat_transfer = TransferOrbit(self.transfer_orbit_radius, satellite.orbit.radius, self.planet)
                
                # Time to reach satellite orbit
                transfer_to_sat_time = to_sat_transfer.transfer_time
                
                # Angle traveled by tanker during transfer
                tanker_angle_change = self.transfer_orbit.angular_velocity * transfer_to_sat_time
                
                # Angle traveled by satellite during transfer
                sat_angle_change = satellite.orbit.angular_velocity * transfer_to_sat_time
                
                # Angle difference between tanker and satellite at rendezvous
                angle_diff = (sat_angle_at_departure + sat_angle_change) - (tanker_angle_at_departure + tanker_angle_change)
                angle_diff = (angle_diff + np.pi) % (2*np.pi) - np.pi  # Normalize to [-π, π]
                
                # Additional waiting for optimal rendezvous
                if abs(angle_diff) > 0.01:  # If not close enough for rendezvous
                    # Calculate wait time needed for satellite to reach rendezvous point
                    if satellite.orbit.angular_velocity > 0:
                        extra_wait = (2*np.pi - angle_diff) / satellite.orbit.angular_velocity
                        if extra_wait < 0:
                            extra_wait += 2*np.pi / satellite.orbit.angular_velocity
                    else:
                        extra_wait = angle_diff / abs(satellite.orbit.angular_velocity)
                    departure_time += extra_wait
                    tanker_angle_at_departure += self.transfer_orbit.angular_velocity * extra_wait
                    sat_angle_at_departure += satellite.orbit.angular_velocity * extra_wait
                
                # Refueling operation time (simplified as a constant)
                refuel_time = 0.5  # Time units
                
                # Return transfer
                from_sat_transfer = TransferOrbit(satellite.orbit.radius, self.transfer_orbit_radius, self.planet)
                transfer_from_sat_time = from_sat_transfer.transfer_time
                
                # Total roundtrip time for this shuttle
                roundtrip_time = transfer_to_sat_time + refuel_time + transfer_from_sat_time
                
                if roundtrip_time < best_roundtrip_time:
                    best_roundtrip_time = roundtrip_time
                    best_departure_time = departure_time
            
            # Record the mission details for this shuttle
            return_time = best_departure_time + best_roundtrip_time
            shuttle_missions.append({
                'satellite_idx': sat_idx,
                'departure_time': best_departure_time,
                'return_time': return_time,
                'roundtrip_time': best_roundtrip_time
            })
            
            events.append(('Shuttle departure to satellite', sat_idx, best_departure_time))
            events.append(('Shuttle return from satellite', sat_idx, return_time))
        
        # Sort mission events chronologically
        events.sort(key=lambda x: x[2])
        
        # Determine when all shuttles have returned
        mission_end_time = max(mission['return_time'] for mission in shuttle_missions)
        
        # Add deorbit time
        deorbit_transfer = TransferOrbit(self.transfer_orbit_radius, self.planet.radius, self.planet)
        mission_end_time += deorbit_transfer.transfer_time
        
        events.append(('Tanker deorbit start', None, mission_end_time - deorbit_transfer.transfer_time))
        events.append(('Mission complete', None, mission_end_time))
        
        # Calculate total fuel cost (delta-v)
        total_delta_v = (
            surface_to_orbit.total_delta_v +  # Launch
            sum(TransferOrbit(self.transfer_orbit_radius, sat.orbit.radius, self.planet).total_delta_v * 2 
                for sat in self.satellites) +  # All shuttle round trips
            deorbit_transfer.total_delta_v  # Return to surface
        )
        
        return {
            'pad': pad,
            'launch_time': 0,  # We'll consider this t=0 for each pad scenario
            'mission_end_time': mission_end_time,
            'total_mission_time': mission_end_time,
            'total_delta_v': total_delta_v,
            'shuttle_missions': shuttle_missions,
            'events': events
        }
    
    def find_optimal_pad(self) -> Dict:
        """Find the launch pad that minimizes mission time"""
        best_mission = None
        best_time = float('inf')
        
        for pad in self.pads:
            mission_result = self.calculate_optimal_launch_time(pad)
            if mission_result['total_mission_time'] < best_time:
                best_time = mission_result['total_mission_time']
                best_mission = mission_result
                
        return best_mission
    
    def visualize_mission(self, mission_result: Dict, save_animation: bool = False):
        """Visualize the mission with animation"""
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.set_aspect('equal')
        
        pad = mission_result['pad']
        max_radius = max(self.transfer_orbit_radius, max(sat.orbit.radius for sat in self.satellites))
        
        # Set plot limits with some margin
        margin = max_radius * 0.2
        ax.set_xlim(-max_radius-margin, max_radius+margin)
        ax.set_ylim(-max_radius-margin, max_radius+margin)
        
        # Draw planet
        planet_circle = plt.Circle((0, 0), self.planet.radius, color='blue', alpha=0.7)
        ax.add_patch(planet_circle)
        
        # Mark chosen launch pad
        ax.plot(pad.position[0], pad.position[1], 'ro', markersize=10)
        
        # Draw orbits
        for satellite in self.satellites:
            orbit_circle = plt.Circle((0, 0), satellite.orbit.radius, fill=False, color='gray', linestyle='-')
            ax.add_patch(orbit_circle)
        
        # Draw transfer orbit
        transfer_orbit_circle = plt.Circle((0, 0), self.transfer_orbit_radius, fill=False, color='gray', linestyle='--')
        ax.add_patch(transfer_orbit_circle)
        
        # Initialize objects that will be animated
        tanker_point, = ax.plot([], [], 'ro', markersize=8, label='Tanker')
        satellite_points = [ax.plot([], [], 'wo', markersize=6)[0] for _ in self.satellites]
        shuttle_points = [ax.plot([], [], 'go', markersize=5)[0] for _ in self.satellites]
        
        # Extract mission timeline
        shuttle_missions = mission_result['shuttle_missions']
        events = mission_result['events']
        total_mission_time = mission_result['total_mission_time']
        
        # Display time and events text
        time_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, verticalalignment='top')
        event_text = ax.text(0.02, 0.94, '', transform=ax.transAxes, verticalalignment='top')
        
        # Create mission timeline for animation
        surface_to_orbit = TransferOrbit(self.planet.radius, self.transfer_orbit_radius, self.planet)
        deorbit_transfer = TransferOrbit(self.transfer_orbit_radius, self.planet.radius, self.planet)
        
        def init():
            tanker_point.set_data([], [])
            for sat_point in satellite_points:
                sat_point.set_data([], [])
            for shuttle_point in shuttle_points:
                shuttle_point.set_data([], [])
            time_text.set_text('')
            event_text.set_text('')
            return [tanker_point, *satellite_points, *shuttle_points, time_text, event_text]
        
        def animate(frame):
            current_time = frame * total_mission_time / 200  # 200 frames total
            
            # Update satellites
            for i, satellite in enumerate(self.satellites):
                angle = satellite.initial_angle + satellite.orbit.angular_velocity * current_time
                x = satellite.orbit.radius * np.cos(angle)
                y = satellite.orbit.radius * np.sin(angle)
                satellite_points[i].set_data([x], [y])  # Wrap in list to make it a sequence
                
            # Update tanker position
            if current_time < surface_to_orbit.transfer_time:
                # During launch
                progress = current_time / surface_to_orbit.transfer_time
                start_angle = pad.angle
                end_angle = start_angle + np.pi  # Arriving on opposite side
                current_angle = start_angle + progress * np.pi
                
                # Interpolate radius from surface to transfer orbit
                r_current = self.planet.radius + progress * (self.transfer_orbit_radius - self.planet.radius)
                x = r_current * np.cos(current_angle)
                y = r_current * np.sin(current_angle)
                
            elif current_time < total_mission_time - deorbit_transfer.transfer_time:
                # On transfer orbit
                orbit_time = current_time - surface_to_orbit.transfer_time
                tanker_angle = pad.angle + np.pi + self.transfer_orbit.angular_velocity * orbit_time
                x = self.transfer_orbit_radius * np.cos(tanker_angle)
                y = self.transfer_orbit_radius * np.sin(tanker_angle)
                
            else:
                # During deorbit
                deorbit_time = current_time - (total_mission_time - deorbit_transfer.transfer_time)
                progress = deorbit_time / deorbit_transfer.transfer_time
                
                # Tanker position at start of deorbit
                deorbit_start_time = total_mission_time - deorbit_transfer.transfer_time
                orbit_time = deorbit_start_time - surface_to_orbit.transfer_time
                start_angle = pad.angle + np.pi + self.transfer_orbit.angular_velocity * orbit_time
                
                # Find end angle (aimed at original pad)
                end_angle = pad.angle
                
                # Interpolate
                current_angle = start_angle + progress * (end_angle - start_angle)
                r_current = self.transfer_orbit_radius - progress * (self.transfer_orbit_radius - self.planet.radius)
                x = r_current * np.cos(current_angle)
                y = r_current * np.sin(current_angle)
                
            tanker_point.set_data([x], [y])  # Wrap in list to make it a sequence
            
            # Update shuttles
            for i, mission in enumerate(shuttle_missions):
                departure_time = mission['departure_time']
                return_time = mission['return_time']
                
                if current_time < departure_time or current_time > return_time:
                    # Shuttle not active or docked with tanker
                    shuttle_points[i].set_data([], [])
                    
                elif current_time < departure_time + surface_to_orbit.transfer_time:
                    # Shuttle heading to satellite
                    progress = (current_time - departure_time) / surface_to_orbit.transfer_time
                    
                    # Starting position (tanker on transfer orbit)
                    orbit_time = departure_time - surface_to_orbit.transfer_time
                    start_angle = pad.angle + np.pi + self.transfer_orbit.angular_velocity * orbit_time
                    start_x = self.transfer_orbit_radius * np.cos(start_angle)
                    start_y = self.transfer_orbit_radius * np.sin(start_angle)
                    
                    # Target satellite position at arrival
                    sat_idx = mission['satellite_idx']
                    target_angle = self.satellites[sat_idx].initial_angle + self.satellites[sat_idx].orbit.angular_velocity * (departure_time + surface_to_orbit.transfer_time)
                    target_x = self.satellites[sat_idx].orbit.radius * np.cos(target_angle)
                    target_y = self.satellites[sat_idx].orbit.radius * np.sin(target_angle)
                    
                    # Interpolate (simplified - should follow Hohmann arc)
                    x = start_x + progress * (target_x - start_x)
                    y = start_y + progress * (target_y - start_y)
                    shuttle_points[i].set_data([x], [y])  # Wrap in list
                    
                elif current_time < return_time - surface_to_orbit.transfer_time:
                    # Shuttle with satellite (during refueling)
                    sat_idx = mission['satellite_idx']
                    angle = self.satellites[sat_idx].initial_angle + self.satellites[sat_idx].orbit.angular_velocity * current_time
                    x = self.satellites[sat_idx].orbit.radius * np.cos(angle)
                    y = self.satellites[sat_idx].orbit.radius * np.sin(angle)
                    shuttle_points[i].set_data([x], [y])  # Wrap in list
                    
                else:
                    # Shuttle returning to tanker
                    sat_idx = mission['satellite_idx']
                    return_start_time = return_time - surface_to_orbit.transfer_time
                    progress = (current_time - return_start_time) / surface_to_orbit.transfer_time
                    
                    # Starting position (satellite orbit)
                    start_angle = self.satellites[sat_idx].initial_angle + self.satellites[sat_idx].orbit.angular_velocity * return_start_time
                    start_x = self.satellites[sat_idx].orbit.radius * np.cos(start_angle)
                    start_y = self.satellites[sat_idx].orbit.radius * np.sin(start_angle)
                    
                    # Target tanker position at shuttle return
                    orbit_time = return_time - surface_to_orbit.transfer_time
                    target_angle = pad.angle + np.pi + self.transfer_orbit.angular_velocity * orbit_time
                    target_x = self.transfer_orbit_radius * np.cos(target_angle)
                    target_y = self.transfer_orbit_radius * np.sin(target_angle)
                    
                    # Interpolate (simplified)
                    x = start_x + progress * (target_x - start_x)
                    y = start_y + progress * (target_y - start_y)
                    shuttle_points[i].set_data([x], [y])  # Wrap in list
            
            # Update time display
            time_text.set_text(f'Mission Time: {current_time:.2f}')
            
            # Update event display
            current_events = [e for e in events if abs(e[2] - current_time) < total_mission_time/200]
            if current_events:
                event_text.set_text('\n'.join([f"{e[0]} {e[1] if e[1] is not None else ''}" for e in current_events]))
            else:
                event_text.set_text('')
            
            return [tanker_point, *satellite_points, *shuttle_points, time_text, event_text]
        
        ani = FuncAnimation(fig, animate, frames=200, init_func=init, blit=True, interval=50)
        
        # Add title with mission information
        plt.title(f"Optimal Launch Pad: {np.degrees(pad.angle):.1f}°, Mission Time: {total_mission_time:.2f}")
        
        if save_animation:
            ani.save('mission_animation.mp4', writer='ffmpeg', fps=30)
            plt.close()
        else:
            plt.tight_layout()
            plt.show()
            
        return ani

def test_algorithm(save_animation=False):
    # Create a test scenario
    GM = 100000  # Gravitational parameter (arbitrary units)
    planet_radius = 100  # Planet radius
    planet = Planet(planet_radius, GM)
    
    # Create several launch pads around the planet
    pad_angles = np.linspace(0, 2*np.pi, 12, endpoint=False)  # 12 pads evenly spaced
    pads = [LaunchPad(angle, planet) for angle in pad_angles]
    
    # Create several orbits
    orbit_radii = [200, 300, 400]
    orbits = [Orbit(radius, planet) for radius in orbit_radii]
    
    # Create satellites on different orbits
    satellites = [
        Satellite(orbits[0], 0.5),  # First orbit, angle 0.5 rad
        Satellite(orbits[1], 2.0),  # Second orbit, angle 2.0 rad
        Satellite(orbits[2], 4.0),  # Third orbit, angle 4.0 rad
    ]
    
    # Choose a transfer orbit (somewhat arbitrary for this example)
    transfer_orbit_radius = np.mean(orbit_radii)
    
    # Create mission
    mission = Mission(planet, pads, satellites, transfer_orbit_radius)
    
    # Find optimal pad
    print("Finding optimal launch pad...")
    optimal_mission = mission.find_optimal_pad()
    
    # Print results
    optimal_pad = optimal_mission['pad']
    print(f"Optimal launch pad angle: {np.degrees(optimal_pad.angle):.2f} degrees")
    print(f"Total mission time: {optimal_mission['total_mission_time']:.2f} time units")
    print(f"Total delta-v: {optimal_mission['total_delta_v']:.2f} velocity units")
    
    # Visualize mission
    print("Visualizing mission...")
    mission.visualize_mission(optimal_mission, save_animation=save_animation)
    
    return mission, optimal_mission

if __name__ == "__main__":
    import sys
    save_animation = "--save" in sys.argv
    mission, optimal_mission = test_algorithm(save_animation)
