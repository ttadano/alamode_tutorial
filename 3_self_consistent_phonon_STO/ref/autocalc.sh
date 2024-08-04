#!/bin/bash

if [ -e kappa_STO.dat ]; then
rm kappa_STO.dat
fi
export OMP_NUM_THREADS=1
for ((temp=200; temp<=800; temp+=100))
do

~/src/alamode/_build2/tools/dfc2 STO222.xml STO222_scph_${temp}K.xml STO_scph2-2.scph_dfc2 ${temp}
#dfc2 STO222.xml STO222_scph_${temp}K.xml STO_scph2-2.scph_dfc2 ${temp}
cat << EOF > kappa${temp}.in
&general
 PREFIX = STO_scph_${temp}K
 MODE = RTA;
 NKD = 3; KD = Sr Ti O
 FCSXML = STO_anharm.xml
 FC2XML = STO222_scph_${temp}K.xml
 TMIN = ${temp}; TMAX = ${temp}
 NONANALYTIC = 3; BORNINFO = BORN
/
&cell
 7.363
 1.0 0.0 0.0
 0.0 1.0 0.0
 0.0 0.0 1.0
/
&kpoint
 2
 9 9 9
/
EOF
echo "Running kappa calculation at T = " $temp
mpirun -np 4 ~/src/alamode/_build2/anphon/anphon kappa${temp}.in > kappa${temp}.log
#mpirun -np 4 anphon kappa${temp}.in > kappa${temp}.log
echo "Done"
tail -n 1 STO_scph_${temp}K.kl >> kappa_STO.dat

done
