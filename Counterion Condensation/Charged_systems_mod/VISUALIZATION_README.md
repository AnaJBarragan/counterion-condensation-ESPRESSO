# Aggregate Visualization Guide

This guide explains how to visualize the aggregate structure created from sphere data.

## Two Approaches

### 1. Notebook Approach (Cell 8)

Run cell 8 in the `charged_system.ipynb` notebook. This will:
- Create a visualization system
- Build the aggregate
- Open an interactive visualization window

**Note:** This requires the notebook kernel to have display access.

### 2. Standalone Script Approach (Recommended for VNC)

Use the `visualization_aggregate.py` script with pypresso.

#### Setup (in terminal from Charged_systems_mod directory):

```bash
# Set up virtual display (if not already running)
Xvfb :99 -screen 0 1280x800x24 &
export DISPLAY=:99

# Start VNC server (if not already running)
x11vnc -display :99 -nopw -forever &

# Run the visualization
~/espresso-src/build/pypresso visualization_aggregate.py
```

## Visualization Controls

Once the visualization window opens:

- **Mouse drag**: Rotate the view
- **Mouse wheel**: Zoom in/out
- **Arrow keys**: Move camera position
- **'q' key**: Quit the visualization

## Customization

### In the notebook (Cell 8):

You can customize:
- `box_size`: Size of the simulation box
- `particle_colors`: Change particle colors (RGB values 0-1)
- `background_color`: Change background color
- `camera_position`: Initial camera position
- Thermostat settings: Comment out to freeze the aggregate

### In visualization_aggregate.py:

Same customization options are available around lines 120-130.

## Troubleshooting

### "No display" error
Make sure you've set up Xvfb and exported DISPLAY=:99

### "Module not found" error when running notebook
The visualization requires espressomd.visualization which should be available in your kernel.

### Aggregate appears static
This is normal if the thermostat is disabled. Uncomment the thermostat line to allow movement.

### Particles overlap or look wrong
Check that the sphere data is loaded correctly and the `scale` parameter is appropriate.

## Features

- The aggregate is created as a **rigid body** using virtual sites
- All spheres are connected to a central particle
- The rigid body can rotate and translate as a single unit
- Individual spheres maintain their relative positions

## Performance Tips

- Reduce the number of spheres (change `iloc[:100]` to a smaller number) for faster visualization
- Increase `time_step` if simulation runs too slowly
- Adjust `gamma` parameter in thermostat for different motion speeds
