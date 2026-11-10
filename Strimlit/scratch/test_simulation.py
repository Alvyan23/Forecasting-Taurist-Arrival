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

class MockContainer:
    def __enter__(self): return self
    def __exit__(self, *args): pass

class MockExpander:
    def __init__(self, title, expanded=False):
        self.title = title
    def __enter__(self): return self
    def __exit__(self, *args): pass

charts_shown = []
dfs_shown = []

class MockSt:
    def container(self, **kw): return MockContainer()
    def expander(self, title, expanded=False): return MockExpander(title, expanded)
    def columns(self, n, **kw): return [MockContainer() for _ in range(n if isinstance(n, int) else len(n))]
    def write(self, *a, **kw): pass
    def markdown(self, *a, **kw): pass
    def caption(self, *a, **kw): pass
    def error(self, *a, **kw): print("ERROR:", a)
    def warning(self, *a, **kw): print("WARN:", a)
    def info(self, *a, **kw): pass
    def selectbox(self, label, options, **kw): return options[0]
    def plotly_chart(self, fig, **kw):
        charts_shown.append(fig)
    def dataframe(self, df, **kw):
        dfs_shown.append(df)

am.st = MockSt()

for met in ["Hybrid VMD-GRU", "Hybrid ICEEMDAN-VMD-GRU"]:
    for dest in ["Gunung geger", "Kolla Langgundi"]:
        print(f"\nTesting {met} -> {dest}")
        charts_shown.clear()
        dfs_shown.clear()
        h = am._cari_benchmark(met, dest)
        h["metode"] = met
        am.render_tahap_praproses(h, "Dekomposisi VMD", "test_kp", raw_df=None)
        print(f"  Charts shown: {len(charts_shown)}")
        print(f"  Dataframes shown: {len(dfs_shown)}")
        assert len(charts_shown) > 0, "No charts shown for Dekomposisi VMD!"
        assert len(dfs_shown) > 0, "No dataframes shown for Dekomposisi VMD!"
        print(f"  First df columns: {list(dfs_shown[0].columns)}")
        print(f"  First df rows:\n{dfs_shown[0]}")

print("\nSimulation test passed successfully with plotly mocked!")
