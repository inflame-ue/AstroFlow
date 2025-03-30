import unittest
from test import MissionPlanner, RefuelTanker, EARTH_RADIUS, Orbit, Satellite
import numpy as np
import matplotlib.pyplot as plt

class TestLaunchSimulation(unittest.TestCase):
    def setUp(self):
        # Create a tanker
        self.tanker = RefuelTanker(
            position=(EARTH_RADIUS, 0),
            velocity=(0, 0),
            fuel=1000.0,
            dry_mass=500.0
        )
        
        # Create a mission planner
        self.planner = MissionPlanner(planet_radius=EARTH_RADIUS, tanker=self.tanker)
        
        # Add an orbit
        self.orbit = self.planner.add_orbit(EARTH_RADIUS + 1500)
        
        # Add a satellite
        self.satellite = self.planner.add_satellite(self.orbit, 0.5, 0.001)
        
        # Add a launch pad
        self.pad = self.planner.add_launch_pad(0.0)
    
    def test_launch_simulation(self):
        """Test that the launch simulation generates a valid trajectory"""
        # Set tanker to launch pad position
        self.tanker.position = self.pad.position
        self.tanker.trajectory = [self.pad.position]
        
        # Run launch simulation
        final_pos, steps = self.planner.run_launch_simulation(self.tanker, self.orbit)
        
        # Check that the trajectory has the correct number of points
        self.assertEqual(len(self.tanker.trajectory), steps + 1)  # +1 for the initial position
        
        # Check that the final position is at the target orbit radius
        distance_from_center = np.sqrt(final_pos[0]**2 + final_pos[1]**2)
        self.assertAlmostEqual(distance_from_center, self.orbit.radius, delta=1.0)
        
        # Visualize the test
        self.visualize_test()
    
    def visualize_test(self):
        """Visualize the test results"""
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')
        
        # Plot planet
        planet = plt.Circle((0, 0), EARTH_RADIUS, color='blue', alpha=0.3)
        ax.add_patch(planet)
        
        # Plot orbit
        orbit_circle = plt.Circle((0, 0), self.orbit.radius, fill=False, color='grey', linestyle='--')
        ax.add_patch(orbit_circle)
        
        # Plot satellite
        ax.plot(self.satellite.position[0], self.satellite.position[1], 'ko', markersize=5)
        
        # Plot launch pad
        ax.plot(self.pad.position[0], self.pad.position[1], 'r^', markersize=8)
        
        # Plot tanker trajectory
        traj_x, traj_y = zip(*self.tanker.trajectory)
        ax.plot(traj_x, traj_y, 'g-', linewidth=2)
        
        # Plot tanker final position
        ax.plot(self.tanker.position[0], self.tanker.position[1], 'go', markersize=8)
        
        # Set limits and labels
        max_radius = self.orbit.radius * 1.1
        ax.set_xlim(-max_radius, max_radius)
        ax.set_ylim(-max_radius, max_radius)
        ax.set_xlabel('X Position (km)')
        ax.set_ylabel('Y Position (km)')
        ax.set_title('Launch Simulation Test')
        
        plt.grid(True)
        plt.savefig('test_launch_simulation.png')
        plt.show()

if __name__ == '__main__':
    unittest.main() 