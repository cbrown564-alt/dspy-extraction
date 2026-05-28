import sys
from pathlib import Path

# Add src/ to python path so we can import clinical_extraction
sys.path.insert(0, str(Path("src").resolve()))

from clinical_extraction.datasets.gan import load_gan_records

records = load_gan_records()

unknown_labels = set()
unknown_counts = {}

for r in records:
    label = r.gold_label
    if "unknown" in label:
        unknown_labels.add(label)
        unknown_counts[label] = unknown_counts.get(label, 0) + 1

print(f"Total unique gold labels containing 'unknown': {len(unknown_labels)}")
print("\nUnique labels and their counts:")
for label in sorted(unknown_labels):
    print(f"  {label!r}: {unknown_counts[label]}")
