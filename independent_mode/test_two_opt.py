import unittest, random, math, sys, os

# Ensure the pygame_sim module can be imported
current_dir = os.path.dirname(__file__)
sys.path.append(current_dir)
from pygame_sim import two_opt

def segments_intersect(a1, a2, b1, b2):
    def orient(p, q, r):
        return (q['x'] - p['x']) * (r['y'] - p['y']) - (q['y'] - p['y']) * (r['x'] - p['x'])
    o1 = orient(a1, a2, b1)
    o2 = orient(a1, a2, b2)
    o3 = orient(b1, b2, a1)
    o4 = orient(b1, b2, a2)
    return (o1 * o2 < 0) and (o3 * o4 < 0)

class TestTwoOpt(unittest.TestCase):
    def test_no_crossings(self):
        # Generate random points
        random.seed(0)
        points = [{'x': random.uniform(0, 100), 'y': random.uniform(0, 100)} for _ in range(10)]
        # Add a start point to close the tour
        start = points[0]
        path = two_opt([start] + points[1:] + [start])
        # Check for any crossing edges
        for i in range(len(path) - 1):
            for j in range(i + 2, len(path) - 1):
                if i == 0 and j == len(path) - 1:
                    continue
                a1, a2 = path[i], path[i+1]
                b1, b2 = path[j], path[j+1]
                self.assertFalse(segments_intersect(a1, a2, b1, b2), f"Edges {i}-{i+1} and {j}-{j+1} cross")

if __name__ == '__main__':
    unittest.main()
