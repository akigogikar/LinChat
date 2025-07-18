from html.parser import HTMLParser
import re

class _BS(HTMLParser):
    def __init__(self, text, parser):
        super().__init__()
        self.html = text
        self._texts = []
        self.feed(text)
    def handle_data(self, data):
        self._texts.append(data)
    def __call__(self, tags):
        return []
    def find_all(self, tag):
        return []
    def select(self, selector):
        if selector == "a.result__a":
            return [dict(href=m.group(1)) for m in re.finditer(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"', self.html)]
        return []
    def get_text(self, separator="", strip=False):
        if strip:
            return separator.join(t.strip() for t in self._texts)
        return separator.join(self._texts)
    def decompose(self):
        pass

BeautifulSoup = _BS
