# Bike Gear Plotter

Generates a chart comparing the gears of several bikes.

The format is as follows

```
# Bike Name
front: 32,
rear: 34, 30, 26, 23, 20, 17, 15, 13, 11
full_diameter: 700 mm
crank: 175 mm
```

The following length units are supported:

- km
- m
- dm
- cm
- mm
- ft
- in

In order to determine the wheel size, one of the following should be given:

- wheel_radius
- wheel_diameter
- tyre_thickness
- full_diameter
- full_circumference
- full_radius
