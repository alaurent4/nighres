#!/bin/bash

# args 
#  1: Input - Absolute Path for Moving Image (Subject)
#  2: Input - Absolute Path for Fixed Image (Target)
#  3: Input - Contrast Weight
#  4: Input - Absolute Path for Moving Image 2 (Subject)
#  5: Input - Absolute Path for Fixed Image 2 (Target)
#  6: Input - Contrast Weight 2
#  7: Input - Absolute Path for Moving Image 3 (Subject)
#  8: Input - Absolute Path for Fixed Image 3 (Target)
#  9: Input - Contrast Weight 3
#  10: Input - Absolute Path for Coordinate Image (both Subject and Target)
#  11: Input - Number of Coarse Iterations
#  12: Input - Number of Medium Iterations
#  13: Input - Number of Fine Iterations
#  14: Input - Run Affine Step Before Registration
#  15: Output - Absolute Path for Registration Result (Deform Subject)
#  16: Output - Absolute Path for Registration Result 2 (Deform Subject)
#  17: Output - Absolute Path for Registration Result 3 (Deform Subject)
#  18: Output - Absolute Path for Forward Mapping (Subject to Target)
#  19: Output - Absolute Path for Inverse Mapping (Target to Subject)
#  20: Output - Absolute Path for working directory

moving="$1"
fixed="$2"
weight="$3"
moving2="$4"
fixed2="$5"
weight2="$6"
moving3="$7"
fixed3="$8"
weight3="$9"
coord="${10}"
coarseItr="${11}"
mediumItr="${12}"
fineItr="${13}"
affineFirst="${14}"
outResult="${15}"
outResult2="${16}"
outResult3="${17}"
outMap="${18}"
outInvMap="${19}"
destdir="${20}"

output="$destdir/syn.nii"
synWarp="$destdir/synWarp.nii"
synInverseWarp="$destdir/synInverseWarp.nii"
synAffine="$destdir/synAffine.txt"

# Perform affine registration first
if [ "$affineFirst" == "true" ]
then
		offAffineTag=""
else
    offAffineTag="--number-of-affine-iterations 0"
fi

metricTag="-m CC[$fixed,$moving,$weight,2]"
metricTag2="-m CC[$fixed2,$moving2,$weight2,2]"
metricTag3="-m CC[$fixed3,$moving3,$weight3,2]"	

interpTag=""

# Calls ANTS
ANTS 3 $metricTag $metricTag2 $metricTag3 -o $output -i $coarseItr"x"$mediumItr"x"$fineItr -r Gauss[3,3] -t SyN[.25] $offAffineTag --use-all-metrics-for-convergence

# Transform the moving images
WarpImageMultiTransform 3 $moving $outResult -R $fixed $interpTag $synWarp $synAffine
WarpImageMultiTransform 3 $moving2 $outResult2 -R $fixed2 $interpTag $synWarp $synAffine
WarpImageMultiTransform 3 $moving3 $outResult3 -R $fixed3 $interpTag $synWarp $synAffine

# Transform the moving coordinates image
WarpTimeSeriesImageMultiTransform 4 $coord $outMap -R $fixed $synWarp $synAffine

# Transform the fixed coordinates image
WarpTimeSeriesImageMultiTransform 4 $coord $outInvMap -R $moving -i $synAffine $synInverseWarp

# delete temp files
rm -f $synAffine
rm -f $synWarp
rm -f $synInverseWarp

