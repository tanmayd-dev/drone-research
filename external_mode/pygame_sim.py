import pygame
import json
import math
import os
import sys
import random
from itertools import cycle

# Load config
with open('../config.json') as f:
    config = json.load(f)
with open(f"../{config['pois_file']}" ) as f:
    pois = json.load(f)
with open(f"../{config['obstacles_file']}") as f:
    obstacles = json.load(f)

MAP_W, MAP_H = config['map_size']
BIG_RANGE = config['big_drone_range']
SMALL_MULT_RANGE = config['small_drone_multiplier_range']
SMALL_DETECTION_RANGE = config.get('small_drone_detection_range', 5)
REGION_MARGIN = 2  # pixels

# Pygame settings
WIN_W, WIN_H = 1100, 800
MARGIN = 40
SCALE_X = (WIN_W - 2*MARGIN) / MAP_W
SCALE_Y = (WIN_H - 2*MARGIN) / MAP_H
BG_COLOR = (30, 30, 30)
POI_COLOR = (255, 200, 0)
BIG_COLOR = (0, 200, 255)
SMALL_BASE_COLORS = [
    (180, 180, 255), (180, 255, 180), (255, 180, 180), (255, 255, 180),
    (255, 180, 255), (180, 255, 255), (255, 220, 180), (220, 180, 255),
    (180, 220, 255), (220, 255, 180)
]

def to_screen(pt):
    return (int(MARGIN + pt['x']*SCALE_X), int(MARGIN + pt['y']*SCALE_Y))
def dist(a, b):
    return math.hypot(a['x'] - b['x'], a['y'] - b['y'])
def compute_grid(num_cells):
    cols = math.ceil(math.sqrt(num_cells))
    rows = math.ceil(num_cells / cols)
    return rows, cols
def grid_sweep_path(region, step):
    x0, y0, x1, y1 = region
    path = []
    x = x0
    direction = 1
    while x <= x1:
        if direction == 1:
            path.append({'x': x, 'y': y0})
            path.append({'x': x, 'y': y1})
        else:
            path.append({'x': x, 'y': y1})
            path.append({'x': x, 'y': y0})
        x += step
        direction *= -1
    return path
def nearest_neighbor_tsp(start, points):
    if not points:
        return [start, start]
    unvisited = points[:]
    path = [start]
    curr = start
    while unvisited:
        next_p = min(unvisited, key=lambda p: math.hypot(curr['x']-p['x'], curr['y']-p['y']))
        path.append(next_p)
        curr = next_p
        unvisited.remove(next_p)
    path.append(start)
    return path
def two_opt(path):
    best = path[:]
    improved = True
    def path_length(path):
        return sum(math.hypot(path[i]['x']-path[i+1]['x'], path[i]['y']-path[i+1]['y']) for i in range(len(path)-1))
    while improved:
        improved = False
        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                if j - i == 1:
                    continue
                new_path = best[:i] + best[i:j][::-1] + best[j:]
                if path_length(new_path) < path_length(best):
                    best = new_path
                    improved = True
        path = best
    return best
def kmeans(points, k, max_iter=10, seed=None):
    if not points:
        return [], [[] for _ in range(k)]
    if seed is not None:
        random.seed(seed)
    centers = random.sample(points, k) if len(points) >= k else [points[0]]*k
    for _ in range(max_iter):
        clusters = [[] for _ in range(k)]
        for p in points:
            dists = [dist(p, c) for c in centers]
            idx = dists.index(min(dists))
            clusters[idx].append(p)
        new_centers = []
        for cluster in clusters:
            if cluster:
                x = sum(p['x'] for p in cluster) / len(cluster)
                y = sum(p['y'] for p in cluster) / len(cluster)
                new_centers.append({'x': x, 'y': y})
            else:
                new_centers.append(random.choice(points))
        if all(dist(a, b) < 1e-3 for a, b in zip(centers, new_centers)):
            break
        centers = new_centers
    return centers, clusters

