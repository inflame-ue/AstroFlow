import numpy as np
import matplotlib.pyplot as plt
from testing import MissionPlanner, EARTH_RADIUS, G, EARTH_MASS, RefuelTanker, HohmannTransfer

def test_simple_system():
    """Simple Earth-like system with a few orbits"""
    print("Running Simple System Test...")
    
    planner = MissionPlanner(planet_radius=EARTH_RADIUS)
    
    # Add three orbits
    low_orbit = planner.add_orbit(EARTH_RADIUS + 1000)
    medium_orbit = planner.add_orbit(EARTH_RADIUS + 5000)
    high_orbit = planner.add_orbit(EARTH_RADIUS + 15000)
    
    # Add satellites with different speeds
    for i in range(6):
        angle = i * 2 * np.pi / 6
        planner.add_satellite(low_orbit, angle, 0.0015)  # Fast rotation
    
    for i in range(4):
        angle = i * 2 * np.pi / 4
        planner.add_satellite(medium_orbit, angle, 0.0008)
        
    for i in range(2):
        angle = i * np.pi
        planner.add_satellite(high_orbit, angle, 0.0003)
    
    # Add launch pads
    for i in range(4):
        angle = i * np.pi/2
        planner.add_launch_pad(angle)
    
    # Calculate best pad and simulate mission
    best_pad, fuel = planner.calculate_best_launch_pad()
    print(f"Best launch pad angle: {best_pad.angle * 180 / np.pi:.1f}° with fuel: {fuel:.1f}")
    
    planner.simulate_mission(best_pad)
    planner.visualize(animation=True)

def test_densely_packed_orbits():
    """Test with many closely packed orbits"""
    print("Running Densely Packed Orbits Test...")
    
    planner = MissionPlanner(planet_radius=EARTH_RADIUS)
    
    # Add multiple close orbits
    orbits = []
    for altitude in range(1000, 10001, 1000):
        orbit = planner.add_orbit(EARTH_RADIUS + altitude)
        orbits.append(orbit)
    
    # Add satellites to each orbit
    for i, orbit in enumerate(orbits):
        num_satellites = 2 + i % 3  # 2-4 satellites per orbit
        speed = 0.002 / (1 + i/5)  # Gradually decreasing speed
        
        for j in range(num_satellites):
            angle = j * 2 * np.pi / num_satellites
            planner.add_satellite(orbit, angle, speed)
    
    # Add launch pads
    for i in range(8):
        angle = i * 2 * np.pi / 8
        planner.add_launch_pad(angle)
    
    # Calculate best pad and simulate mission
    best_pad, fuel = planner.calculate_best_launch_pad()
    print(f"Best launch pad angle: {best_pad.angle * 180 / np.pi:.1f}° with fuel: {fuel:.1f}")
    
    planner.simulate_mission(best_pad)
    planner.visualize(animation=True)

def test_distant_orbits():
    """Test with widely spaced orbits"""
    print("Running Distant Orbits Test...")
    
    planner = MissionPlanner(planet_radius=EARTH_RADIUS)
    
    # Add widely spaced orbits
    orbits = []
    altitudes = [1000, 5000, 15000, 30000, 60000]
    for altitude in altitudes:
        orbit = planner.add_orbit(EARTH_RADIUS + altitude)
        orbits.append(orbit)
    
    # Add satellites to each orbit
    for i, orbit in enumerate(orbits):
        num_satellites = 6 - i  # More satellites in lower orbits
        speed = 0.0015 / (1 + i)  # Speed decreases with altitude
        
        for j in range(num_satellites):
            angle = j * 2 * np.pi / num_satellites
            planner.add_satellite(orbit, angle, speed)
    
    # Add launch pads
    for i in range(6):
        angle = i * 2 * np.pi / 6
        planner.add_launch_pad(angle)
    
    # Calculate best pad and simulate mission
    best_pad, fuel = planner.calculate_best_launch_pad()
    print(f"Best launch pad angle: {best_pad.angle * 180 / np.pi:.1f}° with fuel: {fuel:.1f}")
    
    planner.simulate_mission(best_pad)
    planner.visualize(animation=True)

