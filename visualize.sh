python visualization/vis_frame.py \
    --py-config ./config/tpv04_occupancy.py \
    --work-dir ./out/tpv_occupancy_hw \
    --ckpt-path ./out/tpv_occupancy_hw/tpv04_occupancy_v2.pth \
    --save-path ./out/tpv_occupancy_hw/frames \
    --frame-idx 4500 \
    --mode 2


# "--mode" to determine what to visualize: 0 for occupancy prediction, 
# 1 for lidar segmentation prediction, 
# 2 for lidar segmentation ground truth.