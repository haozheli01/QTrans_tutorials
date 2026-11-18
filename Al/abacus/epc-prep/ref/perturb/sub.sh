#!/bin/bash

for i in {0..3}
do
    idx=$(printf "%01d" $i)
    mkdir ${i}
    cd ${i}
    mv ../QTepc-${idx}.dat ./STRU
    cp ../sub_abacus.sh ./
    cp ../INPUT ./
    cp ../KPT ./
    sbatch sub_abacus.sh
    cd ..
done

