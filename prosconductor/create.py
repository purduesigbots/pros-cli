import prosconductor


def create_project(kernel, projectdirectory, dropins):
    kerneldir = prosconductor.loader.find_kernel_template(kernel)
    loader = prosconductor.loader.KernelLoader()
    loader.create_project(kernelpath=kerneldir, projectpath=projectdirectory, dropins=dropins)
