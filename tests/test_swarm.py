import inspect


def test_docstrings():
    # Test that all functions and classes have docstrings
    import swarm.swarm as swarm
    for name, obj in inspect.getmembers(swarm):
        if inspect.isclass(obj) or inspect.isfunction(obj):
            assert obj.__doc__ is not None, f"{name} has no docstring"

