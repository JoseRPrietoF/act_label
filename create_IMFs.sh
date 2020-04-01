#!/usr/bin/env bash
volumes=( 35 36 37 38 41 45 46 47 48 49 50 51 52 53 54A 58 60 61 62 )
for vol in "${volumes[@]}"; do
  python3.6 create_IMF.py "JJ0"${vol}
done

