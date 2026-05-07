from docify.skeletons import Skeleton


class SimpleSkeleton(Skeleton):
    name = "SimpleSkeleton"
    sections = [
        {"heading": "Introducción", "required": True},
        {"heading": "Conclusiones", "required": True},
    ]
