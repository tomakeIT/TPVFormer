# N-Perspective View: Ablation Study on Tri-Perspective View on Plane Configurations

## Overview
This project explores the impact of plane configurations in the **Tri-Perspective View (TPV)** representation for **3D semantic occupancy prediction**. Using the TPVFormer architecture, we conduct an **ablation study** to evaluate different plane combinations on the Panoptic nuScenes dataset. The results reveal that two-plane configurations outperform the original three-plane setup, shedding light on the trade-off between feature completeness and simplicity.

---

## Key Features
- **Ablation Study**: Investigates the performance of 3D semantic prediction using different TPV configurations: single-plane, two-plane, and three-plane setups.
- **Quantitative Analysis**: Measures performance using mIoU and IoU metrics across various plane combinations.
- **Visualization**: Provides detailed visual comparisons of 3D semantic occupancy predictions.
- **Optimized Configurations**: Demonstrates that two-plane setups outperform traditional three-plane TPV, offering insights for simplified yet effective 3D scene representation.

---

## Methodologies
1. **TPV Representation**:
   - Extends Bird's Eye View (BEV) with three orthogonal planes: $HW$, $DH$, and $WD$.
   - Encodes 3D spatial features more comprehensively than BEV.

2. **Plane Configurations**:
   - **Single Plane**: $HW$ only (equivalent to BEV).
   - **Two Planes**: $HW+DH$, $HW+WD$.
   - **Three Planes**: Original TPV configuration with $HW$, $DH$, and $WD$.

3. **Task**: Semantic Occupancy Prediction (SOP) on the **Panoptic nuScenes dataset**.

4. **Evaluation Metrics**:
   - mIoU (mean Intersection over Union)
   - Per-class IoU

---

## Results
| **Configuration** | **mIoU (%)** |
|-------------------|--------------|
| Original TPV      | 40.2         |
| $HW$ Only (BEV)   | 33.5         |
| $HW+DH$           | 47.9         |
| $HW+WD$           | 48.8         |

- Two-plane configurations **($HW+DH$, $HW+WD$)** achieved better performance than the original three-plane TPV setup, likely due to reduced feature redundancy.

---

## Case Study
- **Visualization**:
  - Top-view and isometric-view results demonstrate the significant improvement in 3D semantic occupancy predictions when adding vertical planes ($DH$ or $WD$) to the BEV ($HW$) configuration.

---

## Dependencies
- LaTeX IEEEtran Class (`IEEEtran.cls`)
- Packages: `amsmath`, `graphicx`, `booktabs`, `xcolor`, `adjustbox`, `tcolorbox`, `rotating`

---

## How to Use
1. **Clone Repository**:
   ```bash
   git clone https://github.com/[username]/tpv-ablation-study.git
   ```
2. **Compile the Paper**:
   - Open `main.tex` in your LaTeX editor (e.g., Overleaf or TeXShop).
   - Compile using **PDFLaTeX**.

3. **Run Experiments**:
   - Refer to the `code/` directory for scripts used in TPV ablation experiments.
   - Modify configurations in `config.yaml` to test specific setups.

4. **Visualize Results**:
   - Use the provided visualization scripts in `visualization/` to reproduce figures from the paper.

---

## Future Work
- Extend experiments to **3D object detection** and **segmentation** tasks.
- Analyze feature distributions in different plane configurations to better understand performance differences.
- Investigate generalization of findings to other datasets and architectures.

---

## Authors
- **Erdao Liang** (University of Michigan, Ann Arbor) - [Email](mailto:erdao@umich.edu)
- **Jialeng Ni** (University of Michigan, Ann Arbor) - [Email](mailto:jialeng@umich.edu)
- **Jiyang Wang** (University of Michigan, Ann Arbor) - [Email](mailto:realwjy@umich.edu)

---

## Citation
If you find this work useful, please cite:
```bibtex
@article{,
  title={N-Perspective View: Ablation Study on Tri-Perspective View on Plane Configurations},
  author={Liang, Erdao and Ni, Jialeng and Wang, Jiyang},
  journal={},
  year={2024},
  publisher={}
}
```

---

## License
This project is licensed under the MIT License. See `LICENSE` for details.
