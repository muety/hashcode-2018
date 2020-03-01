import sys
import math
import numpy as np
from multiprocessing.pool import ThreadPool
import multiprocessing
from tqdm import tqdm

def print_pizza(pizza):
    for l in pizza: print(l)
    print('\n')

def read_pizza():
    pizza = []
    with open(sys.argv[1] if len(sys.argv) > 1 else 'data/small.in', 'r') as f:
        for i, l in enumerate(f):
            if i == 0: height, width, min_ingredients, max_slice = l.split(' ')
            else:
                pizza.append(list(l)[:-1])
    return pizza, int(height), int(width), int(min_ingredients), int(max_slice)

def dump_slices(slices):
    with open(sys.argv[2] if len(sys.argv) > 2 else 'out.txt', 'w') as f:
        f.write('{}\n'.format(len(slices)))
        for s in slices:
            f.write('{} {} {} {}\n'.format(s[0][0], s[0][1], s[1][0], s[1][1]))

def preprocess(pizza, point, maxsize, min_ingredients):
    x, y = point
    if pizza[y][x] == 'X': return -1, [None for i in range(4)]
    required_const = ['T' for i in range(min_ingredients)] + ['M' for i in range(min_ingredients)]
    required_const.remove(pizza[y][x])
    scores = []
    height, width = len(pizza), len(pizza[0])

    dx, dy = x, y
    required = required_const[:]
    while dy > 0:
        dy -= 1
        score = abs(dy - y) + 1
        if score > maxsize or pizza[dy][x] == 'X':
            scores.append(max(width, height))
            break
        
        if pizza[dy][x] in required: required.remove(pizza[dy][x])
        if len(required) == 0 and dy != y:
            scores.append(score)
            break
    if dy <= 0 and len(scores) < 1: scores.append(sys.maxsize)

    dx, dy = x, y
    required = required_const[:]
    while dy < height - 1:
        dy += 1
        score = abs(dy - y) + 1
        if score > maxsize or pizza[dy][x] == 'X':
            scores.append(max(width, height))
            break
        if pizza[dy][x] in required: required.remove(pizza[dy][x])
        if len(required) == 0 and dy != y:
            scores.append(score)
            break
    if dy >= height - 1 and len(scores) < 2: scores.append(sys.maxsize)

    dx, dy = x, y
    required = required_const[:]
    while dx > 0:
        dx -= 1
        score = abs(dx - x) + 1
        if score > maxsize or pizza[y][dx] == 'X':
            scores.append(max(width, height))
            break
        if pizza[y][dx] in required: required.remove(pizza[y][dx])
        if len(required) == 0 and dx != x:
            scores.append(score)
            break
    if dx <= 0 and len(scores) < 3: scores.append(sys.maxsize)

    dx, dy = x, y
    required = required_const[:]
    while dx < width - 1:
        dx += 1
        score = abs(dx - x) + 1
        if score > maxsize or pizza[y][dx] == 'X':
            scores.append(max(width, height))
            break
        if pizza[y][dx] in required: required.remove(pizza[y][dx])
        if len(required) == 0 and dx != x:
            scores.append(score)
            break
    if dx >= width - 1 and len(scores) < 4: scores.append(sys.maxsize)

    directions = list(map(lambda i: ['up', 'down', 'left', 'right'][i] if (scores[i] <= maxsize and scores[i] > 1) else None, np.array(scores).argsort()))
    if min(scores) >= sys.maxsize:
        final_score = None
    elif min(scores) > maxsize:
        final_score = -1
    else:
        final_score = min(scores)
    return final_score, directions

