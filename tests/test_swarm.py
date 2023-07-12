import inspect


def test_docstrings():
    # Test that all functions and classes have docstrings
    import swarm.swarm as swarm
    for name, obj in inspect.getmembers(swarm):
        if inspect.isclass(obj) or inspect.isfunction(obj):
            assert obj.__doc__ is not None, f"{name} has no docstring"

def test_return_parameters():
    # Test that all functions have return parameters
    import swarm.swarm as swarm
    for name, obj in inspect.getmembers(swarm):
        if inspect.isfunction(obj):
            assert obj.__annotations__.get("return") is not None, f"{name} has no return parameter"
        elif inspect.isclass(obj):
            for cname, cobj in inspect.getmembers(obj):
                if inspect.isfunction(cobj):
                    assert cobj.__annotations__.get("return") is not None, f"{name}.{cname} has no return parameter"
