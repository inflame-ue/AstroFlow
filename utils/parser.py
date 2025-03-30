def normalize_form_data(form_data: dict) -> dict:
    """
    The simulation enforces specific scaling of the radius for it to display correctly.
    This function takes form data on input and normalizes the radius to the simulation's requirements.
    Based on the following formula: normalized_radius = 17000 + (radius - 17000) * (17000 / 42000)

    Args:
        form_data: dict
    Returns:
        dict

    """
    if not form_data or not isinstance(form_data, dict) or 'orbits' not in form_data:
        return form_data
        
    for key, value in form_data['orbits'].items():
        try:
            radius = float(value['radius'])
            if radius > 17000:
                if radius > 42000 or radius < 0:
                    radius = 42000  # scale down to max radius
                # Using an even smaller scaling factor to downscale more aggressively
                normalized_radius = 17000 + (radius - 17000) * (5000 / 42000)
                value['radius'] = str(normalized_radius)  # Convert back to string to match expected type
            else:
                if radius < 8000:
                    # Upscale very small orbits to ensure visibility
                    radius = 8000  # Set minimum radius to 8000 km
                value['radius'] = str(radius)
        except KeyError as e:
            print(f"Error while accessing radius: {e}")
        except ValueError as e:
            print(f"Error while converting radius to float: {e}")
    
    # Also need to update satellite radius values that reference these orbits
    if 'satellites' in form_data:
        for satellite in form_data['satellites'].values():
            try:
                orbit_id = satellite['orbitId']
                if orbit_id in form_data['orbits']:
                    satellite['radius'] = form_data['orbits'][orbit_id]['radius']
            except KeyError as e:
                print(f"Error while updating satellite radius: {e}")
                
    return form_data