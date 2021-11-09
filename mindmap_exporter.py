import xml.etree.ElementTree as xml


class MindmapExporter:
    def export(self, tree: xml.Element) -> None:
        raise NotImplementedError("Should have implemented this")