def test_different_sized_planet():
    """Test with a smaller planet (like Mars)"""
    print("Running Different Sized Planet Test (Mars-like)...")
    
    # Mars parameters (roughly)
    MARS_RADIUS = 3389.5  # km
    MARS_MASS = 6.4171e23  # kg
    
    planner = MissionPlanner(planet_radius=MARS_RADIUS, planet_mass=MARS_MASS)
    
    # Add orbits suitable for Mars
    low_orbit = planner.add_orbit(MARS_RADIUS + 400)
    medium_orbit = planner.add_orbit(MARS_RADIUS + 1500)
    high_orbit = planner.add_orbit(MARS_RADIUS + 5000)
    
    # Add satellites with adjusted speeds for Mars gravity
    for i in range(4):
        angle = i * 2 * np.pi / 4
        planner.add_satellite(low_orbit, angle, 0.0020)
    
    for i in range(3):
        angle = i * 2 * np.pi / 3
        planner.add_satellite(medium_orbit, angle, 0.0010)
        
    for i in range(2):
        angle = i * np.pi
        planner.add_satellite(high_orbit, angle, 0.0005)
    
    # Add launch pads
    for i in range(4):
        angle = i * np.pi/2
        planner.add_launch_pad(angle)
    
    # Calculate best pad and simulate mission
    best_pad, fuel = planner.calculate_best_launch_pad()
    print(f"Best launch pad angle: {best_pad.angle * 180 / np.pi:.1f}° with fuel: {fuel:.1f}")
    
    planner.simulate_mission(best_pad)
    planner.visualize(animation=True)

def test_multiple_mission_tankers():
    """Test with multiple mission tankers"""
    print("Running Multiple Mission Tankers Test...")
    
    planner = MissionPlanner(planet_radius=EARTH_RADIUS)
    
    # Add a few orbits
    low_orbit = planner.add_orbit(EARTH_RADIUS + 2000)
    high_orbit = planner.add_orbit(EARTH_RADIUS + 10000)
    
    # Add satellites
    for i in range(4):
        angle = i * 2 * np.pi / 4
        planner.add_satellite(low_orbit, angle, 0.0012)
    
    for i in range(2):
        angle = i * np.pi
        planner.add_satellite(high_orbit, angle, 0.0004)
    
    # Add launch pads
    for i in range(4):
        angle = i * np.pi/2
        planner.add_launch_pad(angle)
    
    # Calculate best pad
    best_pad, fuel = planner.calculate_best_launch_pad()
    print(f"Best launch pad angle: {best_pad.angle * 180 / np.pi:.1f}° with fuel: {fuel:.1f}")
    
    # Simulate first mission from best pad
    planner.simulate_mission(best_pad)
    
    # Add a second mission from a different pad
    second_pad = planner.launch_pads[1]
    planner.simulate_mission(second_pad)
    
    # Visualize results with both tankers
    planner.visualize(animation=True)

def test_various_satellite_speeds():
    """Test with satellites at different speeds in the same orbit"""
    print("Running Various Satellite Speeds Test...")
    
    planner = MissionPlanner(planet_radius=EARTH_RADIUS)
    
    # Add a single orbit
    orbit = planner.add_orbit(EARTH_RADIUS + 5000)
    
    # Add satellites with varying speeds
    speeds = [0.0005, 0.001, 0.0015, 0.002, 0.0025]
    for i, speed in enumerate(speeds):
        angle = i * 2 * np.pi / len(speeds)
        planner.add_satellite(orbit, angle, speed)
    
    # Add launch pad
    planner.add_launch_pad(0)
    
    # Calculate best pad and simulate mission
    best_pad, fuel = planner.calculate_best_launch_pad()
    print(f"Best launch pad angle: {best_pad.angle * 180 / np.pi:.1f}° with fuel: {fuel:.1f}")
    
    planner.simulate_mission(best_pad)
    planner.visualize(animation=True)

