import prosconductor


def command(args):
    print(args.verbose)
    print(prosconductor.fetch.suggest_update_site())
