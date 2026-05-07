from docu_craft.renderers.base import BaseTransformer


class DummyTransformer(BaseTransformer):
    input_fmt = "html"
    output_fmt = "pdf"

    def transform(self, content, **options):
        return b"dummy-pdf"
