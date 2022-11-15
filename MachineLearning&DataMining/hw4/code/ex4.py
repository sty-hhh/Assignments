import math
import numpy as np

points = [[5.9, 3.2], [4.6, 2.9], [6.2, 2.8], [4.7, 3.2], [5.5, 4.2],
         [5.0, 3.0], [4.9, 3.1], [6.7, 3.1], [5.1, 3.8], [6.0, 3.0]]
red = [[6.2, 3.2]]
green = [[6.6, 3.7]]
blue = [[6.5, 3.0]]

def dist(point, center):
    return math.sqrt(math.pow(point[0]-center[0], 2)+math.pow(point[1]-center[1], 2))

def cluster():
    red_dist = [dist(point, red[0]) for point in points]
    green_dist = [dist(point, green[0]) for point in points]
    blue_dist = [dist(point, blue[0]) for point in points]
    for i, point in enumerate(points):
        if (red_dist[i] < blue_dist[i] and red_dist[i] < green_dist[i]):
            red.append(point)
        elif (green_dist[i] < blue_dist[i] and green_dist[i] < red_dist[i]):
            green.append(point)
        else:
            blue.append(point)
    red[0][0] = np.sum([k[0] for k in red[1:]])/len(red[1:])
    red[0][1] = np.sum([k[1] for k in red[1:]])/len(red[1:])
    green[0][0] = np.sum([k[0] for k in green[1:]])/len(green[1:])
    green[0][1] = np.sum([k[1] for k in green[1:]])/len(green[1:])
    blue[0][0] = np.sum([k[0] for k in blue[1:]])/len(blue[1:])
    blue[0][1] = np.sum([k[1] for k in blue[1:]])/len(blue[1:])
    print('red: ',red[1:])
    print('blue: ',blue[1:])
    print('green: ',green[1:])
    print('red center: ', red[0])
    print('blue center: ', blue[0])
    print('green center: ', green[0])
    del red[1:]
    del blue[1:]
    del green[1:]

print('初始值')
print('red center: ', red[0])
print('blue center: ', blue[0])
print('green center: ', green[0])
for i in range(3):
    print('迭代次数', i+1)
    cluster()