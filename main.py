import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Constants
R_p = 1.0  # Planet radius
GM = 1.0   # Gravitational parameter
pads = [0, np.pi/2, np.pi, 3*np.pi/2]  # Pad angles
orbits = [1.5, 2.0]  # Orbit radii
satellites = [
    {'r_s': 1.5, 'phi_s': 0.0, 'omega_s': np.sqrt(GM / 1.5**3)},
    {'r_s': 2.0, 'phi_s': np.pi/4, 'omega_s': np.sqrt(GM / 2.0**3)}
]

def hohmann_transfer_params(r1, r2, GM):
    a = (r1 + r2) / 2
    t_transfer = np.pi * np.sqrt(a**3 / GM)
    v1 = np.sqrt(GM / r1)
    v_trans1 = np.sqrt(GM * (2/r1 - 1/a))
    v2 = np.sqrt(GM / r2)
    v_trans2 = np.sqrt(GM * (2/r2 - 1/a))
    dv = (v_trans1 - v1) + (v2 - v_trans2) if r1 < r2 else (v1 - v_trans1) + (v_trans2 - v2)
    return dv, t_transfer

def approximate_launch_time(R_p, r_t, GM):
    dv, t = hohmann_transfer_params(R_p, r_t, GM)
    return t  # Simplified

def approximate_deorbit_time(r_t, R_p, GM):
    dv, t = hohmann_transfer_params(r_t, R_p, GM)
    return t

def find_earliest_departure(t_arrive, theta_start, omega_t, r_s, phi_s, omega_s, t_transfer):
    t_dep = t_arrive
    step = 0.01
    max_attempts = 1000
    for _ in range(max_attempts):
        theta_dep = theta_start + omega_t * (t_dep - t_arrive)
        theta_sat = phi_s + omega_s * (t_dep + t_transfer)
        # Simplified rendezvous: check if angles are close after transfer
        if abs((theta_dep + np.pi) % (2*np.pi) - theta_sat % (2*np.pi)) < 0.1:
            return t_dep
        t_dep += step
    return t_dep  # Fallback

def optimize_launch_time(theta_pad, r_t, R_p, GM, satellites):
    t_launch = approximate_launch_time(R_p, r_t, GM)
    t0_range = np.linspace(0, 10, 100)  # Grid search
    min_time = float('inf')
    best_t0 = 0
    best_trajectory = []

    for t0 in t0_range:
        t_arrive = t0 + t_launch
        omega_t = np.sqrt(GM / r_t**3)
        return_times = []
        trajectory = []
        theta_tanker = theta_pad

        for sat in satellites:
            r_s = sat['r_s']
            phi_s = sat['phi_s']
            omega_s = sat['omega_s']
            dv, t_transfer = hohmann_transfer_params(r_t, r_s, GM)
            t_dep = find_earliest_departure(t_arrive, theta_tanker, omega_t, r_s, phi_s, omega_s, t_transfer)
            t_return = t_dep + 2 * t_transfer
            return_times.append(t_return)
            trajectory.append({'t_dep': t_dep, 'r_from': r_t, 'r_to': r_s, 't_transfer': t_transfer})

        mission_end = max(return_times)
        t_deorbit = approximate_deorbit_time(r_t, R_p, GM)
        total_time = mission_end + t_deorbit - t0
        if total_time < min_time:
            min_time = total_time
            best_t0 = t0
            best_trajectory = trajectory

    return best_t0, min_time, best_trajectory

def calculate_best_launch_pad(R_p, GM, pads, orbits, satellites):
    r_t = satellites[0]['r_s']  # Example choice
    best_pad = None
    best_t0 = None
    min_mission_time = float('inf')
    best_trajectory = None

    for theta_pad in pads:
        t0, mission_time, trajectory = optimize_launch_time(theta_pad, r_t, R_p, GM, satellites)
        if mission_time < min_mission_time:
            min_mission_time = mission_time
            best_pad = theta_pad
            best_t0 = t0
            best_trajectory = trajectory

    return best_pad, best_t0, min_mission_time, best_trajectory

