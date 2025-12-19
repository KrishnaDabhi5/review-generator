import traceback
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "nlp"))

print("Starting precompute (debug)")
try:
    import precompute_buckets as pb
    print("Imported precompute_buckets OK")
    pb.main(r'c:\\wakanda\\ironman\\review-generator\\data\\Restaurant reviews.csv', r'c:\\wakanda\\ironman\\review-generator\\data\\buckets.json')
    print("precompute completed successfully")
except Exception:
    print("Exception during precompute:")
    traceback.print_exc()
    raise
