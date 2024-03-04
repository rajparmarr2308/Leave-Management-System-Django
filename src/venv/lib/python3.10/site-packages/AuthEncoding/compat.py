def b(arg):
    """Convert `arg` to bytes."""
    if isinstance(arg, str):
        arg = arg.encode("latin-1")
    return arg


def u(arg):
    """Convert `arg` to text."""
    if isinstance(arg, bytes):
        arg = arg.decode('ascii', 'replace')
    return arg
