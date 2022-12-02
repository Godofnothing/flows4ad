import os

import torch
import torch.optim as optim

from visualisation import visualise_prediction_histograms, set_visualisation_options
from execution import engine
from modules import *


def get_optimizer(model, config):
    optimizer = optim.AdamW(model.parameters(), lr=config.lr, weight_decay=config.weight_decay)
    return optimizer


def get_scheduler(optimizer, config):
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.num_epochs, eta_min=config.min_lr)
    return scheduler


def save_model(model, config):
    torch.save(model.state_dict(), os.path.join(config.output_dir, 'model.pth'))


def collect_predictions(model, prior, dataloader, device):
    log_probs = []
    with torch.no_grad():
        for (x,) in dataloader:
            z, log_det = model(x.to(device), reverse=True)
            log_prob = prior.log_prob(z) + log_det
            log_probs.append(log_prob.sum(dim=-1).cpu())
    
    log_probs = torch.cat(log_probs, dim=0).numpy()
    return log_probs


def setup_before_experiment(environment, config):
    model, prior, loss, device, dataloaders, optimizer, scheduler = environment
    # maybe something else
    
    if config.output_dir:
        os.makedirs(config.output_dir, exist_ok=True)


def teardown_after_experiment(environment, config):
    model, prior, loss, device, dataloaders, optimizer, scheduler = environment
    # maybe something else
    
    # save model
    if config.save_model:
        assert config.output_dir is not None
        save_model(model, config)
    
    # plot id/ood histogram
    if config.plot_histogram:
        assert config.output_dir is not None

        predictions = {}
        for domain_name in ['in', 'out']:
            dataloader = dataloaders[domain_name]
            log_probs = collect_predictions(model, prior, dataloader, device)
            predictions[domain_name] = log_probs

        set_visualisation_options(config)
        visualise_prediction_histograms(predictions, config)


def run_experiment(environment, config):
    model, prior, loss, device, dataloaders, optimizer, scheduler = environment

    results = engine.train(
        model, dataloaders['in'], dataloaders['out'],
        epochs=config.num_epochs,
        optimizer=optimizer,
        scheduler=scheduler,
        loss_fn=loss,
        device=device,
        log_frequency=config.log_frequency,
        log_wandb=config.log_wandb
    )

    return results
        