# EXTERNAL MODE: An external controller collects all detected POIs and assigns big drones using k-means clustering and TSP+2opt pathing
def compute_paths(num_big, num_small):
    # 1. Small drones grid search and detection
    rows, cols = compute_grid(num_big)
    big_regions = []
    region_w = MAP_W / cols
    region_h = MAP_H / rows
    for i in range(num_big):
        row = i // cols
        col = i % cols
        x0 = col * region_w
        y0 = row * region_h
        x1 = (col+1) * region_w if (col < cols-1 or i != num_big-1) else MAP_W
        y1 = (row+1) * region_h if (row < rows-1 or i != num_big-1) else MAP_H
        if i == num_big-1:
            x1 = MAP_W
            y1 = MAP_H
        if col > 0:
            x0 += REGION_MARGIN / 2
        if col < cols-1:
            x1 -= REGION_MARGIN / 2
        if row > 0:
            y0 += REGION_MARGIN / 2
        if row < rows-1:
            y1 -= REGION_MARGIN / 2
        big_regions.append((x0, y0, x1, y1))
    small_drones_per_big = [num_small // num_big] * num_big
    for i in range(num_small % num_big):
        small_drones_per_big[i] += 1
    small_paths = []
    detected_pois = []
    for i, (region, n_small) in enumerate(zip(big_regions, small_drones_per_big)):
        if n_small == 0:
            continue
        x0, y0, x1, y1 = region
        sub_w = (x1 - x0) / n_small
        small_color = SMALL_BASE_COLORS[i % len(SMALL_BASE_COLORS)]
        for j in range(n_small):
            sx0 = x0 + j * sub_w
            sx1 = sx0 + sub_w
            sweep_path = grid_sweep_path((sx0, y0, sx1, y1), SMALL_DETECTION_RANGE)
            region_center = {'x': (x0 + x1) / 2, 'y': (y0 + y1) / 2}
            path = [region_center] + sweep_path + [region_center]
            small_paths.append((path, small_color))
            for poi in pois:
                px, py = poi['x'], poi['y']
                in_region = (sx0 <= px < sx1) and (y0 <= py < y1)
                if not in_region:
                    if (abs(px - sx0) < REGION_MARGIN or abs(px - sx1) < REGION_MARGIN or abs(py - y0) < REGION_MARGIN or abs(py - y1) < REGION_MARGIN):
                        region_centers = [{'x': (r[0]+r[2])/2, 'y': (r[1]+r[3])/2} for r in big_regions]
                        dists = [dist(poi, pos) for pos in region_centers]
                        closest_idx = dists.index(min(dists))
                        if closest_idx != i:
                            continue
                    else:
                        continue
                for seg_idx in range(len(sweep_path)-1):
                    xA, yA = sweep_path[seg_idx]['x'], sweep_path[seg_idx]['y']
                    xB, yB = sweep_path[seg_idx+1]['x'], sweep_path[seg_idx+1]['y']
                    dx, dy = xB-xA, yB-yA
                    if dx == dy == 0:
                        dist_to_seg = math.hypot(px-xA, py-yA)
                    else:
                        t = max(0, min(1, ((px-xA)*dx + (py-yA)*dy)/(dx*dx+dy*dy)))
                        proj_x = xA + t*dx
                        proj_y = yA + t*dy
                        dist_to_seg = math.hypot(px-proj_x, py-proj_y)
                    if dist_to_seg <= SMALL_DETECTION_RANGE:
                        if poi not in detected_pois:
                            detected_pois.append(poi)
                        break
    # 2. K-means clustering on detected POIs for big drone placement
    if detected_pois:
        kmeans_seed = hash((num_big, num_small)) % (2**32)
        big_drone_positions, big_drone_poi_chunks = kmeans(detected_pois, num_big, seed=kmeans_seed)
    else:
        big_drone_positions = [{'x': MAP_W/2, 'y': MAP_H/2} for _ in range(num_big)]
        big_drone_poi_chunks = [[] for _ in range(num_big)]
    # 3. Big drone TSP+2opt, start and return to cluster center
    big_paths = []
    for big_pos, pois_list in zip(big_drone_positions, big_drone_poi_chunks):
        if pois_list:
            tsp_path = nearest_neighbor_tsp(big_pos, pois_list)
            tsp_path = two_opt(tsp_path)
            big_paths.append(tsp_path)
    return big_drone_positions, small_paths, big_paths

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption('Proposed Mode Drone Simulation')
    font = pygame.font.SysFont(None, 24)
    outdir = 'simulations'
    os.makedirs(outdir, exist_ok=True)
    num_big = BIG_RANGE[0]
    num_small = num_big * SMALL_MULT_RANGE[0]
    running = True
    clock = pygame.time.Clock()
    while running:
        screen.fill(BG_COLOR)
        big_positions, small_paths, big_paths = compute_paths(num_big, num_small)
        for poi in pois:
            pygame.draw.circle(screen, POI_COLOR, to_screen(poi), 7)
        for path, color in small_paths:
            s = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            pygame.draw.lines(s, color + (80,), False, [to_screen(p) for p in path], 3)
            screen.blit(s, (0, 0))
        for path in big_paths:
            pygame.draw.lines(screen, BIG_COLOR, False, [to_screen(p) for p in path], 3)
        for pos in big_positions:
            pygame.draw.circle(screen, BIG_COLOR, to_screen(pos), 12, 3)
        legend_x = 850
        legend_y = MARGIN
        legend_gap = 28
        pygame.draw.rect(screen, (50,50,50), (legend_x-10, legend_y-10, 230, 160), border_radius=8)
        screen.blit(font.render('Legend:', True, (255,255,255)), (legend_x, legend_y))
        pygame.draw.circle(screen, POI_COLOR, (legend_x+15, legend_y+legend_gap), 7)
        screen.blit(font.render('POI', True, (255,255,255)), (legend_x+35, legend_y+legend_gap-10))
        pygame.draw.circle(screen, BIG_COLOR, (legend_x+15, legend_y+2*legend_gap), 12, 3)
        screen.blit(font.render('Big Drone', True, (255,255,255)), (legend_x+35, legend_y+2*legend_gap-10))
        pygame.draw.line(screen, (180, 180, 255), (legend_x+5, legend_y+3*legend_gap), (legend_x+25, legend_y+3*legend_gap), 3)
        screen.blit(font.render('Small Drone Path', True, (255,255,255)), (legend_x+35, legend_y+3*legend_gap-10))
        pygame.draw.line(screen, BIG_COLOR, (legend_x+5, legend_y+4*legend_gap), (legend_x+25, legend_y+4*legend_gap), 3)
        screen.blit(font.render('Big Drone Path', True, (255,255,255)), (legend_x+35, legend_y+4*legend_gap-10))
        info = f'Big drones: {num_big}   Small drones: {num_small}   (Left/Right: big, Up/Down: small, S: save, Q: quit)'
        txt = font.render(info, True, (255,255,255))
        screen.blit(txt, (MARGIN, 10))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_LEFT:
                    if num_big > BIG_RANGE[0]:
                        num_big -= 1
                        num_small = max(num_big * SMALL_MULT_RANGE[0], num_small)
                elif event.key == pygame.K_RIGHT:
                    if num_big < BIG_RANGE[1]:
                        num_big += 1
                        num_small = max(num_big * SMALL_MULT_RANGE[0], num_small)
                elif event.key == pygame.K_UP:
                    if num_small < num_big * SMALL_MULT_RANGE[1]:
                        num_small += 1
                elif event.key == pygame.K_DOWN:
                    if num_small > num_big * SMALL_MULT_RANGE[0]:
                        num_small -= 1
                elif event.key == pygame.K_s:
                    fname = os.path.join(outdir, f'sim_big{num_big}_small{num_small}.png')
                    pygame.image.save(screen, fname)
        clock.tick(30)
    pygame.quit()

if __name__ == '__main__':
    main() 