import numpy as np
import matplotlib.pyplot as plt
from algo8 import (
    EARTH_RADIUS, LaunchPad, Tanker, SimulateMission,
    MU, FUEL_MASS_PER_DELTA_V_KG_PER_KMS, FUEL_DENSITY_KG_PER_LITER
)

def run_test_case(test_name, launch_pads, orbit_altitudes, satellite_config, efficiency_formula=None):
    """
    Run a test case with the given parameters
    
    Parameters:
    - test_name: Name of the test
    - launch_pads: List of LaunchPad objects
    - orbit_altitudes: List of orbit altitudes (km)
    - satellite_config: Dictionary mapping orbit index to list of satellite angles (radians)
    - efficiency_formula: Function that takes angle and returns efficiency factor (if None, uses default)
    """
    print(f"\n{'='*20} TEST: {test_name} {'='*20}")
    print(f"Orbits: {orbit_altitudes}")
    print(f"Launch Pads: {[pad.angle for pad in launch_pads]}")
    
    best_sim_instance = None
    min_fuel_usage = float('inf')
    best_launch_pad_angle = None
    fuel_results = {}
    
    for i, launch_pad in enumerate(launch_pads):
        print(f"\n--- Running Simulation for Launch Pad {i+1} (Angle: {launch_pad.angle:.2f} rad) ---")
        
        # Create a fresh environment
        tanker = Tanker(EARTH_RADIUS, 0, 0)
        sim = SimulateMission(EARTH_RADIUS, tanker)
        
        # Add launch pad and store all for visualization
        sim.add_launch_pad(launch_pad)
        sim.add_all_launch_pads(launch_pads)
        
        # Add orbits
        orbits = [sim.add_orbit(EARTH_RADIUS + alt) for alt in orbit_altitudes]
        
        # Add satellites
        for orbit_idx, angles in satellite_config.items():
            if orbit_idx < len(orbits):
                for angle in angles:
                    sim.add_satellite(orbits[orbit_idx], angle)
        
        # Run simulation
        try:
            # Reset simulation state
            sim.mission_clock = 0.0
            sim.total_delta_v = 0.0
            sim.tanker_mission_trajectory = []
            sim.tanker.mission_events = []
            sim.tanker.shuttles_deployed = []
            sim.tanker.shuttles_recovered = []
            sim.tanker.active = True
            
            # Set custom efficiency if provided
            if efficiency_formula:
                sim.launch_pad_efficiency = efficiency_formula(launch_pad.angle)
            else:
                # Default formula from the main code
                sim.launch_pad_efficiency = 0.8 + 0.4 * (abs(launch_pad.angle) % np.pi) / np.pi
            
            # Run simulation
            sim.simulate_mission()
            
            # Calculate fuel and store results
            fuel_usage = sim.get_total_fuel_liters()
            fuel_results[launch_pad.angle] = (fuel_usage, sim.launch_pad_efficiency)
            
            # Check if this is best run
            if fuel_usage < min_fuel_usage:
                min_fuel_usage = fuel_usage
                best_sim_instance = sim
                best_launch_pad_angle = launch_pad.angle
                
        except Exception as e:
            print(f"Simulation failed: {e}")
            continue
    
    # Print results
    print("\n--- Fuel Usage Results ---")
    for angle, (fuel, efficiency) in sorted(fuel_results.items()):
        print(f"Launch Pad Angle: {angle:.2f} rad, Efficiency: {efficiency:.2f}, Fuel Used: {fuel:,.0f} L")
    
    if best_sim_instance:
        print(f"\nOptimal Launch Pad Angle: {best_launch_pad_angle:.2f} rad")
        print(f"Minimum Estimated Fuel: {min_fuel_usage:,.0f} L")
        
        # Show visualization of best run
        if best_sim_instance.tanker_mission_trajectory and len(best_sim_instance.tanker_mission_trajectory) > 1:
            print(f"\nShowing visualization for '{test_name}' - optimal trajectory...")
            try:
                fig, ani = best_sim_instance.visualize()
                plt.show(block=True)  # Show and wait for window to close
                plt.close(fig)
            except Exception as e:
                print(f"Visualization failed: {e}")
    
    return best_sim_instance, fuel_results

