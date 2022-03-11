# rocprof_compare

### Usage
Read rocprof csv data from two different runs of the ROCm profiler hsa trace
and find kernels with the biggest performance deltas. Compare kernels in the
order in which they appear in the profiler data.

Usage Example: `compare_rocprof_hsa_trace.py ./4.3.1/results.csv ./7774-no-sap/results.csv results.csv`

Argv[1] = rocprof hsa-trace csv #1.
Argv[2] = rocprof hsa-trace csv #2.
Argv[3] = Name of output csv file to write

### Tests
Run with: `pytest rocprof_compare/test/`
