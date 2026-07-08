# TODO

## Analyze using Marker for pdf → md

Marker (`marker-pdf`) does deep-learning-based layout detection for PDF
extraction — likely better table/heading fidelity than the current
`pdf_md.py` (PyMuPDF font-size heuristics). Would slot in as a second
`pdf → md` edge, disambiguated via `engine="marker"`, same pattern already
used for `html → pdf` (weasyprint vs reportlab).

Open question before building it: Marker pulls in a full deep-learning
stack (torch + downloaded model weights) — much heavier than PyMuPDF's pure
heuristic, and slower per page on CPU. Needs to stay strictly opt-in
(`engine="marker"`, never the default edge, own `[marker]` extra kept out
of `[all]`) rather than something that silently fattens every install.
Decide whether the fidelity gain is actually worth that weight for real
use cases before scaffolding it.

Note: table fidelity specifically is now partially addressed without Marker
— `pdf_md.py` gained PyMuPDF `find_tables()`-based table detection (`text`
strategy, catches borderless/booktabs-style tables too), rendering real
`|pipe|table|` markdown instead of flattening rows into prose. Re-evaluate
whether Marker's fidelity gain is still worth its weight given that.