def test_different_orbit_counts():
    """Test with different numbers of orbits"""
    launch_pads = [
        LaunchPad(EARTH_RADIUS, 0),
        LaunchPad(EARTH_RADIUS, np.pi/2),
        LaunchPad(EARTH_RADIUS, np.pi),
    ]
    
    # Two orbits
    run_test_case(
        "Two Orbits Only",
        launch_pads,
        [500, 3000],  # Just two orbits
        {
            0: [0, np.deg2rad(120), np.deg2rad(240)],
            1: [np.deg2rad(90), np.deg2rad(270)],
        },
        lambda angle: 0.8 + 0.4 * np.sin(angle)  # Different efficiency formula
    )
    
    # Four orbits
    run_test_case(
        "Four Orbits",
        launch_pads,
        [500, 2000, 5000, 10000],  # Four orbits
        {
            0: [0, np.pi/2, np.pi, 3*np.pi/2],
            1: [np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4],
            2: [0, np.pi],
            3: [np.pi/2, 3*np.pi/2],
        }
    )

def test_different_efficiency_models():
    """Test with different efficiency models"""
    launch_pads = [
        LaunchPad(EARTH_RADIUS, 0),
        LaunchPad(EARTH_RADIUS, np.pi/4),
        LaunchPad(EARTH_RADIUS, np.pi/2),
        LaunchPad(EARTH_RADIUS, 3*np.pi/4),
        LaunchPad(EARTH_RADIUS, np.pi),
    ]
    
    # Cosine model - best efficiency at 0 and pi
    run_test_case(
        "Cosine Efficiency Model",
        launch_pads,
        [500, 3000, 8000],  # Standard orbits
        {
            0: [0, np.deg2rad(120), np.deg2rad(240)],
            1: [np.deg2rad(90), np.deg2rad(270)],
            2: [np.deg2rad(180)],
        },
        lambda angle: 0.8 + 0.2 * np.cos(angle)  # Cosine model
    )
    
    # Sine model - best efficiency at pi/2 and 3pi/2
    run_test_case(
        "Sine Efficiency Model",
        launch_pads,
        [500, 3000, 8000],  # Standard orbits
        {
            0: [0, np.deg2rad(120), np.deg2rad(240)],
            1: [np.deg2rad(90), np.deg2rad(270)],
            2: [np.deg2rad(180)],
        },
        lambda angle: 0.8 + 0.2 * np.sin(angle)  # Sine model
    )

def test_many_launch_pads():
    """Test with many launch pads around the Earth"""
    # Create 8 launch pads evenly spaced around the Earth
    angles = np.linspace(0, 2*np.pi, 9)[:-1]  # 8 angles, exclude last (same as first)
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    run_test_case(
        "Eight Launch Pads",
        launch_pads,
        [500, 3000, 8000],  # Standard orbits
        {
            0: [0, np.deg2rad(120), np.deg2rad(240)],
            1: [np.deg2rad(90), np.deg2rad(270)],
            2: [np.deg2rad(180)],
        },
        lambda angle: 0.8 + 0.4 * np.abs(np.sin(angle))  # Efficiency formula
    )

def test_complex_satellites():
    """Test with many satellites in different configurations"""
    launch_pads = [
        LaunchPad(EARTH_RADIUS, 0),
        LaunchPad(EARTH_RADIUS, np.pi/2),
        LaunchPad(EARTH_RADIUS, np.pi),
    ]
    
    # Many satellites in all orbits
    run_test_case(
        "Many Satellites",
        launch_pads,
        [500, 2000, 5000],
        {
            0: np.linspace(0, 2*np.pi, 7)[:-1].tolist(),  # 6 satellites evenly spaced
            1: np.linspace(0, 2*np.pi, 5)[:-1].tolist(),  # 4 satellites evenly spaced
            2: np.linspace(0, 2*np.pi, 3)[:-1].tolist(),  # 2 satellites evenly spaced
        }
    )

if __name__ == "__main__":
    # Set figure size for all plots
    plt.rcParams["figure.figsize"] = (12, 10)
    
    print("Starting algorithm tests...")
    
    # Run all test cases
    test_different_orbit_counts()
    test_different_efficiency_models()
    test_many_launch_pads()
    test_complex_satellites()
    
    print("\nAll tests completed.") 