import numpy as np
import matplotlib.pyplot as plt
from algo8 import (
    EARTH_RADIUS, LaunchPad, Tanker, SimulateMission,
    MU, FUEL_MASS_PER_DELTA_V_KG_PER_KMS, FUEL_DENSITY_KG_PER_LITER
)

def run_test_case(test_name, launch_pads, orbit_altitudes, satellite_config, efficiency_formula=None, return_all_results=False):
    """
    Run a test case with the given parameters
    
    Parameters:
    - test_name: Name of the test
    - launch_pads: List of LaunchPad objects
    - orbit_altitudes: List of orbit altitudes (km)
    - satellite_config: Dictionary mapping orbit index to list of satellite angles (radians)
    - efficiency_formula: Function that takes angle and returns efficiency factor (if None, uses default)
    - return_all_results: If True, return all sim instances in addition to the best one
    """
    print(f"\n{'='*20} TEST: {test_name} {'='*20}")
    print(f"Orbits: {orbit_altitudes}")
    print(f"Launch Pads: {[pad.angle for pad in launch_pads]}")
    
    best_sim_instance = None
    min_fuel_usage = float('inf')
    best_launch_pad_angle = None
    fuel_results = {}
    all_sim_instances = {}
    
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
            
            # Store simulation instance if requested
            if return_all_results:
                all_sim_instances[launch_pad.angle] = sim
            
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
    
    if return_all_results:
        return best_sim_instance, fuel_results, all_sim_instances
    else:
        return best_sim_instance, fuel_results

def test_asymmetric_orbit_distribution():
    """Test with asymmetrically distributed orbits"""
    # Launch pads at 8 different angles
    angles = np.linspace(0, 2*np.pi, 9)[:-1]  # 8 angles, exclude last (same as first)
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    # Asymmetric orbit distribution (concentrated more on one side)
    run_test_case(
        "Asymmetric Orbit Distribution",
        launch_pads,
        [500, 1500, 2500, 3500, 5000],  # 5 orbits
        {
            0: [0, np.pi/4, np.pi/2, 3*np.pi/4],  # More satellites on one side (0-90°)
            1: [0, np.pi/3],
            2: [0],
            3: [np.pi/6],
            4: [np.pi/8],
        },
        lambda angle: 0.7 + 0.6 * (1 - abs(angle % (2*np.pi) - np.pi/4)/(np.pi))  # Best efficiency at π/4
    )

def test_dynamic_efficiency_model():
    """Test with a more complex efficiency model that changes based on orbit targeted"""
    launch_pads = [
        LaunchPad(EARTH_RADIUS, 0),
        LaunchPad(EARTH_RADIUS, np.pi/6),
        LaunchPad(EARTH_RADIUS, np.pi/3),
        LaunchPad(EARTH_RADIUS, np.pi/2),
        LaunchPad(EARTH_RADIUS, 2*np.pi/3),
        LaunchPad(EARTH_RADIUS, 5*np.pi/6),
        LaunchPad(EARTH_RADIUS, np.pi),
        LaunchPad(EARTH_RADIUS, 7*np.pi/6),
        LaunchPad(EARTH_RADIUS, 4*np.pi/3),
        LaunchPad(EARTH_RADIUS, 3*np.pi/2),
        LaunchPad(EARTH_RADIUS, 5*np.pi/3),
        LaunchPad(EARTH_RADIUS, 11*np.pi/6),
    ]
    
    # Define a "wave" efficiency model that varies with more complexity
    def wave_efficiency(angle):
        # Combined sine waves with different frequencies
        return 0.7 + 0.3 * np.sin(angle) + 0.2 * np.sin(3*angle)
    
    run_test_case(
        "Complex Wave Efficiency Model",
        launch_pads,
        [500, 2000, 5000, 10000],
        {
            0: np.linspace(0, 2*np.pi, 13)[:-1].tolist(),  # 12 evenly spaced satellites
            1: np.linspace(0, 2*np.pi, 9)[:-1].tolist(),   # 8 evenly spaced satellites
            2: np.linspace(0, 2*np.pi, 5)[:-1].tolist(),   # 4 evenly spaced satellites
            3: np.linspace(0, 2*np.pi, 3)[:-1].tolist(),   # 2 evenly spaced satellites
        },
        wave_efficiency
    )

