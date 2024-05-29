import random
import wdapy

c = wdapy.AppiumUSBClient()
w, h = c.window_size()
# print(w, h)
x = w//10 * random.randint(1, 9)
print(x)
sy = h//10*7
ey = h//10*2

steps = 10
step_size = (ey - sy) // steps
ys = list(range(sy+step_size, ey, step_size)) + [ey]

gestures = []
gestures.append(wdapy.Gesture("press", options={"x": x, "y": sy}))
for y in ys:
    gestures.append(wdapy.Gesture("wait", options={"ms": 100}))
    gestures.append(wdapy.Gesture("moveTo", options={"x": x, "y": y}))
gestures.append(wdapy.Gesture("wait", options={"ms": 100}))
gestures.append(wdapy.Gesture("release"))


for g in gestures:
    print(g.action, g.options)

# c.debug = True
c.appium_settings({"snapshotMaxDepth": 3})
c.touch_perform(gestures)