import prosconductor


def upgrade_project(kernel, projectdirectory, dropins):
    kerneldir = prosconductor.resolve.find_kernel_template(kernel)
    loader = prosconductor.loader.KernelLoader()
    loader.upgrade_project(kernelpath=kerneldir, projectpath=projectdirectory, dropins=dropins)
