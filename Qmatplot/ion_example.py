from matplotlib import pyplot as plt
import numpy as np


# create plot
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

# plot setting
axes = plt.gca()
xmin, xmax = 0, 10
ymin, ymax = -1, 1
axes.set_xlim([xmin, xmax])
axes.set_ylim([ymin, ymax])

# data showed in matplotlib
# x = np.linspace(0, 2 * np.pi, num=50)
# y = np.sin(x)
x = np.linspace(0, xmax, num=100)
y = np.zeros_like(x)

# draw point on plot
ax.plot(x, y)

# start interaction mode
# """
plt.ion()

num_of_sin_wave = 10
for i in range(0, int(np.ceil(np.pi*num_of_sin_wave)), 1):
    x = np.linspace(i, i + np.pi*num_of_sin_wave, num=100)
    y = np.sin(x)
    try:
        ax.lines.remove(lines[0])
    except Exception as e:
        print(e)
        pass
    lines = ax.plot(x - i, y)
    plt.pause(0.1)

# close interaction mode
plt.ioff()
# """

# stop for a while
# plt.pause(2)

# close plot
plt.close()
