import os

from prosconductor import loader, config, resolve


def get_available_dropins(kernel):
    """
    Gets a list of available dropins in the form of a dictionary where the key is the dropin and the value is binary
    number indicating if the dropin is available from the kernel (1 << 0) or universal repository (1 << 1)
    :param kernel: A valid kernel string - takes the first result of prosconductor.resolve.resolve_kernel_reques
    """
    kernel_path = loader.find_kernel_template(resolve.resolve_kernel_request(kernel)[0])
    dropins = loader.find_loader(kernel_path).list_local_dropins(kernelpath=kernel_path)
    dropins = dict(zip(dropins, [1 << 0] * len(dropins)))
    for drop in get_global_dropins():
        dropins[drop] = dropins.get(drop, 0) | 1 << 1
    return dropins


def get_global_dropins():
    return os.listdir(config.dropin_repo)
