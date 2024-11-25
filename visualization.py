from typing import List
from matplotlib import pyplot as plt
from states import Edge, State


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