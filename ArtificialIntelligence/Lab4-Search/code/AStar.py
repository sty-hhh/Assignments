import time
import queue

# 读取迷宫
def read_file(filename):
	maze = []
	s, e = (0,0), (0,0)
	with open(filename, 'r') as file:
		for (i, line) in enumerate(file):
			if line[-1] not in ['1', '0', 'S', 'E']:
				line = line[:-1]
			j = line.find('S')
			if j != -1:
				s = (i,j)
			j = line.find('E')
			if j != -1:
				e = (i,j)
			row = ""
			for x in line:
				if x == '0':
					row += ' '
				elif x == '1':
					row += '.'
				else:
					row += x
			maze.append(row)		
	return maze, s, e

# 测试(x, y)位置是否可走
def validQ(x,y):
	if x < 0 or x >= len(maze) or y < 0 or y >= len(maze[0]) or maze[x][y] == '.':
		return False
	else:
		return True

# Lp距离，p=1为曼哈顿距离
def h(pos, e, p=1):
	return ((abs(pos[0] - e[0]))**p + (abs(pos[0] - e[0]))**p)**(1/p)

# A*搜索
def AStar(maze, s, e):
	best = ""
	shortestLength = 0
	x, y = s[0], s[1]
	complex = 1	# 复杂度
	# 初始化
	q = queue.PriorityQueue()
	q.put((0,(x,y)))
	prev = {}
	prevCost = {}
	prev[s] = None
	prevCost[s] = 0
	# 寻找终点
	while not q.empty():
		complex += 1
		_, (x, y) = q.get()	# 取出优先队列队首元素
		if (x, y) == e:
			break
		# 遍历4邻域节点
		for pos in [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]:
			g = prevCost[(x,y)] + 1
			# 如果节课可走，并且节点未遍历或节点有更短的走法
			if validQ(pos[0], pos[1])and ((pos not in prev) or g < prevCost[pos]):
				prevCost[pos] = g
				f = g + h(pos, e, 1)
				q.put((f, pos))	# 入队
				prev[pos] = (x, y)
	# 回到起点生成最短路径
	p = e
	while prev[p] != None:
		shortestLength += 1
		x, y = p[0], p[1]
		maze[x] = maze[x][:y] + '#' + maze[x][y+1:]
		p = prev[p]
    # 将路径写入字符串best
	maze[e[0]] = maze[e[0]][:e[1]] + 'E' + maze[e[0]][e[1]+1:]
	maze[s[0]] = maze[s[0]][:s[1]] + 'S' + maze[s[0]][s[1]+1:]
	for i in range(len(maze)):
		best += maze[i] + "\n"
    # 返回路径图、最短距离、复杂度
	return best, shortestLength, complex
	
if __name__ == "__main__": 
	maze, s, e = read_file("MazeData.txt")
	start = time.time()
	best, shortestLength, complex = AStar(maze, s, e)
	end = time.time()
	print("A* Search Shortest length: ", shortestLength)
	print("Running time: {:.4f}s".format(end-start))
	print("Time complexity is ", complex)
	print("Space complexity is :", complex)
	print(best)	

