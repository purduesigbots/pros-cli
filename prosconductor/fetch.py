def suggest_update_site():
    return "https://raw.githubusercontent.com/purduesigbots/purdueros-kernels/master"


local_kernel_repository_path = None
def get_local_kernel_repository_path():
    if local_kernel_repository_path is not None:
        return local_kernel_repository_path
    return "hello"
