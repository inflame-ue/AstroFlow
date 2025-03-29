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
        if value['radius'] > 17000:
            normalized_radius = 17000 + (radius - 17000) * (17000 / 42000)
            value['radius'] = normalized_radius
        else:
            pass
    
    return form_data