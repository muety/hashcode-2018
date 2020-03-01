import sys
import numpy as np

class Car():
    def __init__(self, id):
        self.id = id
        self.position = (0,0)
        self.rides = []
        self.current_t = 0

class Ride():
    def __init__(self, id, start_x, start_y, dest_x, dest_y, earliest, latest):
        self.id = id
        self.start_x = int(start_x)
        self.start_y = int(start_y)
        self.dest_x = int(dest_x)
        self.dest_y = int(dest_y)
        self.earliest = int(earliest)
        self.latest = int(latest)
        self.car = None
        self.score = 0

    def __str__(self):
        return '[{}] from {},{} to {},{}'.format(self.id, self.start_x, self.start_y, self.dest_x, self.dest_y)

def parse_input(file):
    rides = []
    with open(file, 'r') as f:
        for i, line in enumerate(f):
            if i == 0: rows, cols, n_vehicles, n_rides, bonus, t = line.split(' ')
            else: rides.append(Ride(i - 1, *(line.split(' '))))
    return rides, int(rows), int(cols), int(n_vehicles), int(bonus), int(t)

def dump_rides(file, cars):
    with open(file, 'w') as f:
        for c in cars:
            f.write('{} '.format(len(c.rides)))
            for r in c.rides:
                f.write('{} '.format(r.id))
            f.write('\n')


def get_distance(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def get_distance_for_ride(ride):
    return get_distance((ride.start_x, ride.start_y), (ride.dest_x, ride.dest_y))

def count_steps(car, ride):
    new_t = car.current_t
    new_t += get_distance(car.position, (ride.start_x, ride.start_y))
    new_t += max(0, ride.earliest - car.current_t)
    new_t += get_distance((ride.start_x, ride.start_y), (ride.dest_x, ride.dest_y))
    return new_t - car.current_t

def get_global_average(rides):
    x = [r.start_x for r in rides]
    y = [r.start_y for r in rides]
    return np.mean(x), np.mean(y)

def score_ride(car, ride, bonus, medium):
    drive_distance = get_distance_for_ride(ride)
    pick_distance = get_distance(car.position, (ride.start_x, ride.start_y))
    wait_time = max(0, ride.earliest - (car.current_t + pick_distance))
    on_time = pick_distance + car.current_t <= ride.earliest
    dest_medium_dist = get_distance((ride.dest_x, ride.dest_y), medium)

    return drive_distance - pick_distance - wait_time + (bonus if on_time else 0) - dest_medium_dist

def pick_ride(car, rides, t, bonus):
    count_lookup = {}
    for r in rides:
        count_lookup[r.id] = count_steps(car, r)
    medium = get_global_average(rides)

    candidates = filter(lambda r: r.car is None, rides)
    candidates = filter(lambda r: count_lookup[r.id] < (t - car.current_t), candidates)
    candidates = filter(lambda r: car.current_t + count_lookup[r.id] <= r.latest, candidates)
    candidates = sorted(list(candidates), key=lambda r: score_ride(car, r, bonus, medium), reverse=True)
    return candidates[0] if len(candidates) > 0 else None

# In-place
def evaluate_car(car, rides, t, bonus, idles):
    c = car
    r = pick_ride(c, rides, t, bonus)
    if r is None: return None
    r.car = c
    c.rides.append(r)
    steps = count_steps(c, r)
    c.current_t += steps
    c.position = (r.dest_x, r.dest_y)
    idles.append((c, steps))
    return r

if __name__ == '__main__':
    rides, rows, cols, n_vehicles, bonus, t = parse_input(sys.argv[1])
    cars = [Car(i + 1) for i in range(n_vehicles)]

    idles = []

    for c in cars:
        evaluate_car(c, rides, t, bonus, idles)

    c = 0
    while len(idles) > 0:
        idles = sorted(idles, key=lambda i: i[1])
        car, idle_t = idles[0]
        idles = idles[1:]
        evaluate_car(car, rides, t, bonus, idles)
        if c % 10 == 0: print('{} rides in queue'.format(len(idles)))
        c += 1

    dump_rides(sys.argv[2] if len(sys.argv) > 2 else 'out.txt', cars)