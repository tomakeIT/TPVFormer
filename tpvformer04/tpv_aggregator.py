
import torch, torch.nn as nn, torch.nn.functional as F
from mmcv.runner import BaseModule
from mmseg.models import HEADS


@HEADS.register_module()
class TPVAggregator(BaseModule):
    def __init__(
        self, tpv_h, tpv_w, tpv_z, nbr_classes=20, 
        in_dims=64, hidden_dims=128, out_dims=None,
        scale_h=2, scale_w=2, scale_z=2, use_checkpoint=True,
        planes=['hw', 'zh', 'wz']
    ):
        super().__init__()
        self.tpv_h = tpv_h
        self.tpv_w = tpv_w
        self.tpv_z = tpv_z
        self.scale_h = scale_h
        self.scale_w = scale_w
        self.scale_z = scale_z
        self.planes = planes

        out_dims = in_dims if out_dims is None else out_dims

        self.decoder = nn.Sequential(
            nn.Linear(in_dims, hidden_dims),
            nn.Softplus(),
            nn.Linear(hidden_dims, out_dims)
        )

        self.classifier = nn.Linear(out_dims, nbr_classes)
        self.classes = nbr_classes
        self.use_checkpoint = use_checkpoint
    
    def forward(self, tpv_list, points=None):
        """
        tpv_list[0]: bs, h*w, c
        tpv_list[1]: bs, z*h, c
        tpv_list[2]: bs, w*z, c
        """

        tpv_hw = tpv_list[0]
        bs, _, c = tpv_hw.shape
        tpv_hw = tpv_hw.permute(0, 2, 1).reshape(bs, c, self.tpv_h, self.tpv_w) # bs, c, h, w

        if 'zh' in self.planes:
            tpv_zh = tpv_list[1]
            bs, _, c = tpv_zh.shape
            tpv_zh = tpv_zh.permute(0, 2, 1).reshape(bs, c, self.tpv_z, self.tpv_h) # bs, c, z, h
        else:
            tpv_zh = None

        if 'wz' in self.planes:
            # FIXME
            tpv_wz = tpv_list[1] if len(tpv_list) == 2 else tpv_list[2]
            bs, _, c = tpv_wz.shape
            tpv_wz = tpv_wz.permute(0, 2, 1).reshape(bs, c, self.tpv_w, self.tpv_z) # bs, c, w, z
        else:
            tpv_wz = None

        if self.scale_h != 1 or self.scale_w != 1:
            tpv_hw = F.interpolate(
                tpv_hw, 
                size=(self.tpv_h*self.scale_h, self.tpv_w*self.scale_w),
                mode='bilinear'
            )
        if tpv_zh is not None and (self.scale_z != 1 or self.scale_h != 1):
            tpv_zh = F.interpolate(
                tpv_zh, 
                size=(self.tpv_z*self.scale_z, self.tpv_h*self.scale_h),
                mode='bilinear'
            )
        if tpv_wz is not None and (self.scale_w != 1 or self.scale_z != 1):
            tpv_wz = F.interpolate(
                tpv_wz, 
                size=(self.tpv_w*self.scale_w, self.tpv_z*self.scale_z),
                mode='bilinear'
            )
        
        if points is not None:
            # points: bs, n, 3
            _, n, _ = points.shape
            points = points.reshape(bs, 1, n, 3)
            points[..., 0] = points[..., 0] / (self.tpv_w*self.scale_w) * 2 - 1
            points[..., 1] = points[..., 1] / (self.tpv_h*self.scale_h) * 2 - 1
            points[..., 2] = points[..., 2] / (self.tpv_z*self.scale_z) * 2 - 1
            sample_loc = points[:, :, :, [0, 1]]
            tpv_hw_pts = F.grid_sample(tpv_hw, sample_loc).squeeze(2) # bs, c, n
            if tpv_zh is not None:
                sample_loc = points[:, :, :, [1, 2]]
                tpv_zh_pts = F.grid_sample(tpv_zh, sample_loc).squeeze(2)
            if tpv_wz is not None:
                sample_loc = points[:, :, :, [2, 0]]
                tpv_wz_pts = F.grid_sample(tpv_wz, sample_loc).squeeze(2)

            tpv_hw_vox = tpv_hw.unsqueeze(-1).permute(0, 1, 3, 2, 4).expand(-1, -1, -1, -1, self.scale_z*self.tpv_z) # [bs, c, h, w, z]
            if tpv_zh is not None:
                tpv_zh_vox = tpv_zh.unsqueeze(-1).permute(0, 1, 4, 3, 2).expand(-1, -1, self.scale_w*self.tpv_w, -1, -1)
            if tpv_wz is not None:
                tpv_wz_vox = tpv_wz.unsqueeze(-1).permute(0, 1, 2, 4, 3).expand(-1, -1, -1, self.scale_h*self.tpv_h, -1)
            
        

            if tpv_zh is not None and tpv_wz is not None:
                fused_vox = (tpv_hw_vox + tpv_zh_vox + tpv_wz_vox).flatten(2) # bs, c, whz
                fused_pts = tpv_hw_pts + tpv_zh_pts + tpv_wz_pts # bs, c, n
            elif tpv_zh is not None:
                fused_vox = (tpv_hw_vox + tpv_zh_vox).flatten(2) # bs, c, whz
                fused_pts = tpv_hw_pts + tpv_zh_pts # bs, c, n
            elif tpv_wz is not None:
                fused_vox = (tpv_hw_vox + tpv_wz_vox).flatten(2) # bs, c, whz
                fused_pts = tpv_hw_pts + tpv_wz_pts # bs, c, n
            else:
                fused_vox = tpv_hw_vox.flatten(2) # bs, c, whz
                fused_pts = tpv_hw_pts # bs, c, n


            fused_pts = tpv_hw_pts  # bs, c, n
            fused = torch.cat([fused_vox, fused_pts], dim=-1) # bs, c, whz+n
            
            fused = fused.permute(0, 2, 1) # bs, whz+n, c
            if self.use_checkpoint:
                fused = torch.utils.checkpoint.checkpoint(self.decoder, fused)
                logits = torch.utils.checkpoint.checkpoint(self.classifier, fused) # bs, whz+n, classes
            else:
                fused = self.decoder(fused)
                logits = self.classifier(fused)
            logits = logits.permute(0, 2, 1)    # bs, classes, whz+n
            logits_vox = logits[:, :, :(-n)].reshape(bs, self.classes, self.scale_w*self.tpv_w, self.scale_h*self.tpv_h, self.scale_z*self.tpv_z)
            logits_pts = logits[:, :, (-n):].reshape(bs, self.classes, n, 1, 1)
            return logits_vox, logits_pts # [bs, classes, w, h, z], [bs, classes, n, 1, 1]
            
        else:
            tpv_hw = tpv_hw.unsqueeze(-1).permute(0, 1, 3, 2, 4).expand(-1, -1, -1, -1, self.scale_z*self.tpv_z)
            if tpv_zh is not None:
                tpv_zh = tpv_zh.unsqueeze(-1).permute(0, 1, 4, 3, 2).expand(-1, -1, self.scale_w*self.tpv_w, -1, -1)
            if tpv_wz is not None:
                tpv_wz = tpv_wz.unsqueeze(-1).permute(0, 1, 2, 4, 3).expand(-1, -1, -1, self.scale_h*self.tpv_h, -1)
        
            fused = tpv_hw # + tpv_zh + tpv_wz
            fused = fused.permute(0, 2, 3, 4, 1)
            if self.use_checkpoint:
                fused = torch.utils.checkpoint.checkpoint(self.decoder, fused)
                logits = torch.utils.checkpoint.checkpoint(self.classifier, fused)
            else:
                fused = self.decoder(fused)
                logits = self.classifier(fused)
            logits = logits.permute(0, 4, 1, 2, 3)
        
            return logits
