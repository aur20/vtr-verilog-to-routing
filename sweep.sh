#!/bin/bash

mkdir -p temp
cd temp
echo "Operating in directory: ${PWD}"

VTR_ROOT=/path/to/vtr
GNL_ROOT=/path/to/GNL-Generate-Netlist

NET_DIR=nets
VPR_DIR=vprs
ARCH_PATH="${VTR_ROOT}/vtr_flow/arch/hes"
ARCH_NAME=raveena.xml
# Number of blocks to use in the benchmark
L_NB=(50 100 200 400 500)
# Distribution of blocks to use in the benchmark
D_NB=(0.2 0.2 0.2 0.2 0.1 0.1) # 20% latches, 20% inv, 20% and2, 20% nand3, 10% or4, 10% xor2

GNL_RUN=off
VPR_RUN=on
VPR_CONF="markus" #"both" # "default" "markus"
NRUN=3
NPROC=12

if [ "$GNL_RUN" == "on" ]; then
    if [ ! -d "$GNL_ROOT" ]; then
        echo "GNL path does not exist"
        exit 1
    fi
    # Build GNL
    pw=$PWD
    mkdir -p $GNL_ROOT/build
    cd $GNL_ROOT/build
    cmake ..
    make
    cd "$pw"
    # Generate GNL files
    mkdir -p $NET_DIR
    cd $NET_DIR
    for NB in "${L_NB[@]}"; do
        FILENAME="${NB}.gnl"
        echo "Generating $FILENAME with NB=$NB blocks"
        result0=$(awk "BEGIN {print $NB * ${D_NB[0]}}")
        result1=$(awk "BEGIN {print $NB * ${D_NB[1]}}")
        result2=$(awk "BEGIN {print $NB * ${D_NB[2]}}")
        result3=$(awk "BEGIN {print $NB * ${D_NB[3]}}")
        result4=$(awk "BEGIN {print $NB * ${D_NB[4]}}")
        result5=$(awk "BEGIN {print $NB * ${D_NB[5]}}")
        cat > $FILENAME <<EOL
[library]
name=lib
latch=latch   1 1
gate=inv    1 1
gate=and2   2 1
gate=nand3  3 1
gate=or4    4 1
gate=xor2   2 1

[circuit]
name=$NB
libraries=lib

distribution=$result0 $result1 $result2 $result3 $result4 $result5
size=$NB
p=0.50
sigmaG=0
sigmaT=0
EOL
        # Generate BLIF file from GNL
        $GNL_ROOT/build/gnl -w blif $FILENAME -sp
    done
    cd ..
fi

enumerate_folders() {
    prefix="$1"  # Prefix for folders (e.g., original, new)
    description="$2"  # Additional text in folder names
    dir="$3"  # Target directory

    # Find the highest index for folders matching the prefix and description
    max_index=$(find "$dir" -mindepth 1 -maxdepth 1 -type d -name "${prefix}_${description}_*" \
        | sed -E "s|.*/${prefix}_${description}_||" \
        | grep -E '^[0-9]+$' \
        | sort -n \
        | tail -n 1)

    # Default to 0 if no matching folders are found
    max_index=${max_index:-0}
    echo $((max_index + 1))
}

if [ "$VPR_RUN" == "on" ]; then
    if [ ! -d "$VTR_ROOT" ]; then
        echo "VTR path does not exist"
        exit 1
    fi

    if [ "$VPR_CONF" == "original" ] || [ "$VPR_CONF" == "both" ]; then
        pw=$PWD
        cd $VTR_ROOT
        make CMAKE_PARAMS="-DMARKUS_AT_WORK=off" -j$NPROC vpr
        cd "$pw"

        mkdir -p $VPR_DIR
        for RUN in $(seq 0 $NRUN); do
            for NB in "${L_NB[@]}"; do
                description="${NB}_${ARCH_NAME%.*}"  # Customize this as needed
                folder_index=$(enumerate_folders "original" "$description" "$VPR_DIR")
                PATHNAME="${VPR_DIR}/original_${description}_${folder_index}"
                mkdir -p "$PATHNAME"
                cd "$PATHNAME"
                echo "Running VPR for NB=$NB"
                $VTR_ROOT/vpr/vpr $ARCH_PATH/$ARCH_NAME ../../$NET_DIR/${NB}.blif --route_chan_width 20 --inner_loop_recompute_divider 1 --save_graphics on --graphics_commands "set_cpd 1; save_graphics cpd1.png;" --seed $NB$RUN --write_timing_summary timing_summary.json -j$NPROC --pack --place --write_initial_place_file initial.place --post_place_timing_report timing_post_place.rpt > "vpr_output.log" 2>&1
                cd "$pw"
            done
        done
    fi

    if [ "$VPR_CONF" == "stroobandt" ] || [ "$VPR_CONF" == "both" ]; then
        pw=$PWD
        cd $VTR_ROOT
        make CMAKE_PARAMS="-DMARKUS_AT_WORK=1" -j$NPROC vpr
        cd "$pw"

        mkdir -p $VPR_DIR
        for RUN in $(seq 0 $NRUN); do
            for NB in "${L_NB[@]}"; do
                description="${NB}_${ARCH_NAME%.*}"  # Customize this as needed
                folder_index=$(enumerate_folders "stroobandt" "$description" "$VPR_DIR")
                PATHNAME="${VPR_DIR}/stroobandt_${description}_${folder_index}"
                mkdir -p "$PATHNAME"
                cd "$PATHNAME"
                echo "Running VPR for NB=$NB"
                $VTR_ROOT/vpr/vpr $ARCH_PATH/$ARCH_NAME ../../$NET_DIR/${NB}.blif --route_chan_width 20 --inner_loop_recompute_divider 1 --save_graphics on --graphics_commands "set_cpd 1; save_graphics cpd1.png;" --seed $NB$RUN --write_timing_summary timing_summary.json -j$NPROC --pack --place --write_initial_place_file initial.place --post_place_timing_report timing_post_place.rpt > "vpr_output.log" 2>&1
                cd "$pw"
            done
        done
    fi
fi