import json
import numpy as np
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from independent_mode.energy_calc import run_energy_sweep as run_indep
from external_mode.energy_calc import run_energy_sweep as run_ext

# Load config once
with open('config.json') as f:
    config = json.load(f)

MAP_W, MAP_H = config['map_size']
POI_SWEEP_RANGE = config.get('poi_sweep_range', [1, 1000])

# Helper to generate POIs using numpy
def generate_pois(n):
    xs = np.random.randint(0, MAP_W+1, size=n)
    ys = np.random.randint(0, MAP_H+1, size=n)
    return [{"x": int(x), "y": int(y)} for x, y in zip(xs, ys)]

def process_poi_count(num_pois):
    pois = generate_pois(num_pois)
    indep_rows = run_indep(config, pois)
    ext_rows = run_ext(config, pois)
    indep_results = [[row[0], row[1], num_pois, row[2]] for row in indep_rows]
    ext_results = [[row[0], row[1], num_pois, row[2]] for row in ext_rows]
    return indep_results, ext_results

if __name__ == "__main__":
    with open('sweep_results_independent.csv', 'w') as f_indep, open('sweep_results_external.csv', 'w') as f_ext:
        f_indep.write('big_drones,small_drones,POIs,energy\n')
        f_ext.write('big_drones,small_drones,POIs,energy\n')
        with ProcessPoolExecutor() as executor:
            for indep_results, ext_results in tqdm(executor.map(process_poi_count, range(POI_SWEEP_RANGE[0], POI_SWEEP_RANGE[1]+1)), total=POI_SWEEP_RANGE[1]-POI_SWEEP_RANGE[0]+1, desc='POIs'):
                for row in indep_results:
                    f_indep.write(','.join(map(str, row)) + '\n')
                for row in ext_results:
                    f_ext.write(','.join(map(str, row)) + '\n')

    print('Sweep complete. Results saved to sweep_results_independent.csv and sweep_results_external.csv.') 