def test_seasonal_variation():
    """Simulates seasonal variations in launch efficiency due to Earth's position"""
    # Use 24 launch pads to simulate different times of year
    angles = np.linspace(0, 2*np.pi, 25)[:-1]  # 24 angles
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    # Seasonal variation model - efficiency peaks at certain "seasons" (angles)
    def seasonal_efficiency(angle):
        # Model with four seasonal peaks (roughly at 0, π/2, π, 3π/2)
        season_factor = np.cos(4*angle)
        # Add some randomness to represent weather and other unpredictable factors
        random_factor = np.random.uniform(0.95, 1.05)
        return (0.9 + 0.3 * season_factor) * random_factor
    
    run_test_case(
        "Seasonal Launch Efficiency",
        launch_pads,
        [500, 2000, 5000, 8000, 12000],
        {
            0: np.linspace(0, 2*np.pi, 13)[:-1].tolist(),
            1: np.linspace(0, 2*np.pi, 9)[:-1].tolist(),
            2: np.linspace(0, 2*np.pi, 7)[:-1].tolist(),
            3: np.linspace(0, 2*np.pi, 5)[:-1].tolist(),
            4: np.linspace(0, 2*np.pi, 3)[:-1].tolist(),
        },
        seasonal_efficiency
    )

def test_geopolitical_constraints():
    """Simulates launch efficiency based on geopolitical constraints (some regions better than others)"""
    # 16 launch pads around the globe
    angles = np.linspace(0, 2*np.pi, 17)[:-1]
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    # Geopolitical constraints model
    # Some regions are more favorable for launches due to infrastructure, regulations, etc.
    def geopolitical_efficiency(angle):
        # Define "favorable regions" (e.g., 0-π/4, π-5π/4, 3π/2-7π/4)
        favorable_regions = [
            (0, np.pi/4),           # Region 1 (highly favorable)
            (np.pi, 5*np.pi/4),     # Region 2 (highly favorable)
            (3*np.pi/2, 7*np.pi/4)  # Region 3 (favorable)
        ]
        
        # Check if angle is in a favorable region
        in_region_1 = favorable_regions[0][0] <= angle <= favorable_regions[0][1]
        in_region_2 = favorable_regions[1][0] <= angle <= favorable_regions[1][1]
        in_region_3 = favorable_regions[2][0] <= angle <= favorable_regions[2][1]
        
        # Base efficiency
        base = 0.9
        
        # Apply regional bonus
        if in_region_1:
            return base * 0.7  # 30% more efficient
        elif in_region_2:
            return base * 0.75  # 25% more efficient
        elif in_region_3:
            return base * 0.8  # 20% more efficient
        else:
            return base * (1.0 + 0.2 * np.sin(angle))  # Variable efficiency in other regions
    
    run_test_case(
        "Geopolitical Launch Constraints",
        launch_pads,
        [500, 2500, 5000, 10000],
        {
            0: np.linspace(0, 2*np.pi, 9)[:-1].tolist(),
            1: np.linspace(0, 2*np.pi, 7)[:-1].tolist(),
            2: np.linspace(0, 2*np.pi, 5)[:-1].tolist(),
            3: np.linspace(0, 2*np.pi, 3)[:-1].tolist(),
        },
        geopolitical_efficiency
    )

