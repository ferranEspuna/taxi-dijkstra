from states import State
import heapq
import time

def dijkstra(start, heuristic=False):
    count = 0
    queue = []
    heapq.heappush(queue, (0, 0, count, start, start, None))
    count += 1
    visited = dict()
    while queue:
        prev_est_cost, prev_cost, _, state, prev, edge = heapq.heappop(queue)
        print(state.remaining_customers())
        if state in visited:
            continue

        visited[state] = (prev, edge)

        if state.is_goal():
            return state, visited

        edges = list(state.edges())

        for edge in edges:
            cost = prev_cost + edge['cost']
            est_cost = cost

            if heuristic:
                # assert state.heuristic() <= edge['state'].heuristic() + edge['cost']
                est_cost += edge['state'].heuristic()

            heapq.heappush(queue, (est_cost, cost, count, edge['state'], state, edge['edge']))
            count += 1

def reconstruct_edges(state, visited):

    edges = []
    state, edge = visited[state]


    while edge is not None:

        edges.append(edge)
        state, edge = visited[state]

    edges.reverse()
    return edges

if __name__ == '__main__':

    t0 = time.time()
    x = reconstruct_edges(* dijkstra(State.start(), heuristic=False))
    print(time.time() - t0)

    print(x)
