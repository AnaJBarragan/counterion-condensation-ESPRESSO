# Run VNC Visualization

```bash
Xvfb :99 -screen 0 1280x800x24 &
export DISPLAY=:99

# Start VNC server sharing that display
x11vnc -display :99 -nopw -forever &

#Python ≠ Pypresso
~/espresso-src/build/pypresso visualization_bonded.py 
```