class Car():
    def __init__(self):
        pass

class Ride():
    def __init__(self, id, start_x, start_y, dest_x, dest_y, earliest, latest):
        self.id = id
        self.start_x = start_x
        self.start_y = start_y
        self.dest_x = dest_x
        self.dest_y = dest_y
        self.earliest = earliest
        self.latest = latest

    def __str__(self):
        return '[{}] from {},{} to {},{}'.format(self.id, self.start_x, self.start_y, self.dest_x, self.dest_y)

def parse_input(file):
    rides = []
    with open(file) as f:
        for i, line in enumerate(f):
            if i == 0: rows, cols, n_vehicles, n_rides, bonus, t = line.split(' ')
            rides.append(Ride(i, *(line.split(' '))))
    return rides, rows, cols, n_vehicles, bonus, t


if __name__ == '__main__':
    rides, rows, cols, n_vehicles, bonus, t = parse_input('data/a_example.in')
    print(rides[0])