import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from unittest.mock import MagicMock
import admin_methods as am

# Mock plotly
mock_fig = MagicMock()
mock_go = MagicMock()
mock_make_subplots = MagicMock(return_value=mock_fig)
am.go = mock_go
am.make_subplots = mock_make_subplots

headers_shown = []
class MockContainer:
    def __enter__(self): return self
    def __exit__(self, *args): pass

class MockExpander:
    def __init__(self, title, expanded=False):
        self.title = title
    def __enter__(self): return self
    def __exit__(self, *args): pass

class MockSt:
    session_state = {}
    def container(self, **kw): return MockContainer()
    def expander(self, title, expanded=False): return MockExpander(title, expanded)
    def columns(self, n, **kw): return [MockContainer() for _ in range(n if isinstance(n, int) else len(n))]
    def write(self, *a, **kw): pass
    def markdown(self, text, *a, **kw):
        headers_shown.append(text)
    def caption(self, *a, **kw): pass
    def error(self, *a, **kw): pass
    def warning(self, *a, **kw): pass
    def info(self, *a, **kw): pass
    def selectbox(self, label, options, **kw): return "Evaluasi & Prediksi"
    def radio(self, label, options, **kw): return "Evaluasi & Prediksi"
    def pills(self, label, options, **kw): return "Evaluasi & Prediksi"
    def plotly_chart(self, fig, **kw): pass
    def dataframe(self, df, **kw): pass

am.st = MockSt()

h = am._cari_benchmark("Hybrid ICEEMDAN-VMD-GRU", "Gunung geger")
h["metode"] = "Hybrid ICEEMDAN-VMD-GRU"

headers_shown.clear()
am.render_hasil_admin(h)

print("Headers rendered in render_hasil_admin:")
for h_text in headers_shown:
    if "ct" in h_text:
        print(" ", h_text)

assert not any("Ringkasan Evaluasi Seperti Notebook" in text for text in headers_shown), "Notebook summary still appears!"
print("\nEvaluation test passed: Notebook summary is completely removed!")
