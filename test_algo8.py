import unittest
import numpy as np
import math
from algo8 import (
    EARTH_RADIUS, MU, FUEL_MASS_PER_DELTA_V_KG_PER_KMS, FUEL_DENSITY_KG_PER_LITER,
    Orbit, LaunchPad, SpaceCraft, Satellite, Shuttle, Tanker, SimulateMission
)

class TestBasicClasses(unittest.TestCase):
    """Test the basic classes used in the simulation"""
    
    def test_spacecraft_initialization(self):
        """Test if SpaceCraft objects initialize correctly"""
        radius = EARTH_RADIUS + 500
        angle = np.pi/4
        velocity = 0.001  # angular velocity in rad/s
        
        spacecraft = SpaceCraft(radius, angle, velocity)
        self.assertEqual(spacecraft.radius, radius)
        self.assertEqual(spacecraft.angle, angle)
        self.assertEqual(spacecraft.speed, velocity)
        self.assertTrue(spacecraft.visible)
        self.assertTrue(spacecraft.active)
    
    def test_spacecraft_update(self):
        """Test if spacecraft position updates correctly"""
        radius = EARTH_RADIUS + 500
        angle = 0
        velocity = 0.001  # rad/s
        
        spacecraft = SpaceCraft(radius, angle, velocity)
        time_step = 100  # seconds
        spacecraft.update(time_step)
        
        # Expected new angle
        expected_angle = (angle + velocity * time_step) % (2 * np.pi)
        self.assertAlmostEqual(spacecraft.angle, expected_angle)
        
        # Position calculation
        pos = spacecraft.position()
        expected_x = radius * np.cos(expected_angle)
        expected_y = radius * np.sin(expected_angle)
        self.assertAlmostEqual(pos[0], expected_x)
        self.assertAlmostEqual(pos[1], expected_y)
    
    def test_satellite_creation(self):
        """Test Satellite child class"""
        radius = EARTH_RADIUS + 1000
        angle = np.pi/2
        velocity = 0.001
        
        sat = Satellite(radius, angle, velocity)
        self.assertEqual(sat.initial_angle, angle)
        self.assertIn(f"Sat-{int(radius)}", sat.id)
    
    def test_shuttle_creation(self):
        """Test Shuttle child class"""
        radius = EARTH_RADIUS + 1500
        angle = np.pi
        velocity = 0.001
        
        shuttle = Shuttle(radius, angle, velocity)
        self.assertFalse(shuttle.deployed)
        self.assertFalse(shuttle.intercepted)
        self.assertIsNone(shuttle.deployment_time)
        self.assertIsNone(shuttle.recovery_time)
        self.assertIn(f"Shuttle-{int(radius)}", shuttle.id)
    
    def test_tanker_creation(self):
        """Test Tanker class"""
        radius = EARTH_RADIUS
        angle = 0
        fuel = 5000
        
        tanker = Tanker(radius, angle, 0, fuel)
        self.assertEqual(tanker.fuel, fuel)
        self.assertEqual(tanker.mode, "launch")
        self.assertTrue(tanker.outbound)
        self.assertEqual(len(tanker.shuttles_deployed), 0)
        self.assertEqual(len(tanker.shuttles_recovered), 0)

    def test_orbit_creation(self):
        """Test if Orbit initializes correctly"""
        radius = EARTH_RADIUS + 800
        inclination = 0.1
        
        orbit = Orbit(radius, inclination)
        self.assertEqual(orbit.radius, radius)
        self.assertEqual(orbit.inclination, inclination)
        self.assertEqual(len(orbit.satellites), 0)
        self.assertEqual(len(orbit.shuttles), 0)
    
    def test_launchpad_creation(self):
        """Test if LaunchPad initializes correctly"""
        radius = EARTH_RADIUS
        angle = np.pi/4
        
        pad = LaunchPad(radius, angle)
        self.assertEqual(pad.position, radius)
        self.assertEqual(pad.angle, angle)

