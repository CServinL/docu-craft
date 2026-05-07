"""DAG-based workflow engine for format transformations."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import networkx as nx

_STYLE_KEYS = ("css", "preamble", "doc_class", "emoji_set")


@dataclass
class TransformerEntry:
    path: str           # "module:ClassName"
    package: str        # PyPI name for error messages
    install: str        # pip install command
    priority: int = 10  # lower = preferred when multiple paths exist


class WorkflowGraph:
    """
    Directed acyclic graph where nodes are format strings and edges are
    transformers that convert one format to another.

    Formats: "md", "html", "pdf", "latex", "docx", ...
    Each edge may carry an optional engine tag for disambiguation.
    Edge weight = transformer priority; Dijkstra picks the lowest-cost path.
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
        priority: int = 10,
    ) -> None:
        from_fmt = from_fmt.lower()
        to_fmt = to_fmt.lower()
        engine = engine.lower() if engine else None
        pkg = package or module_path.split(".")[0]
        entry = TransformerEntry(
            path=module_path,
            package=pkg,
            install=install or f"pip install {pkg}",
            priority=priority,
        )
        key = (from_fmt, to_fmt, engine)
        self._entries[key] = entry
        self._graph.add_edge(from_fmt, to_fmt, engine=engine, key=key, weight=priority)

    def transformer(self, from_fmt: str, to_fmt: str, engine: str | None = None):
        """Instantiate a transformer for a direct (from, to) edge."""
        from_fmt = from_fmt.lower()
        to_fmt = to_fmt.lower()
        engine = engine.lower() if engine else None

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

    def path(self, from_fmt: str, to_fmt: str, engine: str | None = None) -> list[tuple[str, str]]:
        """
        Return (from, to) edge pairs for the preferred path from from_fmt to to_fmt.

        When engine is specified, edges tagged with that engine get a 10x weight
        reduction (strongly preferred) and edges tagged with a different engine get
        a 10x weight increase (strongly avoided). Untagged edges are neutral.
        This makes 'engine=latex' route md→pdf through md→latex→pdf automatically.
        """
        from_fmt = from_fmt.lower()
        to_fmt   = to_fmt.lower()
        eng      = engine.lower() if engine else None

        def _score(attrs: dict) -> float:
            edge_engine = attrs.get("engine")
            base = attrs.get("weight", 10)
            if eng is None:
                return base
            if edge_engine == eng:
                return base * 0.1   # strongly prefer
            if edge_engine is not None:
                return base * 10    # strongly avoid other engines
            return base             # neutral

        def weight_fn(u, v, data):
            # MultiDiGraph: data is {key: edge_attrs} — pick best scoring edge
            return min(_score(attrs) for attrs in data.values())

        nodes = nx.dijkstra_path(self._graph, from_fmt, to_fmt, weight=weight_fn)
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
        Execute the preferred workflow path, threading output through each step.
        Style options (css, preamble, doc_class, emoji_set) are only passed to
        transformers that declare applies_style = True.
        """
        style_opts = {k: v for k, v in options.items() if k in _STYLE_KEYS}
        plain_opts  = {k: v for k, v in options.items() if k not in _STYLE_KEYS}

        edges = self.path(from_fmt, to_fmt, engine)
        for src, dst in edges:
            t = self.transformer(src, dst, engine)
            step_opts = {**plain_opts, **(style_opts if t.applies_style else {})}
            content = t.transform(content, **step_opts)
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