def test_fuel_types():
    """Simulates different fuel types available at different launch sites"""
    # 12 launch pads
    angles = np.linspace(0, 2*np.pi, 13)[:-1]
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    # Model different fuel types with different efficiencies
    def fuel_type_efficiency(angle):
        # Quantize the angles into 4 groups representing different fuel types
        # Fuel types: High-performance (0.7), Standard (0.9), Economic (1.1), Low-grade (1.3)
        angle_group = int((angle / (2*np.pi)) * 4)
        
        fuel_types = [0.7, 0.9, 1.1, 1.3]
        return fuel_types[angle_group % 4]
    
    run_test_case(
        "Different Fuel Types",
        launch_pads,
        [500, 2000, 4000, 8000],
        {
            0: np.linspace(0, 2*np.pi, 9)[:-1].tolist(),
            1: np.linspace(0, 2*np.pi, 7)[:-1].tolist(),
            2: np.linspace(0, 2*np.pi, 5)[:-1].tolist(),
            3: np.linspace(0, 2*np.pi, 3)[:-1].tolist(),
        },
        fuel_type_efficiency
    )

def test_precise_planetary_alignment():
    """Tests optimal launch timing based on precise planetary alignment"""
    # 36 launch pads to represent precise timing options (10° spacing)
    angles = np.linspace(0, 2*np.pi, 37)[:-1]
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    # Planetary alignment efficiency model
    def planetary_alignment_efficiency(angle):
        # Model gravitational assistance from planetary alignment
        # Best alignment at specific angles (0, π/3, 2π/3, π, 4π/3, 5π/3)
        alignment_points = [0, np.pi/3, 2*np.pi/3, np.pi, 4*np.pi/3, 5*np.pi/3]
        
        # Find closest alignment point
        min_distance = min(abs(angle - point) % (2*np.pi) for point in alignment_points)
        normalized_distance = min_distance / (np.pi/3)  # Normalize by max possible distance
        
        # Higher efficiency (lower value) when closer to an alignment point
        return 0.7 + 0.5 * normalized_distance
    
    run_test_case(
        "Planetary Alignment Optimization",
        launch_pads,
        [500, 1500, 3000, 6000, 12000],
        {
            0: np.linspace(0, 2*np.pi, 13)[:-1].tolist(),
            1: np.linspace(0, 2*np.pi, 9)[:-1].tolist(),
            2: np.linspace(0, 2*np.pi, 7)[:-1].tolist(),
            3: np.linspace(0, 2*np.pi, 5)[:-1].tolist(),
            4: np.linspace(0, 2*np.pi, 3)[:-1].tolist(),
        },
        planetary_alignment_efficiency
    )

def test_multi_phase_mission():
    """Test a multi-phase mission with complex orbit configurations"""
    # 8 main launch positions
    angles = np.linspace(0, 2*np.pi, 9)[:-1]
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    # Complex mission with many orbits and strategic satellite placements
    run_test_case(
        "Multi-Phase Mission",
        launch_pads,
        [500, 1000, 2000, 3500, 5000, 7500, 10000],  # 7 orbits
        {
            0: [0, np.pi/4, np.pi/2, 3*np.pi/4, np.pi, 5*np.pi/4, 3*np.pi/2, 7*np.pi/4],  # 8 satellites
            1: [0, np.pi/3, 2*np.pi/3, np.pi, 4*np.pi/3, 5*np.pi/3],  # 6 satellites
            2: [0, np.pi/2, np.pi, 3*np.pi/2],  # 4 satellites
            3: [0, 2*np.pi/3, 4*np.pi/3],  # 3 satellites
            4: [np.pi/4, 3*np.pi/4, 5*np.pi/4, 7*np.pi/4],  # 4 satellites
            5: [0, np.pi],  # 2 satellites
            6: [np.pi/2],  # 1 satellite
        },
        lambda angle: 0.75 + 0.25 * np.cos(2*angle)  # Efficiency model
    )

