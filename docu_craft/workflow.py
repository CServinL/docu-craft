"""DAG-based workflow engine for format transformations."""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import networkx as nx


@dataclass
class TransformerEntry:
    path: str           # "module:ClassName"
    package: str        # PyPI name for error messages
    install: str        # pip install command


class WorkflowGraph:
    """
    Directed acyclic graph where nodes are format strings and edges are
    transformers that convert one format to another.

    Formats are free-form strings: "md", "html", "pdf", "latex", "docx", ...
    Each edge may carry an optional engine tag for disambiguation when multiple
    transformers exist for the same (from, to) pair.
    """

    def __init__(self) -> None:
        self._graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self._entries: dict[tuple[str, str, str | None], TransformerEntry] = {}

    def register(
        self,
        from_fmt: str,
        to_fmt: str,
        module_path: str,
        engine: str | None = None,
        package: str | None = None,
        install: str | None = None,
    ) -> None:
        """Add a transformer edge to the graph."""
        from_fmt = from_fmt.lower()
        to_fmt = to_fmt.lower()
        engine = engine.lower() if engine else None
        pkg = package or module_path.split(".")[0]
        entry = TransformerEntry(
            path=module_path,
            package=pkg,
            install=install or f"pip install {pkg}",
        )
        key = (from_fmt, to_fmt, engine)
        self._entries[key] = entry
        self._graph.add_edge(from_fmt, to_fmt, engine=engine, key=key)

    def transformer(
        self, from_fmt: str, to_fmt: str, engine: str | None = None
    ):
        """Instantiate and return a transformer for a direct edge."""
        from_fmt = from_fmt.lower()
        to_fmt = to_fmt.lower()
        engine = engine.lower() if engine else None

        # Prefer exact engine match, fall back to None engine
        key = (from_fmt, to_fmt, engine)
        entry = self._entries.get(key) or self._entries.get((from_fmt, to_fmt, None))
        if entry is None:
            raise ValueError(
                f"No transformer registered for {from_fmt!r} → {to_fmt!r}"
                + (f" engine={engine!r}" if engine else "")
            )
        mod_name, cls_name = entry.path.rsplit(":", 1)
        try:
            mod = importlib.import_module(mod_name)
        except ImportError:
            raise ImportError(
                f"Transformer '{entry.path}' requires '{entry.package}' which is not installed.\n"
                f"Install it with:  {entry.install}"
            ) from None
        return getattr(mod, cls_name)()

    def path(
        self, from_fmt: str, to_fmt: str, engine: str | None = None
    ) -> list[tuple[str, str]]:
        """
        Return the list of (from, to) edge pairs forming the shortest path
        from from_fmt to to_fmt.  Raises nx.NetworkXNoPath if unreachable.
        """
        from_fmt = from_fmt.lower()
        to_fmt = to_fmt.lower()
        nodes = nx.shortest_path(self._graph, from_fmt, to_fmt)
        return list(zip(nodes, nodes[1:]))

    def run(
        self,
        content: Any,
        from_fmt: str,
        to_fmt: str,
        engine: str | None = None,
        **options,
    ) -> Any:
        """
        Execute the shortest workflow path from from_fmt to to_fmt, threading
        the output of each step into the input of the next.
        """
        edges = self.path(from_fmt, to_fmt, engine)
        for src, dst in edges:
            t = self.transformer(src, dst, engine)
            content = t.transform(content, **options)
        return content

    def formats(self) -> set[str]:
        return set(self._graph.nodes)

    def edges(self) -> list[tuple[str, str, str | None]]:
        return [
            (u, v, data.get("engine"))
            for u, v, data in self._graph.edges(data=True)
        ]


# Global singleton
graph = WorkflowGraph()
