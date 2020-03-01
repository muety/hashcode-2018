# hashcode-2018

![](https://anchr.io/i/hkAyX.png)

This is my multi-threaded solution for the practice round in [Google Hash Code](https://hashcode.withgoogle.com) 2018. It **does not** produce an optimal solution and **does not** run efficiently at all. Several simplifying assumptions are made and there are a few constraints. The problem statement can be found [here (.pdf)](https://github.com/alesolano/hashcode-pizza/raw/master/pizza.pdf).

## Usage
`python3 pizza.py data/medium.in medium.out.txt`

Optionally, a third argument can be given to specify the number of threads to use for concurrency, e.g. `python3 pizza.py data/medium.in medium.out.txt 4`.

## Approach
First of all, we only consider 1-dimensional slices for simplicity. This assumption should work in most cases. However, for the example it wouldn't.
In every iteration, we walk through the entire pizza matrix and try to find the cell(s) for which it is the "hardest" to gather all ingredients in a piece with it.
This is determined by considering the max amount of cells required. Subsequently, slicing is done for that cell first (the left-upper-most if there are multiple) and so on.

## Optimizations
* More efficient computations
* Only do partial re-evaluation also in horizontal direction
* Add "postprocessing" step to re-arrange slices, i.e. for every gap, check whether a surrounding slice could lend a cell
* Consider multi-directional slicing (up + down or left + right) for a given cell, i.e. go up and down simultaneously for instance.
* Also consider 2-dimensional slices
* Introduce some kind of heuristic to determine optimal slice size - currently we try to maximize slices

## Scores
* Small: **40 points** (95 %)
* Medium: **38442 points** (77 %)
* Big: _timeout_

## Lessons learned
**The simpler the better**. [alesolano/hashcode-pizza](https://github.com/alesolano/hashcode-pizza) achieved a pretty descent score with a very naive approach where computations on the big file took less than a minute - single-threaded.
My multi-threaded script did not terminate at all for the big file on a 12-core GCP instance within ten hours. Of course, **performance optimization and efficiency** is crucial, too, but probably there#s not enough time during the real challenge.

## License
MIT