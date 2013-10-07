#!/usr/bin/env bash
#
# Run benchmarking exercise

# Create ROs for benchmarking

BMLIST=""

if True; then
  BMLIST_10="1 1 5 10 20 50 100 200 500 1000"
  BMLIST_100="1 2 5 10 20 50 100 200 500"
  BMLIST_1000="1 2 5 10 20 50 100"
  BMLIST_10000="1 2 5 10 20"
else
  BMLIST_10="1 10 100"
  BMLIST_100=""
  BMLIST_1000=""
  BMLIST_10000=""
fi

echo "BMLIST_10:    ${BMLIST_10}"
echo "BMLIST_100:   ${BMLIST_100}"
echo "BMLIST_1000:  ${BMLIST_1000}"
echo "BMLIST_10000: ${BMLIST_10000}"

for NSUB in ${BMLIST_10}; do
    BMNAME="benchmark_${NSUB}_10"
    echo "Creating $BMNAME"
    rm -rf $BMNAME
    python generate-ro.py -s 10 -n $NSUB $BMNAME
    BMLIST="$BMLIST $BMNAME"
done

for NSUB in ${BMLIST_100}; do
    BMNAME="benchmark_${NSUB}_100"
    echo "Creating $BMNAME"
    rm -rf $BMNAME
    python generate-ro.py -s 100 -n $NSUB $BMNAME
    BMLIST="$BMLIST $BMNAME"
done

for NSUB in ${BMLIST_1000}; do
    BMNAME="benchmark_${NSUB}_1000"
    echo "Creating $BMNAME"
    rm -rf $BMNAME
    python generate-ro.py -s 1000 -n $NSUB $BMNAME
    BMLIST="$BMLIST $BMNAME"
done

for NSUB in ${BMLIST_10000}; do
    BMNAME="benchmark_${NSUB}_10000"
    echo "Creating $BMNAME"
    rm -rf $BMNAME
    python generate-ro.py -s 10000 -n $NSUB $BMNAME
    BMLIST="$BMLIST $BMNAME"
done

# Prepare to run benchmarks

echo "Benchmark ROs created:"         >run-benchmark.log
echo "$BMLIST"                        >>run-benchmark.log
echo "BMLIST_10:    ${BMLIST_10}"     >>run-benchmark.log
echo "BMLIST_100:   ${BMLIST_100}"    >>run-benchmark.log
echo "BMLIST_1000:  ${BMLIST_1000}"   >>run-benchmark.log
echo "BMLIST_10000: ${BMLIST_10000}"  >>run-benchmark.log

du -h .  >>run-benchmark.log

# Test RO evaluation times

for BMNAME in $BMLIST; do
    echo "----"
    echo "Starting evaluation of $BMNAME: $(date)" >>run-benchmark.log
    # ro evaluate checklist [ -d <dir> ] [ -a | -l <level> ] [ -o <format> ] <minim> <purpose> [ <target> ]
    STARTTIME=$(date +%s)
    ro eval checklist -d $BMNAME ../minim-null-checklist.rdf nothing
    ENDTIME=$(date +%s)
    echo "             completed $BMNAME: $(date)" >>run-benchmark.log
    echo "      elapsed time for $BMNAME: $((ENDTIME-STARTTIME))s" >>run-benchmark.log
    echo "$BMNAME elapsed time: $((ENDTIME-STARTTIME))s"
done

echo "All benchmarks run"  >>run-benchmark.log
echo "All benchmarks run"

# End.
