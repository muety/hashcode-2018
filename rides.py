import sys
from tqdm import tqdm


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

def score_ride(car, ride, bonus):
    drive_distance = get_distance_for_ride(ride)
    pick_distance = get_distance(car.position, (ride.start_x, ride.start_y))
    wait_time = max(0, ride.earliest - (car.current_t + pick_distance))
    on_time = pick_distance + car.current_t <= ride.earliest

    # TODO: weights
    return drive_distance - pick_distance - wait_time + (bonus if on_time else 0)

def pick_ride(car, rides, t, bonus):
    count_lookup = {}
    for r in rides:
        count_lookup[r.id] = count_steps(car, r)

    candidates = filter(lambda r: r.car is None, rides)
    candidates = filter(lambda r: count_lookup[r.id] < (t - car.current_t), candidates)
    candidates = filter(lambda r: car.current_t + count_lookup[r.id] <= r.latest, candidates)
    candidates = sorted(list(candidates), key=lambda r: score_ride(car, r, bonus), reverse=True)
    return candidates[0] if len(candidates) > 0 else None

if __name__ == '__main__':
    rides, rows, cols, n_vehicles, bonus, t = parse_input(sys.argv[1])
    cars = [Car(i + 1) for i in range(n_vehicles)]
    pbar = tqdm(total=n_vehicles)

    for c in cars:
        r = pick_ride(c, rides, t, bonus)
        can_pick = r is not None
        while can_pick:
            r = pick_ride(c, rides, t, bonus)
            if r is None: break

            r.car = c
            c.rides.append(r)
            c.current_t += count_steps(c, r)
            c.position = (r.dest_x, r.dest_y)
        pbar.update(1)

    dump_rides('out.txt', cars)
    pbar.close()