# Attention: In-place replacements
# point is (x, y), meaning (horizontal, vertical)
def walk_and_slice(pizza, point, direction, min_ingredients):
    # Assumes that preprocess() has already filtered out invalid walk directions    
    height, width = len(pizza), len(pizza[0])
    y, x = point
    dx, dy = x, y
    if direction == 'None' or pizza[y][x] == 'X': return None
    required = ['T' for i in range(min_ingredients)] + ['M' for i in range(min_ingredients)]
    required.remove(pizza[y][x])
    pizza[y][x] = 'X'
    if direction == 'up':
        while dy >= 0:
            dy -= 1
            ingredient = pizza[dy][x]
            pizza[dy][x] = 'X'
            if ingredient in required:
                required.remove(ingredient)
                if len(required) == 0: break
    elif direction == 'down':
        while dy < height - 1:
            dy += 1
            ingredient = pizza[dy][x]
            pizza[dy][x] = 'X'
            if ingredient in required:
                required.remove(ingredient)
                if len(required) == 0: break
    elif direction == 'left':
        while dx >= 0:
            dx -= 1
            ingredient = pizza[y][dx]
            pizza[y][dx] = 'X'
            if ingredient in required:
                required.remove(ingredient)
                if len(required) == 0: break
    elif direction == 'right':
        while dx < width - 1:
            dx += 1
            ingredient = pizza[y][dx]
            pizza[y][dx] = 'X'
            if ingredient in required:
                required.remove(ingredient)
                if len(required) == 0: break
    return (y, x), (dy, dx)

def can_cut(difficulty_matrix):
    return difficulty_matrix.max() > -1

def get_difficulty_and_directions(args):
    pizza, max_size, min_ingredients, boundaries = args
    height, width = len(pizza), len(pizza[0])
    difficulties = np.zeros((height, width))
    directions = np.chararray((height, width, 4), unicode=True, itemsize=5)
    for y in range(boundaries[0], boundaries[1]):
        for x in range(width):
            difficulties[y][x], directions[y][x] = preprocess(pizza, (x, y), max_slice, min_ingredients)
            difficulties[difficulties > max_slice] = -1
    return difficulties, directions

if __name__ == '__main__':
    pizza, height, width, min_ingredients, max_slice = read_pizza()
    points_done = {}
    slices = []
    difficulties = np.zeros((height, width))
    directions = np.chararray((height, width, 4), unicode=True, itemsize=5)
    pbar = tqdm(total=height * width)
    n_threads = int(sys.argv[3]) if len(sys.argv) > 3 else min(multiprocessing.cpu_count(), max_slice * 2)
    if n_threads > 1: pool = ThreadPool(n_threads)
    next_point = (0,0)

    c = 0
    while can_cut(difficulties):
        c += 1

        if c == 1: idx_from, idx_to = 0, height
        else: idx_from, idx_to = max(0, next_point[0] - max_slice - 1), min(height, next_point[0] + max_slice + 1)

        if n_threads > 1:
            n = math.ceil(abs(idx_from - idx_to) / n_threads)
            subdata = []
            for i in range(0, abs(idx_from - idx_to), n):
                subdata.append((pizza[:], max_slice, min_ingredients, (idx_from + i, min(height, idx_from + i + n))))
            results = pool.map(get_difficulty_and_directions, subdata)
            for i, result in enumerate(results):
                difficulties[subdata[i][3][0]:subdata[i][3][1]] = result[0][subdata[i][3][0]:subdata[i][3][1]]
                directions[subdata[i][3][0]:subdata[i][3][1]] = result[1][subdata[i][3][0]:subdata[i][3][1]]
        else:
            result = get_difficulty_and_directions((pizza[:], max_slice, min_ingredients, (idx_from, idx_to)))
            difficulties[idx_from:idx_to] = result[0][idx_from:idx_to]
            directions[idx_from:idx_to] = result[1][idx_from:idx_to]

        pbar.update(height * width - len(difficulties[difficulties > -1]) - pbar.n)

        next_point_valid = False
        while not next_point_valid and difficulties.max() > -1:
            next_point = np.unravel_index(difficulties.argmax(), (height, width))
            if next_point in points_done: difficulties[next_point] = -1
            else: next_point_valid = True
        points_done[next_point] = True

        slc = walk_and_slice(pizza, next_point, directions[next_point][0], min_ingredients)
        if slc is not None: slices.append(slc)
    
    dump_slices(slices)
    pbar.close()