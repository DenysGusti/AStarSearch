import argparse
import yaml
import heapq

# defined types for clarity
ProblemDict = dict[str, str | list[str] | dict[str, dict[str, float]]]
HeuristicDict = dict[str, dict[str, float]]
SolutionDict = dict[str, int | float | list[str] | dict[str, float]]


def load_problem(filename: str) -> tuple[ProblemDict, HeuristicDict]:
    """Loads the YAML file and returns the problem details and heuristic information."""
    with open(filename, 'r') as file:
        data = yaml.safe_load(file)
    return data['problem'], data['additional_information']


def save_solution(filename: str, solution: SolutionDict) -> None:
    """Saves the A* solution to a YAML file in the required format."""
    with open(filename, 'w') as file:
        yaml.dump({'solution': solution}, file)


class AStarSearch:
    def __init__(self, problem: ProblemDict, heuristic_info: HeuristicDict) -> None:
        self.heuristic_info: HeuristicDict = {
            city.removeprefix('city_'): heuristic_details for city, heuristic_details in heuristic_info.items()
        }
        self.cities: list[str] = problem['cities']
        self.city_start: str = problem['city_start']
        self.city_end: str = problem['city_end']
        self.connections: dict[str, dict[str, float]] = {
            city.removeprefix('city_'): details['connects_to'] for city, details in problem.items() if
            city.startswith('city_') and city not in ['city_start', 'city_end']
        }

    def heuristic(self, city: str, mode: str = 'no') -> float:
        """
        Computes the heuristic value for the given city.
        - mode='no': No heuristic (Uniform-Cost Search).
        - mode='simple': Use only line_of_sight_distance.
        - mode='advanced': Use line_of_sight_distance and altitude_difference.
        """
        match mode:
            case 'no':
                return 0.
            case 'simple':
                info = self.heuristic_info[city]
                line_of_sight_distance = info['line_of_sight_distance']
                return line_of_sight_distance
            case 'advanced':
                info = self.heuristic_info[city]
                line_of_sight_distance = info['line_of_sight_distance']
                altitude_difference = info['altitude_difference']
                return (line_of_sight_distance ** 2 + altitude_difference ** 2) ** 0.5
            case _:
                raise ValueError(f"Invalid heuristic mode: {mode}")

    def a_star(self, heuristic_mode: str) -> SolutionDict:
        """Runs the A* algorithm with the specified heuristic function."""
        heuristic_values: dict[str, float] = {city: self.heuristic(city, heuristic_mode) for city in self.cities}
        start, goal = self.city_start, self.city_end
        # priority queue with (cost + heuristic, city)
        frontier: list[tuple[float, str]] = [(heuristic_values[start], start)]
        explored: set[str] = set()
        came_from: dict[str, str] = {}  # to reconstruct path
        # currently known cost of the cheapest path from start to city, explored + frontier
        g_costs: dict[str, float] = {start: 0.}

        while frontier:
            current_cost, current_city = heapq.heappop(frontier)

            # check if goal reached
            if current_city == goal:
                total_cost = g_costs[self.city_end]
                path = self.reconstruct_path(came_from)
                heuristic_output = {f"city_{city}": heuristic for city, heuristic in heuristic_values.items()}
                return {
                    'cost': total_cost,
                    'path': path,
                    'expanded_nodes': len(explored),
                    'heuristic': heuristic_output
                }

            explored.add(current_city)

            # explore neighbors
            for neighbor, move_cost in self.connections[current_city].items():
                tentative_g_cost = g_costs[current_city] + move_cost

                if neighbor not in g_costs or tentative_g_cost < g_costs[neighbor]:
                    came_from[neighbor] = current_city
                    g_costs[neighbor] = tentative_g_cost
                    priority = tentative_g_cost + heuristic_values[neighbor]
                    heapq.heappush(frontier, (priority, neighbor))

            # print(f'{current_cost, current_city = }\n{frontier = }\n{explored = }\n{g_costs = }\n')

        # no solution found
        raise ValueError("No path found from start to goal.")

    def reconstruct_path(self, came_from: dict[str, str]) -> list[str]:
        """Reconstructs the path from start to goal."""
        path: list[str] = []
        current = self.city_end
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(self.city_start)
        path.reverse()
        return path


def main() -> None:
    parser = argparse.ArgumentParser(description='Run A* search on a given problem file.')
    parser.add_argument('filename', help='The YAML file containing the problem description')
    args = parser.parse_args()

    try:
        problem, heuristic_info = load_problem(args.filename)

        search = AStarSearch(problem, heuristic_info)

        # Run A* with no heuristic (Uniform-Cost Search)
        solution1 = search.a_star(heuristic_mode='no')
        save_solution('aufgabe1-1.yaml', solution1)

        # Run A* with simple heuristic (line_of_sight_distance)
        solution2 = search.a_star(heuristic_mode='simple')
        save_solution('aufgabe1-2.yaml', solution2)

        # Run A* with advanced heuristic (line_of_sight_distance and altitude_difference)
        solution3 = search.a_star(heuristic_mode='advanced')
        save_solution('aufgabe1-3.yaml', solution3)

    except Exception as e:
        raise ValueError(f'An error occurred: {e}')


if __name__ == '__main__':
    main()
