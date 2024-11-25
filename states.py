import json
from dataclasses import dataclass
from typing import Tuple, List, ClassVar, Optional
from itertools import combinations
import matplotlib.pyplot as plt


def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

@dataclass(frozen=True)
class TaxiState:
    x: int
    y: int
    customers: Tuple[int | str, ...] = tuple()
    firstFree: float = 0.0
    dead: bool = False

@dataclass(frozen=True)
class Edge:
    state: 'State'
    edge: Optional[List[Tuple[int, int]]]  = None
    cost: float = 0.0

    def __repr__(self):
        return '\n'.join(
            f'Customer {i} goes with taxi {j}, waiting time: {self.state.taxi_states[j].firstFree}'
            for i, j in self.edge
        )


@dataclass(frozen=True)
class State:

    done: Tuple[bool, ...]
    taxi_states: Tuple[TaxiState, ...]
    _people: ClassVar[List[dict] | None] = None
    _taxis: ClassVar[List[dict] | None] = None
    _speed: ClassVar[float] = 1.0

    @classmethod
    def initialize(cls, filename: str, speed: float = 1.0) -> None:

        with open(filename) as json_file:
            info = json.load(json_file)

        cls._people = info['customers']
        cls._taxis = info['vehicles']
        cls._speed = speed

        for person in cls._people:
            person['dist'] = dist((person['coordX'], person['coordY']),
                                  (person['destinationX'], person['destinationY']))
            person['time'] = person['dist'] / speed


    @classmethod
    def start(cls) -> 'State':

        assert cls._people is not None and cls._taxis is not None,\
            'Initialize the data first. For example, State.initialize("smol.json")'

        return cls(
            done=tuple(False for _ in cls._people),
            taxi_states=tuple(TaxiState(x=taxi['coordX'], y=taxi['coordY']) for taxi in cls._taxis)

        )

    def max_waiting_time(self) -> float:
        return max(taxi.firstFree for taxi in self.taxi_states)

    def next(self, assignments) -> 'State':

        customer_indices = [i for i, _ in assignments]
        taxi_indices = [j for _, j in assignments]

        assert len(set(customer_indices)) == len(customer_indices)
        assert len(set(taxi_indices)) == len(taxi_indices)

        new_done = list(self.done)
        new_taxi_states = list(self.taxi_states)

        for customer_idx, taxi_idx in assignments:

            assert not self.taxi_states[taxi_idx].dead
            assert not self.done[customer_idx]

            new_done[customer_idx] = True

            old_taxi_state = new_taxi_states[taxi_idx]
            new_taxi_state = TaxiState(
                x=self._people[customer_idx]['destinationX'],
                y=self._people[customer_idx]['destinationY'],
                customers=tuple(list(old_taxi_state.customers) + [customer_idx]),
                firstFree=old_taxi_state.firstFree + (
                    dist((old_taxi_state.x, old_taxi_state.y),
                         (self._people[customer_idx]['coordX'], self._people[customer_idx]['coordY'])
                         )
                    + self._people[customer_idx]['time']
                ) / self._speed
            )
            new_taxi_states[taxi_idx] = new_taxi_state

        for taxi_idx in range(len(self._taxis)):
            if not taxi_idx in taxi_indices and not new_taxi_states[taxi_idx].dead:
                new_taxi_states[taxi_idx] = TaxiState(
                    x=self.taxi_states[taxi_idx].x,
                    y=self.taxi_states[taxi_idx].y,
                    customers=self.taxi_states[taxi_idx].customers,
                    firstFree=self.taxi_states[taxi_idx].firstFree,
                    dead=True
                )


        new_done = tuple(new_done)
        new_taxi_states = tuple(new_taxi_states)

        return State(done=new_done, taxi_states=new_taxi_states)

    def edges(self) -> List[Edge]:

        # iterate for all sets of taxis and sets of customers
        avail_taxis = [i for i, taxi in enumerate(self.taxi_states) if not taxi.dead]
        avail_customers = [i for i, done in enumerate(self.done) if not done]

        # for all subsets of taxis
        for l in range(1, len(avail_taxis) + 1):
            for tax_idxs in combinations(avail_taxis, l):
                for pep_idxs in combinations(avail_customers, l):
                    assignments = [(pep_idx, tax_idx) for pep_idx, tax_idx in zip(pep_idxs, tax_idxs)]
                    next_state = self.next(assignments)

                    yield Edge(
                        edge=assignments,
                        state=next_state,
                        cost=sum(next_state.taxi_states[j].firstFree for j in tax_idxs)
                    )

    def is_goal(self) -> bool:
        return all(self.done)

    def remaining_customers(self) -> int:
        return sum(not done for done in self.done)

    def heuristic(self) -> float:
        return sum(
            customer['time'] + min(
                dist((taxi.x, taxi.y), (customer['coordX'], customer['coordY'])
                     ) / self._speed + taxi.firstFree
                for taxi in self.taxi_states
                if not taxi.dead
            )
            for customer_idx, customer in enumerate(self._people)
            if not self.done[customer_idx]
        )

    @property
    def people(self):
        return self._people


def visualize_path(path: List[Edge]) -> None:

    # initial starting positions
    taxi_positions = [(taxi.x, taxi.y) for taxi in State.start().taxi_states]
    people_positions = [(person['coordX'], person['coordY']) for person in path[0].state.people]

    # decide colors of the taxis on a gradient
    colors = ['r', 'g', 'b', 'y', 'm', 'c', 'k']

    # plot the initial positions of taxis

    for j, (x, y) in enumerate(taxi_positions):
        plt.plot(x, y, colors[j % len(colors)] + 'o')

    for edge in path:

        for i, j in edge.edge:


            # draw line between taxi position and customer position, in dashed line
            plt.plot(
                [taxi_positions[j][0], people_positions[i][0]], [taxi_positions[j][1], people_positions[i][1]],
                     colors[j % len(colors)], linestyle='dashed')

            # update taxi position
            taxi_positions[j] = (edge.state.taxi_states[j].x, edge.state.taxi_states[j].y)

            x_start, y_start = people_positions[i]
            x_end, y_end = taxi_positions[j]

            plt.plot([x_start, x_end], [y_start, y_end], colors[j % len(colors)])

            plt.arrow(
                x_start, y_start,
                (x_end - x_start) / 2, (y_end - y_start) / 2,
                color=colors[j % len(colors)], linestyle='solid',
                head_width=0.001, length_includes_head=True, width=0.0001
            )

    plt.show()

if __name__ == '__main__':

    State.initialize('smol.json', speed=1.0)

    s = State.start()
    n = s.next([(0, 1)])

    try:
        n = n.next([(1, 0)])
        assert False
    except AssertionError:
        pass

    print(n)
    print('all good')






