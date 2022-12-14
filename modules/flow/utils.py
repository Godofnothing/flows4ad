import torch
import torch.distributions as dist

from .glow import Glow
from .real_nvp import RealNVP
from .planar import PlanarFlow
from .maf import MAF

flow_name_to_class = {
    'real_nvp': RealNVP,
    'glow': Glow,
    'planar': PlanarFlow,
    'maf': MAF
}


def get_flow_class(flow_name):
    return flow_name_to_class[flow_name]


def get_flow_instace(flow_config):
    flow_class = get_flow_class(flow_config.flow_name)
    return flow_class(flow_config)


def get_detector_prior(config=None):
    prior = dist.Normal(loc=0.0, scale=1.0)
    return prior
