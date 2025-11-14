#
# Copyright (C) 2010-2022 The ESPResSo project
#
# This file is part of ESPResSo.
#
# ESPResSo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ESPResSo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Visualize the aggregate created from sphere data.
"""

import espressomd
import espressomd.visualization
import espressomd.rotation
import numpy as np
import fracval2py

# Check for required features
required_features = ["VIRTUAL_SITES_RELATIVE", "MASS", "ROTATIONAL_INERTIA"]
espressomd.assert_features(required_features)

# Parameters
box_size = 100
part_real = 0  # Particle type for aggregate particles
scale = (1/80)*1e+09
path = "LD_1600_1.dat"

# Load sphere data
print("Loading sphere data...")
Spheres = fracval2py.Read_spheres(path, scale, normalized=True)
Spheres = Spheres.iloc[:100].copy()
print(f"Loaded {len(Spheres)} spheres")

# Create system
system = espressomd.System(box_l=3 * [box_size])
system.time_step = 0.01
system.cell_system.skin = 0.4
np.random.seed(42)

def build_aggregate(system, spheres, fact=1):
    """Build the aggregate structure from sphere data."""
    ids_added = []
    N = len(spheres)

    # Calculate and correct CM
    x_cm = np.sum(spheres.x.values * spheres.v.values) / np.sum(spheres.v.values)
    y_cm = np.sum(spheres.y.values * spheres.v.values) / np.sum(spheres.v.values)
    z_cm = np.sum(spheres.z.values * spheres.v.values) / np.sum(spheres.v.values)
    spheres["x"] = spheres["x"] - x_cm
    spheres["y"] = spheres["y"] - y_cm
    spheres["z"] = spheres["z"] - z_cm

    # Add all spheres as real particles and store their IDs
    print("Adding particles...")
    for i in range(N):
        pos = [spheres["x"].iloc[i] * fact + box_size * 0.5,
               spheres["y"].iloc[i] * fact + box_size * 0.5,
               spheres["z"].iloc[i] * fact + box_size * 0.5]
        pid = len(system.part)
        ids_added.append(pid)
        system.part.add(id=pid, pos=pos, type=part_real, 
                       mass=spheres["v"].iloc[i], 
                       rotation=(True, True, True), 
                       fix=(False, False, False))

    # Rigid Body setup
    print("Setting up rigid body...")
    # Get positions and masses of all added particles
    positions = np.array([system.part.by_id(pid).pos for pid in ids_added])
    masses = np.array([system.part.by_id(pid).mass for pid in ids_added])

    # Calculate principal moments and axes of inertia
    principal_moments, principal_axes = espressomd.rotation.diagonalized_inertia_tensor(
        positions, masses)

    # Add central particle at center of mass (already at box center)
    p_center = system.part.add(
        pos=[box_size * 0.5, box_size * 0.5, box_size * 0.5],
        mass=np.sum(masses),
        rinertia=principal_moments,
        rotation=[True, True, True],
        type=part_real,
        quat=espressomd.rotation.matrix_to_quat(principal_axes)
    )

    # Relate all spheres as virtual sites to the central particle
    print("Creating virtual sites...")
    for pid in ids_added:
        system.part.by_id(pid).vs_auto_relate_to(p_center.id)
    
    print(f"Aggregate built with {len(ids_added)} particles and 1 central particle")
    return p_center, ids_added

# Build the aggregate
center_particle, particle_ids = build_aggregate(system, Spheres, fact=1)

# Set up visualization
print("Setting up visualizer...")

# Calculate average particle radius for visualization
if 'r' in Spheres.columns:
    avg_radius = np.mean(Spheres['r'].values)
else:
    avg_radius = 1.0

visualizer = espressomd.visualization.openGLLive(
    system,
    particle_sizes= 'auto', #####SUSPECTED PROBLEM
    background_color=[1, 1, 1],  # White background
    camera_position=[box_size*1.5, box_size*1.5, box_size*1.5],
    camera_target=[box_size*0.5, box_size*0.5, box_size*0.5],
    particle_type_colors={part_real: [0.2, 0.5, 0.8]},  # Blue particles
    window_size=[1024, 768]
)

# Set up integrator
system.integrator.set_vv()

# Set up thermostat to allow the rigid body to rotate and move
system.thermostat.set_langevin(kT=1.0, gamma=1.0, seed=42)

# Run visualization
print("Starting visualization...")
print("Controls:")
print("  - Mouse drag: rotate view")
print("  - Mouse wheel: zoom")
print("  - Press 'q': quit")
print("  - Arrow keys: move camera")

visualizer.run(1)

print("Visualization closed.")
