import json

class Shape:
    def __init__(self):
        self.text = ""

class SlideShapes(list):
    def __init__(self):
        super().__init__()
        self.title = Shape()
        self.append(self.title)

class Slide:
    def __init__(self):
        self.shapes = SlideShapes()

class Slides(list):
    def add_slide(self, layout):
        slide = Slide()
        self.append(slide)
        return slide

class Presentation:
    def __init__(self, path=None):
        self.slides = Slides()
        self.slide_layouts = [None]
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for title in data:
                    slide = self.slides.add_slide(None)
                    slide.shapes.title.text = title
            except FileNotFoundError:
                pass

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([s.shapes.title.text for s in self.slides], f)
