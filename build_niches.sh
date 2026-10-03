#!/bin/sh
# Build 50-puzzle niche books, 4 at a time, then verify them together with
# every other book in output/ (so scenes are checked across ALL books).
#   ./build_niches.sh                 # every niche whose art is ready
#   ./build_niches.sh ocean cats ...  # just these niches
cd "$(dirname "$0")"
mkdir -p output
if [ $# -eq 0 ]; then
  set -- $(python3 -c "from dotdot import niches; print(' '.join(niches.ready()))")
fi
COMMON="--single-sided --min-dots 1000 --max-dots 2000 --solutions-per-page 4"
for slug in "$@"; do
  echo "python3 build_book.py $COMMON --niche $slug --seed $(printf '%s' "$slug" | cksum | cut -d' ' -f1) \
--out output/niche_$slug.pdf > output/build_niche_$slug.log 2>&1"
done | xargs -d "\n" -P 4 -n 1 sh -c

python3 verify_book.py output/extreme_dot_to_dot_vol*.pdf output/christmas_dot_to_dot.pdf \
  output/thanksgiving_dot_to_dot.pdf output/niche_*.pdf > output/verify_report.txt 2>&1
echo "verify exit code: $?" >> output/verify_report.txt
tail -n 5 output/verify_report.txt