class TestSimulateMission(unittest.TestCase):
    """Test the SimulateMission class"""
    
    def setUp(self):
        """Set up common test objects"""
        self.tanker = Tanker(EARTH_RADIUS, 0, 0, 10000)
        self.sim = SimulateMission(EARTH_RADIUS, self.tanker)
        
        # Add a couple of launch pads
        self.sim.add_launch_pad(LaunchPad(EARTH_RADIUS, 0))
        self.sim.add_launch_pad(LaunchPad(EARTH_RADIUS, np.pi/2))
        
        # Add some orbits
        self.orbit1 = self.sim.add_orbit(EARTH_RADIUS + 500)
        self.orbit2 = self.sim.add_orbit(EARTH_RADIUS + 1000)
        self.orbit3 = self.sim.add_orbit(EARTH_RADIUS + 3000)
        
        # Add some satellites
        self.sat1 = self.sim.add_satellite(self.orbit1, 0)
        self.sat2 = self.sim.add_satellite(self.orbit2, np.pi/2)
        self.sat3 = self.sim.add_satellite(self.orbit3, np.pi)
    
    def test_mission_initialization(self):
        """Test if SimulateMission initializes correctly"""
        self.assertEqual(self.sim.planet_radius, EARTH_RADIUS)
        self.assertEqual(self.sim.mission_clock, 0)
        self.assertEqual(len(self.sim.orbits), 3)
        self.assertEqual(len(self.sim.satellites), 3)
        self.assertEqual(len(self.sim.launch_pads), 2)
    
    def test_orbit_index_finding(self):
        """Test if orbit index is found correctly"""
        # Move tanker to the first orbit
        self.tanker.radius = self.orbit1.radius
        index = self.sim.find_current_orbit_index()
        self.assertEqual(index, 0)
        
        # Move tanker to second orbit
        self.tanker.radius = self.orbit2.radius
        index = self.sim.find_current_orbit_index()
        self.assertEqual(index, 1)
        
        # Test with tanker in between orbits (should return -1)
        self.tanker.radius = (self.orbit1.radius + self.orbit2.radius) / 2
        index = self.sim.find_current_orbit_index()
        self.assertEqual(index, -1)
    
    def test_deploy_shuttle(self):
        """Test shuttle deployment"""
        # First move tanker to first orbit
        self.tanker.radius = self.orbit1.radius
        self.tanker.angle = np.pi/4
        
        # Deploy a shuttle
        shuttle = self.sim.deploy_shuttle_to_orbit(self.orbit1)
        
        # Check if shuttle was created correctly
        self.assertEqual(shuttle.radius, self.orbit1.radius)
        self.assertEqual(shuttle.angle, self.tanker.angle)
        self.assertTrue(shuttle.deployed)
        self.assertEqual(shuttle.deployment_time, self.sim.mission_clock)
        
        # Check if shuttle was added to the lists
        self.assertIn(shuttle, self.orbit1.shuttles)
        self.assertIn(shuttle, self.sim.shuttles)
        self.assertIn(shuttle, self.tanker.shuttles_deployed)
    
    def test_recover_shuttle(self):
        """Test shuttle recovery"""
        # Setup: deploy a shuttle first
        self.tanker.radius = self.orbit1.radius
        self.tanker.angle = np.pi/4
        shuttle = self.sim.deploy_shuttle_to_orbit(self.orbit1)
        
        # Now recover it (should succeed as tanker and shuttle are at same position)
        success = self.sim.recover_shuttle(shuttle)
        self.assertTrue(success)
        
        # Check if recovery was recorded
        self.assertIn(shuttle, self.tanker.shuttles_recovered)
        self.assertTrue(shuttle.intercepted)
        self.assertFalse(shuttle.active)
        self.assertEqual(shuttle.recovery_time, self.sim.mission_clock)
    
    def test_fuel_calculation(self):
        """Test fuel calculation based on delta-v"""
        # Set a specific delta-v value
        self.sim.total_delta_v = 10.0  # km/s
        
        # Test with default efficiency
        self.sim.launch_pad_efficiency = 1.0
        fuel_liters = self.sim.get_total_fuel_liters()
        expected_fuel = 10.0 * FUEL_MASS_PER_DELTA_V_KG_PER_KMS / FUEL_DENSITY_KG_PER_LITER
        self.assertEqual(fuel_liters, expected_fuel)
        
        # Test with custom efficiency
        self.sim.launch_pad_efficiency = 0.8
        fuel_liters = self.sim.get_total_fuel_liters()
        expected_fuel = 10.0 * FUEL_MASS_PER_DELTA_V_KG_PER_KMS * 0.8 / FUEL_DENSITY_KG_PER_LITER
        self.assertEqual(fuel_liters, expected_fuel)

class TestLaunchPadOptimization(unittest.TestCase):
    """Test launch pad efficiency and optimization"""
    
    def test_launch_pad_efficiency(self):
        """Test if different launch pads result in different fuel usage"""
        # Create simulation objects for different launch pads
        results = []
        
        for angle in [0, np.pi/4, np.pi/2, np.pi]:
            tanker = Tanker(EARTH_RADIUS, 0, 0)
            sim = SimulateMission(EARTH_RADIUS, tanker)
            
            # Add launch pad
            sim.add_launch_pad(LaunchPad(EARTH_RADIUS, angle))
            
            # Add orbits
            orbit1 = sim.add_orbit(EARTH_RADIUS + 500)
            orbit2 = sim.add_orbit(EARTH_RADIUS + 1000)
            
            # Add satellites
            sim.add_satellite(orbit1, 0)
            sim.add_satellite(orbit2, 0)
            
            # Set specific efficiency for testing
            sim.launch_pad_efficiency = 0.8 + 0.4 * (abs(angle) % np.pi) / np.pi
            
            # Set a fixed delta-v for testing
            sim.total_delta_v = 10.0
            
            # Calculate fuel
            fuel = sim.get_total_fuel_liters()
            results.append((angle, fuel))
        
        # Check that different angles give different fuel usages
        fuels = [r[1] for r in results]
        self.assertTrue(len(set(fuels)) > 1, "Different launch pads should yield different fuel usages")
        
        # Check specifically if 0 angle (efficiency 0.8) uses less fuel than pi/2 (efficiency 1.0)
        fuel_0 = next(r[1] for r in results if r[0] == 0)
        fuel_pi_2 = next(r[1] for r in results if r[0] == np.pi/2)
        self.assertLess(fuel_0, fuel_pi_2)

class TestOrbitalMechanics(unittest.TestCase):
    """Test basic aspects of orbital mechanics"""
    
    def test_circular_velocity(self):
        """Test calculation of circular orbit velocity"""
        radius = EARTH_RADIUS + 1000  # km
        velocity = np.sqrt(MU / radius)
        
        # Check velocity is reasonable (around 7.3 km/s for this radius)
        self.assertGreater(velocity, 7.0)
        self.assertLess(velocity, 8.0)

if __name__ == '__main__':
    unittest.main() 