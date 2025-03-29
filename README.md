# Satellite Refueling Mission Optimizer

This program simulates and optimizes the launch of a tanker spacecraft to refuel satellites in different orbits. It determines the best launch pad location to minimize mission time while ensuring fuel efficiency.

## Problem Description

The simulation takes place in a 2D plane with the following components:

- **Planet**: A circular body with a specified radius
- **Launch Pads**: Points distributed around the planet's surface
- **Orbits**: Concentric circles with different radii around the planet
- **Satellites**: Objects moving in circular orbits at specified speeds
- **Tanker**: A spacecraft that launches from a pad to a transfer orbit, deploys refueling shuttles, and returns
- **Shuttles**: Small vehicles that travel from the tanker to satellites for refueling operations

The mission profile is as follows:
1. A tanker launches from a pad on the planet's surface to a transfer orbit
2. From the transfer orbit, it deploys shuttles to each satellite
3. Each shuttle travels to its satellite using a Hohmann transfer, refuels it, and returns
4. After all shuttles return, the tanker deorbits back to the planet

## Algorithm

The algorithm:
1. Models the orbital mechanics using Kepler's laws and Hohmann transfers for orbit changes
2. For each potential launch pad, calculates the optimal launch time to minimize mission duration
3. Selects the pad that results in the shortest overall mission time
4. Visualizes the mission with an animated simulation

## Usage

Run the script with the following command:

```
python new_main.py
```

This will:
1. Find the optimal launch pad
2. Calculate the mission profile
3. Display an animated visualization of the entire mission

To save the animation to a file instead of displaying it, use:

```
python new_main.py --save
```

This will create a file called `mission_animation.mp4` in the current directory.

## Customization

You can modify the test scenario in the `test_algorithm()` function to:
- Change the planet's size and gravitational parameter
- Adjust the number and positions of launch pads
- Modify the orbit radii
- Change the number, orbits, and initial positions of satellites
- Adjust the transfer orbit radius

## Dependencies

- NumPy
- Matplotlib
- FFmpeg (required for saving animations) 