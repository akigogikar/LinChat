import json

class Paragraph:
    def __init__(self, text=""):
        self.text = text

class Document:
    def __init__(self, path=None):
        self.paragraphs = []
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.paragraphs = [Paragraph(t) for t in data]
            except FileNotFoundError:
                pass

    def add_paragraph(self, text):
        p = Paragraph(text)
        self.paragraphs.append(p)
        return p

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([p.text for p in self.paragraphs], f)
