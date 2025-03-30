import unittest
import copy  # to avoid modifying original test data
from utils.parser import normalize_form_data

# define the scaling factor used in the function for testing calculations
SCALING_FACTOR = 5000 / 42000

class TestNormalizeFormData(unittest.TestCase):

    def test_basic_normalization(self):
        """Test orbits with radii requiring normalization."""
        input_data = {
            'orbits': {
                '1': {'radius': '20000', 'speed': '7.0'}, # Needs normalization
                '2': {'radius': '42000', 'speed': '5.0'}  # Max value, needs normalization
            }
        }
        expected_radius_1 = 17000 + (20000 - 17000) * SCALING_FACTOR
        expected_radius_2 = 17000 + (42000 - 17000) * SCALING_FACTOR
        print(expected_radius_1, expected_radius_2)
        expected_output = {
            'orbits': {
                '1': {'radius': str(expected_radius_1), 'speed': '7.0'},
                '2': {'radius': str(expected_radius_2), 'speed': '5.0'}
            }
        }
        # Use deepcopy to prevent modification of input_data
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        # Use assertAlmostEqual for floating point comparisons
        self.assertAlmostEqual(float(normalized_data['orbits']['1']['radius']), expected_radius_1)
        self.assertAlmostEqual(float(normalized_data['orbits']['2']['radius']), expected_radius_2)
        # Check other fields remain unchanged
        self.assertEqual(normalized_data['orbits']['1']['speed'], expected_output['orbits']['1']['speed'])
        self.assertEqual(normalized_data['orbits']['2']['speed'], expected_output['orbits']['2']['speed'])


    def test_radius_below_or_equal_threshold(self):
        """Test orbits with radii that should not be normalized."""
        input_data = {
            'orbits': {
                '1': {'radius': '17000', 'speed': '8.0'},
                '2': {'radius': '10000', 'speed': '9.0'}
            }
        }
        # Expected output should match the actual float-to-string conversion
        expected_output = {
             'orbits': {
                 '1': {'radius': '17000.0', 'speed': '8.0'},
                 '2': {'radius': '10000.0', 'speed': '9.0'}
             }
        }
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        self.assertEqual(normalized_data, expected_output)

    def test_radius_above_max_threshold(self):
        """Test orbits with radii above 42000 (should be capped)."""
        input_data = {
            'orbits': {
                '1': {'radius': '50000', 'speed': '4.0'}
            }
        }
        # Expected radius is capped at 42000 then normalized
        expected_radius_1 = 17000 + (42000 - 17000) * SCALING_FACTOR
        expected_output = {
            'orbits': {
                '1': {'radius': str(expected_radius_1), 'speed': '4.0'}
            }
        }
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        self.assertAlmostEqual(float(normalized_data['orbits']['1']['radius']), expected_radius_1)
        self.assertEqual(normalized_data['orbits']['1']['speed'], expected_output['orbits']['1']['speed'])


    def test_satellite_radius_update(self):
        """Test that satellite radii are updated based on normalized orbit radii."""
        input_data = {
            'orbits': {
                'orb1': {'radius': '20000', 'speed': '7.0'},
                'orb2': {'radius': '15000', 'speed': '8.5'}
            },
            'satellites': {
                'sat1': {'angle': '45', 'orbitId': 'orb1', 'radius': 'old_value', 'speed': 'old_speed'},
                'sat2': {'angle': '90', 'orbitId': 'orb2', 'radius': 'other_val', 'speed': 'other_speed'},
                'sat3': {'angle': '180', 'orbitId': 'orb_invalid'} # Should be ignored
            }
        }
        normalized_orbit1_radius = 17000 + (20000 - 17000) * SCALING_FACTOR
        # orb2 radius should remain 15000
        expected_output = {
            'orbits': {
                'orb1': {'radius': str(normalized_orbit1_radius), 'speed': '7.0'},
                'orb2': {'radius': '15000.0', 'speed': '8.5'} # Note: float conversion adds .0
            },
            'satellites': {
                'sat1': {'angle': '45', 'orbitId': 'orb1', 'radius': str(normalized_orbit1_radius), 'speed': '7.0'}, # radius/speed updated
                'sat2': {'angle': '90', 'orbitId': 'orb2', 'radius': '15000.0', 'speed': '8.5'}, # radius/speed updated
                'sat3': {'angle': '180', 'orbitId': 'orb_invalid'} # Unchanged
            }
        }

        expected_output['satellites']['sat1']['speed'] = 'old_speed'
        expected_output['satellites']['sat2']['speed'] = 'other_speed'


        normalized_data = normalize_form_data(copy.deepcopy(input_data))

        # Check orbits (allow for float precision)
        self.assertAlmostEqual(float(normalized_data['orbits']['orb1']['radius']), float(expected_output['orbits']['orb1']['radius']))
        self.assertAlmostEqual(float(normalized_data['orbits']['orb2']['radius']), float(expected_output['orbits']['orb2']['radius']))

        # Check satellites
        self.assertAlmostEqual(float(normalized_data['satellites']['sat1']['radius']), float(expected_output['satellites']['sat1']['radius']))
        self.assertEqual(normalized_data['satellites']['sat1']['speed'], expected_output['satellites']['sat1']['speed']) # Speed should not change based on parser.py

        self.assertAlmostEqual(float(normalized_data['satellites']['sat2']['radius']), float(expected_output['satellites']['sat2']['radius']))
        self.assertEqual(normalized_data['satellites']['sat2']['speed'], expected_output['satellites']['sat2']['speed']) # Speed should not change

        self.assertNotIn('radius', normalized_data['satellites']['sat3']) # Should not have radius added


    def test_empty_input(self):
        """Test behavior with empty dictionary input."""
        input_data = {}
        expected_output = {}
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        self.assertEqual(normalized_data, expected_output)

    # noinspection PyTypeChecker
    def test_none_input(self):
        """Test behavior with None input."""
        input_data = None
        expected_output = None
        normalized_data = normalize_form_data(input_data)
        self.assertEqual(normalized_data, expected_output)

    def test_missing_orbits_key(self):
        """Test input dictionary without the 'orbits' key."""
        input_data = {'satellites': {'sat1': {'angle': '0', 'orbitId': '1'}}}
        expected_output = {'satellites': {'sat1': {'angle': '0', 'orbitId': '1'}}}
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        self.assertEqual(normalized_data, expected_output)

    def test_orbit_missing_radius_key(self):
        """Test an orbit dictionary missing the 'radius' key."""
        input_data = {
            'orbits': {
                '1': {'speed': '7.0'} # Missing 'radius'
            }
        }
        # Function should handle KeyError gracefully and return original data for that orbit
        expected_output = {
            'orbits': {
                '1': {'speed': '7.0'}
            }
        }
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        self.assertEqual(normalized_data, expected_output)

    def test_orbit_invalid_radius_value(self):
        """Test an orbit with a non-numeric radius."""
        input_data = {
            'orbits': {
                '1': {'radius': 'not_a_number', 'speed': '7.0'}
            }
        }
        # Function should handle ValueError gracefully and return original data for that orbit
        expected_output = {
            'orbits': {
                '1': {'radius': 'not_a_number', 'speed': '7.0'}
            }
        }
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        self.assertEqual(normalized_data, expected_output)

    def test_satellite_missing_orbitid(self):
        """Test a satellite missing the 'orbitId' key."""
        input_data = {
            'orbits': {'1': {'radius': '10000', 'speed': '8.0'}},
            'satellites': {'sat1': {'angle': '90'}} # Missing 'orbitId'
        }
        expected_output = {
            'orbits': {'1': {'radius': '10000.0', 'speed': '8.0'}},
            'satellites': {'sat1': {'angle': '90'}}
        }
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        self.assertEqual(normalized_data, expected_output)

    def test_satellite_with_nonexistent_orbitid(self):
        """Test a satellite referencing an orbitId that doesn't exist."""
        input_data = {
            'orbits': {'1': {'radius': '10000', 'speed': '8.0'}},
            'satellites': {'sat1': {'angle': '90', 'orbitId': 'non_existent_orbit'}}
        }
        expected_output = {
             'orbits': {'1': {'radius': '10000.0', 'speed': '8.0'}},
            'satellites': {'sat1': {'angle': '90', 'orbitId': 'non_existent_orbit'}}
        }
        normalized_data = normalize_form_data(copy.deepcopy(input_data))
        self.assertEqual(normalized_data, expected_output) # Satellite should remain unchanged

if __name__ == '__main__':
    unittest.main() 