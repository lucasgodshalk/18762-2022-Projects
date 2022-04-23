from lib.Solve import solve
from lib.settings import Settings
from parsers.parser import parse_raw
from scipy.io import loadmat
from lib.process_results import display_mat_comparison

# path to the grid network RAW file
casename = 'testcases/GS-4_prior_solution.RAW'
#casename = 'testcases/IEEE-14_prior_solution.RAW'
#casename = 'testcases/IEEE-118_prior_solution.RAW'
#casename = 'testcases/ACTIVSg500_prior_solution_fixed.RAW'
#casename = 'testcases/PEGASE-9241_flat_start.RAW'

raw_data = parse_raw(casename)

settings = Settings(debug=True, max_iters=30, flat_start=True, infeasibility_analysis=True, use_sparse=False)

result = solve(raw_data, settings)

result.display()

#mat = loadmat(f'testcases/output-{casename}.mat')
#display_mat_comparison(mat, result)