def test_rocket_equation_effects():
    """Test to demonstrate the effect of tanker mass on delta-v requirements"""
    print("Running Rocket Equation Effects Test...")
    
    planner = MissionPlanner(planet_radius=EARTH_RADIUS)
    
    # Add two orbits
    low_orbit = planner.add_orbit(EARTH_RADIUS + 2000)
    high_orbit = planner.add_orbit(EARTH_RADIUS + 20000)
    
    # Add a satellite to the high orbit
    planner.add_satellite(high_orbit, 0, 0.0002)
    
    # Add one launch pad
    pad = planner.add_launch_pad(0)
    
    # Create three tankers with different mass ratios
    light_tanker = RefuelTanker(
        position=pad.position,
        velocity=(0, 0),
        dry_mass=200.0,  # Light structure
        fuel=1000.0,
        specific_impulse=300.0
    )
    
    medium_tanker = RefuelTanker(
        position=pad.position,
        velocity=(0, 0),
        dry_mass=500.0,  # Medium structure
        fuel=1000.0,
        specific_impulse=300.0
    )
    
    heavy_tanker = RefuelTanker(
        position=pad.position,
        velocity=(0, 0),
        dry_mass=1000.0,  # Heavy structure
        fuel=1000.0,
        specific_impulse=300.0
    )
    
    # Add all tankers to the planner
    planner.tankers = [light_tanker, medium_tanker, heavy_tanker]
    
    # Calculate theoretical delta-v without rocket equation
    r1 = EARTH_RADIUS + 2000
    r2 = EARTH_RADIUS + 20000
    theoretical_dv = HohmannTransfer.calculate_delta_v(r1, r2)
    
    # Calculate actual delta-v with rocket equation for each tanker
    light_dv = HohmannTransfer.calculate_delta_v(r1, r2, light_tanker)
    medium_dv = HohmannTransfer.calculate_delta_v(r1, r2, medium_tanker)
    heavy_dv = HohmannTransfer.calculate_delta_v(r1, r2, heavy_tanker)
    
    # Print results
    print(f"Theoretical delta-v (no mass effects): {theoretical_dv:.2f} m/s")
    print(f"Light tanker (dry mass: 200kg): achieved delta-v {light_dv:.2f} m/s with {light_tanker.fuel:.2f}kg fuel remaining")
    print(f"Medium tanker (dry mass: 500kg): achieved delta-v {medium_dv:.2f} m/s with {medium_tanker.fuel:.2f}kg fuel remaining")
    print(f"Heavy tanker (dry mass: 1000kg): achieved delta-v {heavy_dv:.2f} m/s with {heavy_tanker.fuel:.2f}kg fuel remaining")
    
    # Create new tankers for simulation
    planner.tankers = []
    
    # Simulate the mission with the medium tanker
    medium_tanker = RefuelTanker(
        position=pad.position,
        velocity=(0, 0),
        dry_mass=500.0,
        fuel=1000.0
    )
    planner.tankers = [medium_tanker]
    
    # Launch to first orbit and then transfer to high orbit
    planner.simulate_launch(medium_tanker, low_orbit)
    planner.simulate_hohmann_transfer(medium_tanker, low_orbit, high_orbit)
    
    # Visualize with remaining fuel displayed
    print(f"Remaining fuel after mission: {medium_tanker.fuel:.2f}kg")
    
    # Create custom plot
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Set limits with some padding
    max_radius = max([o.radius for o in planner.orbits], default=planner.planet_radius * 2)
    limit = max_radius * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect('equal')
    
    # Draw planet
    planet = plt.Circle((0, 0), planner.planet_radius, color='blue', alpha=0.7)
    ax.add_patch(planet)
    
    # Draw orbits
    for orbit in planner.orbits:
        circle = plt.Circle((0, 0), orbit.radius, fill=False, color='gray', linestyle='--')
        ax.add_patch(circle)
    
    # Draw satellite
    satellite = high_orbit.satellites[0]
    ax.scatter(satellite.position[0], satellite.position[1], color='green', s=50, label='Satellite')
    
    # Draw tanker trajectory with color based on remaining fuel
    trajectory = np.array(medium_tanker.trajectory)
    ax.plot(trajectory[:, 0], trajectory[:, 1], 'r-', linewidth=1.5, label='Tanker Trajectory')
    
    # Draw tanker at final position
    ax.scatter(medium_tanker.position[0], medium_tanker.position[1], color='orange', s=100, label='Tanker')
    
    # Add a fuel gauge
    fuel_percent = medium_tanker.fuel / 1000.0 * 100
    ax.text(0.05, 0.05, f"Fuel: {medium_tanker.fuel:.1f}kg ({fuel_percent:.1f}%)", 
            transform=ax.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.7))
    
    ax.set_title('Rocket Equation Effects on Tanker Missions')
    ax.legend(loc='upper right')
    
    plt.show()

if __name__ == "__main__":
    # Run each test scenario
    test_simple_system()
    plt.close()  # Close the plot window before starting the next test
    
    test_densely_packed_orbits()
    plt.close()
    
    test_distant_orbits()
    plt.close()
    
    test_different_sized_planet()
    plt.close()
    
    test_multiple_mission_tankers()
    plt.close()
    
    test_various_satellite_speeds()
    plt.close()
    
    # Run the rocket equation test
    test_rocket_equation_effects() 