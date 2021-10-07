#!/bin/bash

images=$(identify -format '%f\n' * 2>/dev/null)

IFS=$'\n'
set -e

max_dims=$(
  identify -format '%w %h\n' $images 2>/dev/null |
  awk '($1>w){w=$1} ($2>h){h=$2} END{print w"x"h}'
  )

orig_dir=originals_$(date +%Y-%m-%d_%T)
mkdir "$orig_dir"
mv -- $images "$orig_dir"
cd "$orig_dir"

set +e

for image in $images; do
  convert -- "$image" -gravity Center -extent "$max_dims" "../$image"
done