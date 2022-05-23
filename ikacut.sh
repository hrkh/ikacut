#!/bin/bash
set -eu

readonly url="$1"
readonly first_match_no="$2"

python3 -m ikacut download "$url" 1>&2
python3 -m ikacut match --first-match-no "$first_match_no"
