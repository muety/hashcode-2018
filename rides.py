class Car():
    def __init__(self, id):
        self.id = id
        self.position = (0,0)

class Ride():
    def __init__(self, id, start_x, start_y, dest_x, dest_y, earliest, latest):
        self.id = id
        self.start_x = start_x
        self.start_y = start_y
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.earliest = earliest
        self.latest = latest
        self.completed = False
        self.car = None
        self.score = 0

    def __str__(self):
        return '[{}] from {},{} to {},{}'.format(self.id, self.start_x, self.start_y, self.dest_x, self.dest_y)

def parse_input(file):
    rides = []
    with open(file) as f:
        for i, line in enumerate(f):
            if i == 0: rows, cols, n_vehicles, n_rides, bonus, t = line.split(' ')
            rides.append(Ride(i, *(line.split(' '))))
    return rides, rows, cols, n_vehicles, bonus, t

def get_distance(start, end):
    return abs(start[0] - end[0]) + abs(start[1] - end[1])

def score_ride(car, ride):
    return 1

def pick_ride(car, rides):
    filtered = [r for r in rides if not r.completed and r.car is None]
    return sorted(filtered, key=lambda r: score_ride(car, r), reverse=True)[0]

if __name__ == '__main__':
    rides, rows, cols, n_vehicles, bonus, t = parse_input('data/a_example.in')
    cars = [Car(i) for i in range(n_vehicles)]

    for c in cars:
        r = pick_ride(c, rides)
        r.car = c

    print(rides[0])