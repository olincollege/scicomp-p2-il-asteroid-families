# first line: 715
def _single_linkage(*args, **kwargs):
    kwargs["linkage"] = "single"
    return linkage_tree(*args, **kwargs)
