import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

import admin_methods as am
print("am.go:", am.go)
print("am.make_subplots:", am.make_subplots)
