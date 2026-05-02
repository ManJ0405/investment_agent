from .state import AgentState

__all__ = ["AgentState", "agent"]


def __getattr__(name: str):
    if name == "agent":
        from .graph import agent as _agent

        globals()["agent"] = _agent
        return _agent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
