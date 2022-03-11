#!/usr/bin/env python3
"""
Read rocprof csv data from two different runs of the ROCm profiler hsa trace and
find kernels with the biggest performance deltas. Compare kernels in the order
in which they appear in the profiler data.

Usage Example: compare_rocprof_hsa_trace.py 4.3.1/results.csv 7774-no-sap/results.csv results.csv 

Argv[1] = rocprof hsa-trace csv #1.
Argv[2] = rocprof hsa-trace csv #2.
Argv[3] = Name of output csv file to write.

TODO: Add args parse.
"""

import sys
import statistics
import csv
import cProfile
import itertools
from pstats import Stats, SortKey

NUMBER_OF_DATA_COLUMNS = 21

# FIXME: Optmize this function. It is a huge bottleneck.
def collectPerfData(filename):
    with open(filename, "r") as rocprofDataFile:
        # Pairs of kernel names and exec duration.
        data = {}

        # Skip the first line which is the column labels.
        rocprofDataFile.readline()

        for tokens in csv.reader(rocprofDataFile):
            if len(tokens) == NUMBER_OF_DATA_COLUMNS:
                kernelName = tokens[1]
                durationNs = int(str.strip(tokens[20]))
                if kernelName in data:
                    data[kernelName].append(durationNs)
                else:
                    data[kernelName] = [durationNs]
            else:
                print(tokens)

        return data


# Check whether the kernel name exists in both lists and compile data.
def getKernelsNotInOtherData(data1, data2):
    return list(set(data1.keys()).difference(data2.keys()))


def collectMismatchData(rocProfData1, rocProfData2):
    mismatchKernels1 = getKernelsNotInOtherData(rocProfData1, rocProfData2)
    mismatchKernels2 = getKernelsNotInOtherData(rocProfData2, rocProfData1)

    mismatchData1 = [
        (k, len(rocProfData1[k]), sum(rocProfData1[k])) for k in mismatchKernels1
    ]
    mismatchData2 = [
        (k, len(rocProfData2[k]), sum(rocProfData2[k])) for k in mismatchKernels2
    ]

    sortedData1 = sorted(
        mismatchData1, key=lambda mismatchData1: mismatchData1[2], reverse=True
    )
    sortedData2 = sorted(
        mismatchData2, key=lambda mismatchData2: mismatchData2[2], reverse=True
    )

    return [
        (
            d1[0] if d1 else "N/A",
            d1[1] if d1 else 0,
            d1[2] if d1 else 0,
            d2[0] if d2 else "N/A",
            d2[1] if d2 else 0,
            d2[2] if d2 else 0,
        )
        for d1, d2 in itertools.zip_longest(sortedData1, sortedData2)
    ]


def compareRocprofHsaTrace(traceDataFilename1, traceDataFilename2):
    rocProfData1 = collectPerfData(traceDataFilename1)
    print("Finished collecting prof data 1...", flush=True)
    rocProfData2 = collectPerfData(traceDataFilename2)
    print("Finished collecting prof data 2...", flush=True)

    result = []
    # FIXME: Data needs some struct and a function to print it.
    for kernel1, durations1 in rocProfData1.items():
        for kernel2, durations2 in rocProfData2.items():
            if kernel1 == kernel2:
                sumKernel1 = sum(durations1)
                sumKernel2 = sum(durations2)
                medianKernel1 = statistics.median(durations1)
                medianKernel2 = statistics.median(durations2)
                result.append(
                    (
                        kernel1,  # Kernel name
                        sumKernel1,  # SUM runtimes 1
                        sumKernel2,  # SUM runtimes 2
                        sumKernel2 - sumKernel1,  # SUM diff
                        (sumKernel2 - sumKernel1) / sumKernel1,  # %SUM diff
                        medianKernel2 - medianKernel1,  # MEAN diff
                        (medianKernel2 - medianKernel1) / medianKernel1,  # %MEAN diff
                        len(durations1),  # Number of kernels 1
                        len(durations2),  # Number of kernels 2
                    )
                )
                break
    print("Finished finding the delta between kernels...", flush=True)

    sortedResult = sorted(result, key=lambda dataPoint: dataPoint[3], reverse=True)

    # Data from kernels that don't exist in both sets of data.
    mismatchResult = collectMismatchData(rocProfData1, rocProfData2)

    return (sortedResult, mismatchResult)


if __name__ == "__main__":
    DO_PROFILE = False
    if DO_PROFILE == True:
        with cProfile.Profile() as pr:
            result = compareRocprofHsaTrace(sys.argv[1], sys.argv[2])

        with open("profiling_stat.txt", "w") as stream:
            stats = Stats(pr, stream=stream)
            stats.strip_dirs()
            stats.sort_stats("time")
            stats.dump_stats(".prof_stats")
            stats.print_stats()
    else:
        result = compareRocprofHsaTrace(sys.argv[1], sys.argv[2])

    # Export kernel comparision to csv.
    with open(sys.argv[3], "w") as dataCsvF:
        dataCsvW = csv.writer(dataCsvF)
        labels = (
            "Kernel name",
            "SUM runtimes 1",
            "SUM runtimes 2",
            "SUM diff",
            "%SUM diff",
            "MEAN diff",
            "%MEAN diff",
            "Number of kernels 1",
            "Number of kernels 2",
        )
        print(labels)
        dataCsvW.writerow(labels)

        for dataPoint in result[0]:
            print(dataPoint)
            dataCsvW.writerow(dataPoint)

    # Export mismatched kernels to csv.
    # FIXME: Extract these to functions.
    with open("mismatches_" + sys.argv[3], "w") as mismatchCsvF:
        mismatchCsvW = csv.writer(mismatchCsvF)
        labels = (
            "Mismatched kernels file 1",
            "Number of kernels 1",
            "Sum of runtimes 1",
            "Mismatched kernels file 2",
            "Number of kernels 2",
            "Sum of runtimes 2",
        )
        print(labels)
        mismatchCsvW.writerow(labels)

        for dataPoint in result[1]:
            print(dataPoint)
            mismatchCsvW.writerow(dataPoint)