# Run algorithm
best_pad, best_t0, mission_time, trajectory = calculate_best_launch_pad(R_p, GM, pads, orbits, satellites)
print(f"Best pad: {best_pad:.2f} rad, Launch time: {best_t0:.2f}, Mission time: {mission_time:.2f}")

# Visualization
fig, ax = plt.subplots()
ax.set_aspect('equal')
plt.title("Refueling Mission Trajectory")

# Draw planet and orbits
planet = plt.Circle((0, 0), R_p, color='blue', alpha=0.5)
ax.add_patch(planet)
for r in orbits:
    orbit = plt.Circle((0, 0), r, color='gray', fill=False)
    ax.add_patch(orbit)

# Initial positions
sat_scatter = ax.scatter([], [], c='white', label='Satellites')
tanker_scatter = ax.scatter([], [], c='red', label='Tanker')
shuttle_scatter = ax.scatter([], [], c='green', label='Shuttles')
plt.legend()

def init():
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    return sat_scatter, tanker_scatter, shuttle_scatter

def update(frame):
    t = frame * 0.1
    sat_x, sat_y = [], []
    for sat in satellites:
        angle = sat['phi_s'] + sat['omega_s'] * (t + best_t0)
        sat_x.append(sat['r_s'] * np.cos(angle))
        sat_y.append(sat['r_s'] * np.sin(angle))
    sat_scatter.set_offsets(np.c_[sat_x, sat_y])

    # Tanker position
    r_t = satellites[0]['r_s']
    t_launch = approximate_launch_time(R_p, r_t, GM)
    t_deorbit = approximate_deorbit_time(r_t, R_p, GM)
    mission_end = max([tr['t_dep'] + 2 * tr['t_transfer'] for tr in trajectory]) + best_t0
    if t < t_launch:
        r = R_p + (r_t - R_p) * (t / t_launch)
        tanker_x = r * np.cos(best_pad)
        tanker_y = r * np.sin(best_pad)
    elif t < mission_end - best_t0:
        omega_t = np.sqrt(GM / r_t**3)
        angle = best_pad + omega_t * (t - t_launch)
        tanker_x = r_t * np.cos(angle)
        tanker_y = r_t * np.sin(angle)
    else:
        frac = (t - (mission_end - best_t0)) / t_deorbit
        r = r_t - (r_t - R_p) * min(frac, 1)
        tanker_x = r * np.cos(best_pad)
        tanker_y = r * np.sin(best_pad)
    tanker_scatter.set_offsets(np.array([[tanker_x, tanker_y]]))

    # Shuttle positions
    shuttle_x, shuttle_y = [], []
    for tr in trajectory:
        t_dep = tr['t_dep'] - best_t0
        t_transfer = tr['t_transfer']
        r_from, r_to = tr['r_from'], tr['r_to']
        omega_t = np.sqrt(GM / r_t**3)
        theta_dep = best_pad + omega_t * (t_dep)
        if t_dep <= t < t_dep + t_transfer:
            frac = (t - t_dep) / t_transfer
            r = r_from + (r_to - r_from) * frac  # Simplified path
            angle = theta_dep + np.pi * frac
            shuttle_x.append(r * np.cos(angle))
            shuttle_y.append(r * np.sin(angle))
        elif t_dep + t_transfer <= t < t_dep + 2 * t_transfer:
            frac = (t - (t_dep + t_transfer)) / t_transfer
            r = r_to - (r_to - r_from) * frac
            angle = (theta_dep + np.pi) - np.pi * frac
            shuttle_x.append(r * np.cos(angle))
            shuttle_y.append(r * np.sin(angle))
    shuttle_scatter.set_offsets(np.c_[shuttle_x, shuttle_y] if shuttle_x else np.array([[]]))

    return sat_scatter, tanker_scatter, shuttle_scatter

ani = FuncAnimation(fig, update, frames=np.arange(0, 50, 1), init_func=init, blit=True)
plt.show()