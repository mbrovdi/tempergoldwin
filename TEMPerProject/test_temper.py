import tempergoldwin

temp = tempergoldwin.read_temperature()
if temp is not None:
    print(f"Temperature: {temp:.2f} °C")


import tempergoldwin

# Read temperature continuously every 2 seconds
tempergoldwin.read_temperature_loop(interval=2)

