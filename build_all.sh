#!/bin/sh
# Rebuild the whole series, 4 books at a time:
#   * 4 regular volumes from ONE series plan, so no scene repeats anywhere
#   * a Christmas book (Christmas subjects only)
#   * a Thanksgiving book (Thanksgiving subjects only)
# then verify every PDF.
cd "$(dirname "$0")"
mkdir -p output
COMMON="--single-sided --min-dots 1000 --max-dots 2000 --solutions-per-page 4"

{
for v in 1 2 3 4; do
  echo "python3 build_book.py $COMMON --volumes 4 --volume $v --series-seed 7 --seed ${v}0${v} --puzzles 100 \
--title 'Extreme Dot-to-Dot for Adults Vol. $v' --subtitle '100 unique scenes, 1,000 to 2,000 dots each' \
--out output/extreme_dot_to_dot_vol$v.pdf > output/build_vol$v.log 2>&1"
done
echo "python3 build_book.py $COMMON --theme christmas --series-seed 1225 --seed 1225 --puzzles 50 \
--title 'Christmas Extreme Dot-to-Dot for Adults' --subtitle '50 unique Christmas scenes, 1,000 to 2,000 dots each' \
--out output/christmas_dot_to_dot.pdf > output/build_christmas.log 2>&1"
echo "python3 build_book.py $COMMON --theme thanksgiving --series-seed 1127 --seed 1127 --puzzles 50 \
--title 'Thanksgiving Extreme Dot-to-Dot for Adults' --subtitle '50 unique Thanksgiving scenes, 1,000 to 2,000 dots each' \
--out output/thanksgiving_dot_to_dot.pdf > output/build_thanksgiving.log 2>&1"
} | xargs -d "\n" -P 4 -n 1 sh -c

python3 verify_book.py output/extreme_dot_to_dot_vol*.pdf output/christmas_dot_to_dot.pdf output/thanksgiving_dot_to_dot.pdf \
  > output/verify_report.txt 2>&1
echo "verify exit code: $?" >> output/verify_report.txt
tail -n 30 output/verify_report.txt
