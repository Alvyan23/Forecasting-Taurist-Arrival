import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))
import forecasting_engine as fe

print("Benchmarks keys:", list(fe.BENCHMARKS.keys()))
for k, v in fe.BENCHMARKS.items():
    print(k, "-> mae:", v.get("mae"), "mape:", v.get("mape"), "rmse:", v.get("rmse"))
