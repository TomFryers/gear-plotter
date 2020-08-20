# Bike Gear Plotter

Generates a chart comparing the gears of several bikes.

To use it, run `python gear_plotter.py file_name.txt`. `file_name.txt`
should contain data about the bikes in the following format:

```
# Bike Name
front: 32,
rear: 34, 30, 26, 23, 20, 17, 15, 13, 11
full_diameter: 700 mm
crank: 175 mm
# Bike Name 2
front: 50, 34
rear: 34, 30, 26, 23, 20, 17, 15, 13, 11
full_diameter: 700 mm
crank: 175 mm
```

The order of fields within a bike is unimportant.

The following length units are supported:

- km
- m
- dm
- cm
- mm
- ft
- in

In order to determine the wheel size, one of the following should be
given:

- `full_diameter`
- `full_circumference`
- `full_radius`

or `tyre_thickness` should be given, along with either `wheel_radius` or
`wheel_diameter`.
