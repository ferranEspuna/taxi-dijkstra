from states import State, Edge
import heapq
import time

def dijkstra(start, heuristic=False):
    count = 0
    queue = []
    heapq.heappush(queue, (0, 0, count, Edge(start), start))
    count += 1
    visited = dict()
    while queue:
        prev_est_cost, prev_cost, _, old_edge, prev = heapq.heappop(queue)

        old_state = old_edge.state

        if old_state in visited:
            continue

        visited[old_state] = (prev, old_edge)

        if old_state.is_goal():
            return old_state, visited, prev_cost

        for new_edge in old_state.edges():
            cost = prev_cost + new_edge.cost
            est_cost = cost

            if heuristic:

                # make sure the heuristic is consistent
                assert old_state.heuristic() <= new_edge.state.heuristic() + new_edge.cost
                est_cost += new_edge.state.heuristic()

            heapq.heappush(queue, (est_cost, cost, count, new_edge, old_state))
            count += 1

def reconstruct_edges(state, visited) -> list:

    edges = []
    state, edge = visited[state]


    while edge.edge is not None:

        edges.append(edge)
        state, edge = visited[state]

    edges.reverse()
    return edges

if __name__ == '__main__':

    t0 = time.time()
    State.initialize('example.json', speed=1.0)

    final_state, visited_dict, total_cost = dijkstra(State.start(), heuristic=True)

    path = reconstruct_edges(final_state, visited_dict)
    print(f'Computation time: {time.time() - t0}')
    print()
    print('\n'.join(str(edge) for edge in path))
    print(f'Total cost: {total_cost}')