def test_targeted_interception():
    """Tests a scenario optimized for intercepting specific targets"""
    # Use 12 launch pads for precise targeting
    angles = np.linspace(0, 2*np.pi, 13)[:-1]
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    # Strategic satellite placement for interception scenario
    satellite_config = {
        0: [0],  # One satellite in lowest orbit
        1: [np.pi/6, 5*np.pi/6],  # Two satellites in second orbit
        2: [np.pi/3, np.pi, 5*np.pi/3],  # Three satellites in third orbit
        3: [0, np.pi/2, np.pi, 3*np.pi/2],  # Four satellites in highest orbit
    }
    
    # Efficiency depends on angle relative to target satellites
    def interception_efficiency(angle):
        # Target satellite positions for interception
        target_positions = [0, np.pi/2, np.pi, 3*np.pi/2]
        
        # Find minimum angular distance to a target
        min_distance = min(abs(angle - target) % (2*np.pi) for target in target_positions)
        normalized_distance = min_distance / (np.pi/2)
        
        # Better efficiency when closer to potential interception point
        return 0.7 + 0.4 * normalized_distance
    
    run_test_case(
        "Targeted Interception",
        launch_pads,
        [500, 2000, 5000, 10000],
        satellite_config,
        interception_efficiency
    )

def compare_multiple_efficiency_models():
    """Compare different efficiency models on the same orbit configuration"""
    # Use 16 launch pads
    angles = np.linspace(0, 2*np.pi, 17)[:-1]
    launch_pads = [LaunchPad(EARTH_RADIUS, angle) for angle in angles]
    
    # Standard orbit and satellite configuration
    orbit_altitudes = [500, 2000, 5000, 10000]
    satellite_config = {
        0: np.linspace(0, 2*np.pi, 9)[:-1].tolist(),
        1: np.linspace(0, 2*np.pi, 7)[:-1].tolist(),
        2: np.linspace(0, 2*np.pi, 5)[:-1].tolist(),
        3: np.linspace(0, 2*np.pi, 3)[:-1].tolist(),
    }
    
    # Define different efficiency models to compare
    efficiency_models = {
        "Sinusoidal": lambda angle: 0.8 + 0.2 * np.sin(angle),
        "Cosine": lambda angle: 0.8 + 0.2 * np.cos(angle),
        "Combined": lambda angle: 0.8 + 0.1 * np.sin(angle) + 0.1 * np.cos(2*angle),
        "Step Function": lambda angle: 0.8 if angle < np.pi else 1.0,
        "Linear": lambda angle: 0.8 + 0.4 * (angle / (2*np.pi))
    }
    
    # Run test cases with each efficiency model
    results = {}
    
    for model_name, efficiency_func in efficiency_models.items():
        print(f"\nTesting efficiency model: {model_name}")
        _, fuel_results = run_test_case(
            f"Efficiency Model Comparison - {model_name}",
            launch_pads,
            orbit_altitudes,
            satellite_config,
            efficiency_func
        )
        results[model_name] = fuel_results
    
    # Summarize and compare results
    print("\n--- Efficiency Model Comparison Summary ---")
    for model_name, fuel_results in results.items():
        min_fuel = min(fuel[0] for fuel in fuel_results.values())
        max_fuel = max(fuel[0] for fuel in fuel_results.values())
        avg_fuel = sum(fuel[0] for fuel in fuel_results.values()) / len(fuel_results)
        print(f"{model_name}: Min={min_fuel:,.0f}L, Max={max_fuel:,.0f}L, Avg={avg_fuel:,.0f}L, Range={max_fuel-min_fuel:,.0f}L")

if __name__ == "__main__":
    # Set figure size for all plots
    plt.rcParams["figure.figsize"] = (14, 12)
    
    print("Starting advanced algorithm tests...")
    
    # Run the advanced test cases
    test_asymmetric_orbit_distribution()
    test_dynamic_efficiency_model()
    test_seasonal_variation()
    test_geopolitical_constraints()
    test_fuel_types()
    test_precise_planetary_alignment()
    test_multi_phase_mission()
    test_targeted_interception()
    compare_multiple_efficiency_models()
    
    print("\nAll advanced tests completed.") 