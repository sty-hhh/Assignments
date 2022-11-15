import time

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

# 判断下一步(x,y)返回起点的路径的方向，加入队列q
def explore(x, y, d, visited, q):
	if validQ(x,y) and visited[x][y] == 0:
		visited[x][y] = d
		q.append((x,y))

# 一致代价搜索，其实是BFS
def UCS(maze, s, e):
	best = ""
	shortestLength = 0
	x, y = s[0], s[1]
	complex = 1	# 复杂度
	# 初始化
	q = [(x,y)]
	visited = [[0] * (len(maze[0])) for _ in range(len(maze))]
	visited[x][y] = -1
	# 遍历上下左右，visited[x][y]保存该点向起点移动路径的方向
	while len(q) > 0:
		(x,y), q = q[0], q[1:]
		if (x,y) == e:
			break
		complex += 1
		explore(x-1, y, 'D', visited, q)
		explore(x+1, y, 'U', visited, q)
		explore(x, y-1, 'R', visited, q)
		explore(x, y+1, 'L', visited, q)
	# 回到起点生成最短路径
	(x, y) = e
	while (x, y) != s:
		shortestLength += 1
		if visited[x][y] == 'D':
			x = x + 1
		elif visited[x][y] == 'U':
			x = x - 1
		elif visited[x][y] == 'L':
			y = y - 1
		elif visited[x][y] == 'R':
			y = y + 1
		maze[x] = maze[x][:y] + 'X' + maze[x][y+1:]
	# 将路径写入字符串best
	maze[s[0]] = maze[s[0]][:s[1]] + 'S' + maze[s[0]][s[1]+1:]
	for i in range(len(maze)):
		best += maze[i] + "\n"
	# 返回路径图、最短距离、复杂度
	return best, shortestLength, complex
	
if __name__ == "__main__": 
	maze, s, e = read_file("MazeData.txt")
	start = time.time()
	best, shortestLength, complex = UCS(maze, s, e)
	end = time.time()
	print("UCS Shortest length: ", shortestLength)
	print("Running time: {:.4f}s".format(end-start))
	print("Time complexity is ", complex)
	print("Space complexity is :", complex)
	print(best)	