package main

import (
	"bufio"
	"fmt"
	"math"
	"os"
	"sort"
	"strconv"
	"strings"
)

type Car struct {
	Id       int
	Position []float64 // bc. of 'medium' we need float coordinates
	Rides    []*Ride
	CurrentT int
}

type Ride struct {
	Id       int
	Start    []float64
	Dest     []float64
	Earliest int
	Latest   int
	Car      interface{}
}

type Config struct {
	Rows     int
	Cols     int
	NumCars  int
	NumRides int
	Bonus    int
	T        int
}

type Idle struct {
	Car  *Car
	Time int
}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

func atoi(a string) int {
	i, err := strconv.Atoi(a)
	check(err)
	return i
}

func atof(a string) float64 {
	return float64(atoi(a))
}

func parseInput(filePath string) ([]Ride, Config) {
	f, err := os.OpenFile(filePath, os.O_RDONLY, 0644)
	check(err)
	defer f.Close()
	scanner := bufio.NewScanner(f)

	var cfg Config
	var rides []Ride

	for c := 0; scanner.Scan(); c++ {
		line := strings.Split(scanner.Text(), " ")
		if c == 0 {
			cfg = Config{
				Rows:     atoi(line[0]),
				Cols:     atoi(line[1]),
				NumCars:  atoi(line[2]),
				NumRides: atoi(line[3]),
				Bonus:    atoi(line[4]),
				T:        atoi(line[5]),
			}
			rides = make([]Ride, cfg.NumRides)
		} else {
			rides[c-1] = Ride{
				Id:       c - 1,
				Start:    []float64{atof(line[0]), atof(line[1])},
				Dest:     []float64{atof(line[2]), atof(line[3])},
				Earliest: atoi(line[4]),
				Latest:   atoi(line[5]),
				Car:      nil,
			}
		}
	}
	return rides, cfg
}

func dumpOutput(filePath string, cars *[]Car) {
	f, err := os.Create(filePath)
	check(err)
	w := bufio.NewWriter(f)
	defer f.Close()
	defer w.Flush()
	for _, car := range *cars {
		w.WriteString(fmt.Sprintf("%d ", len(car.Rides)))
		for _, ride := range car.Rides {
			w.WriteString(fmt.Sprintf("%d ", ride.Id))
		}
		w.WriteString("\n")
	}
}

func getDistance(start, end []float64) float64 {
	return math.Abs(float64(start[0]-end[0])) + math.Abs(float64(start[1]-end[1]))
}

func getDistanceForRide(ride *Ride) float64 {
	return getDistance(ride.Start, ride.Dest)
}

func countSteps(car *Car, ride *Ride) int {
	newT := car.CurrentT
	newT += int(getDistance(car.Position, ride.Start))
	newT += int(math.Max(0, float64(ride.Earliest-car.CurrentT)))
	newT += int(getDistance(ride.Start, ride.Dest))
	return newT - car.CurrentT
}

func getGlobalAverage(rides *[]Ride) []float64 {
	n := float64(len(*rides))
	x, y := 0.0, 0.0
	for _, ride := range *rides {
		x += ride.Start[0]
		y += ride.Start[1]
	}
	return []float64{x / n, y / n}
}

func scoreRide(car *Car, ride *Ride, bonus int, medium []float64) float64 {
	driveDistance := getDistanceForRide(ride)
	pickDistance := getDistance(car.Position, ride.Start)
	waitTime := math.Max(0, float64(ride.Earliest)-(float64(car.CurrentT)+pickDistance))
	destMediumDist := getDistance(ride.Dest, medium)
	effectiveBonus := 0.0
	if int(pickDistance)+car.CurrentT <= ride.Earliest {
		effectiveBonus = float64(bonus)
	}
	return driveDistance - pickDistance - waitTime + effectiveBonus - destMediumDist
}

func pickRide(car *Car, rides *[]Ride, t, bonus int) *Ride {
	countLookup := make(map[int]int)
	for _, ride := range *rides {
		countLookup[ride.Id] = countSteps(car, &ride)
	}
	medium := getGlobalAverage(rides)
	candidates := make([]*Ride, 0)
	for i := range *rides {
		ride := &((*rides)[i])
		if ride.Car == nil &&
			countLookup[ride.Id] < (t-car.CurrentT) &&
			car.CurrentT+countLookup[ride.Id] <= ride.Latest {
			candidates = append(candidates, ride)
		}
	}
	sort.Slice(candidates, func(i, j int) bool {
		return scoreRide(car, candidates[i], bonus, medium) > scoreRide(car, candidates[j], bonus, medium)
	})
	if len(candidates) > 0 {
		return candidates[0]
	}
	return nil
}

func getNextIdleCar(idles *[]Idle) *Car {
	sort.Slice(*idles, func(i, j int) bool {
		return (*idles)[i].Time < (*idles)[j].Time
	})
	return (*idles)[0].Car
}

func evaluateCar(car *Car, rides *[]Ride, t, bonus int, idles *[]Idle) *Ride {
	ride := pickRide(car, rides, t, bonus)
	if ride == nil {
		return nil
	}
	ride.Car = car
	car.Rides = append(car.Rides, ride)
	steps := countSteps(car, ride)
	car.CurrentT += steps
	car.Position = ride.Dest
	*idles = append(*idles, Idle{Car: car, Time: steps})
	return ride
}

func main() {
	inPath := "data/a_example.in"
	outPath := "out.txt"
	if len(os.Args) > 1 {
		inPath = os.Args[1]
	}
	if len(os.Args) > 2 {
		outPath = os.Args[2]
	}

	rides, cfg := parseInput(inPath)
	cars := make([]Car, cfg.NumCars)
	for i := 1; i <= cfg.NumCars; i++ {
		cars[i-1] = Car{
			Id:       i,
			Position: []float64{0.0, 0.0},
			Rides:    make([]*Ride, 0),
			CurrentT: 0,
		}
	}
	idles := make([]Idle, 0)

	for i := range cars {
		evaluateCar(&cars[i], &rides, cfg.T, cfg.Bonus, &idles)
	}

	for c := 0; len(idles) > 0; c++ {
		car := getNextIdleCar(&idles)
		idles = idles[1:]
		evaluateCar(car, &rides, cfg.T, cfg.Bonus, &idles)
		if c%10 == 0 {
			fmt.Printf("%d rides in queue\n", len(idles))
		}
	}

	dumpOutput(outPath, &cars)
}
