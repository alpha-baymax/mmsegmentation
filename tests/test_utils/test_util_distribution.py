# Copyright (c) OpenMMLab. All rights reserved.
from unittest.mock import MagicMock, patch

import torch.nn as nn
from mmcv.device.mlu import MLUDataParallel, MLUDistributedDataParallel
from mmcv.parallel import (MMDataParallel, MMDistributedDataParallel,
                           is_module_wrapper)
from mmcv.utils import IS_CUDA_AVAILABLE, IS_MLU_AVAILABLE

from mmseg.utils import build_ddp, build_dp


def mock(*args, **kwargs):
    pass


class Model(nn.Module):

    def __init__(self):
        super().__init__()
        self.conv = nn.Conv2d(2, 2, 1)

    def forward(self, x):
        return self.conv(x)


@patch('torch.distributed._broadcast_coalesced', mock)
@patch('torch.distributed.broadcast', mock)
@patch('torch.nn.parallel.DistributedDataParallel._ddp_init_helper', mock)
def test_build_dp():
    model = Model()
    assert not is_module_wrapper(model)

    mmdp = build_dp(model, 'cpu')
    assert isinstance(mmdp, MMDataParallel)

    if IS_CUDA_AVAILABLE:
        mmdp = build_dp(model, 'cuda')
        assert isinstance(mmdp, MMDataParallel)

    if IS_MLU_AVAILABLE:
        mludp = build_dp(model, 'mlu')
        assert isinstance(mludp, MLUDataParallel)


@patch('torch.distributed._broadcast_coalesced', mock)
@patch('torch.distributed.broadcast', mock)
@patch('torch.nn.parallel.DistributedDataParallel._ddp_init_helper', mock)
def test_build_ddp():
    model = Model()
    assert not is_module_wrapper(model)

    if IS_CUDA_AVAILABLE:
        mmddp = build_ddp(
            model, 'cuda', device_id=[0], process_group=MagicMock())
        assert isinstance(mmddp, MMDistributedDataParallel)

    if IS_MLU_AVAILABLE:
        mluddp = build_ddp(
            model, 'mlu', device_ids=[0], process_group=MagicMock())
        assert isinstance(mluddp, MLUDistributedDataParallel)
