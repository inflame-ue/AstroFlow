def normalize_form_data(form_data: dict) -> dict:
    """
    The simulation enforces speficic scaling of the radius for it to display correctly.
    This function takes form data on input and normalizes the radius to the simulation's requirements.
    Based on the following formula: normalized_radius = 17000 + (radius - 17000) * (17000 / 42000)

    Args:
        form_data: dict
    Returns:
        dict

    """
    for key, value in form_data['orbits'].items():
        try:    
            if value['radius'] > 17000:
                if value['radius'] > 42000:
                    value['radius'] = 42000 # scale down to max radius
                normalized_radius = 17000 + (value['radius'] - 17000) * (17000 / 42000)
                value['radius'] = normalized_radius
        except KeyError as e:
            print(f"Error while accessing radius: {e}")

    return form_data