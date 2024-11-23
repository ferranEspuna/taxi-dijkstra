import json
from dataclasses import dataclass
from typing import Tuple

speed = 1.0

def dist(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

with open('example.json') as json_file:
    info = json.load(json_file)

taxis = info['vehicles']
people = info['customers']
for person in people:
    person['dist'] = dist((person['coordX'], person['coordY']), (person['destinationX'], person['destinationY']))
    person['time'] = person['dist'] / speed

@dataclass(frozen=True)
class TaxiState:
    x: int
    y: int
    customers: Tuple[int, ...] = tuple()
    firstFree: float = 0.0


@dataclass(frozen=True)
class State:

    done: Tuple[bool, ...]
    taxi_states: Tuple[TaxiState, ...]

    @classmethod
    def start(cls):
        return cls(
            done=tuple(False for _ in people),
            taxi_states=tuple(TaxiState(x=taxi['coordX'], y=taxi['coordY']) for taxi in taxis)

        )

    def max_waiting_time(self):
        return max(taxi.firstFree for taxi in self.taxi_states)

    def next(self, customer_idx, taxi_idx):

        new_done = list(self.done)
        assert not new_done[customer_idx]
        new_done[customer_idx] = True
        new_done = tuple(new_done)

        new_taxi_states = list(self.taxi_states)
        old_taxi_state = new_taxi_states[taxi_idx]
        new_taxi_state = TaxiState(
            x=people[customer_idx]['destinationX'],
            y=people[customer_idx]['destinationY'],
            customers=tuple(list(old_taxi_state.customers) + [customer_idx]),
            firstFree=old_taxi_state.firstFree + (
                dist((old_taxi_state.x, old_taxi_state.y),
                     (people[customer_idx]['coordX'], people[customer_idx]['coordY'])
                     )
                + people[customer_idx]['time']
            ) / speed
        )
        new_taxi_states[taxi_idx] = new_taxi_state
        new_taxi_states = tuple(new_taxi_states)

        return State(done=new_done, taxi_states=new_taxi_states)

    def edges(self):
        for i, customer in enumerate(people):
            if self.done[i]:
                continue
            for j, taxi in enumerate(taxis):
                n = self.next(i, j)
                yield {
                    'edge': (i, j),
                    'state': n,
                    # right now, the cost is the time to reach destination --> total cost is the total time
                    'cost': n.taxi_states[j].firstFree
                }

    def is_goal(self):
        return all(self.done)

    def remaining_customers(self):
        return sum(not done for done in self.done)



if __name__ == '__main__':

    s = State.start()
    n = s.next(0, 0).next(1, 1)
    nn = s.next(1, 1).next(0,0)

    print(s)
    print(n)

    assert nn == n
    print('all good')






