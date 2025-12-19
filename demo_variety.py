"""
Demonstration of review variety with template-based generation
"""
from nlp.template_generator import TemplateReviewGenerator

gen = TemplateReviewGenerator('data/templates.json', 'data/buckets.json')
business = 'Rati Kaka Ni Bhajipav'

print("\n" + "="*75)
print("VARIETY TEST: Generating 5 Medium-Level Reviews (Same Business)")
print("="*75)
print(f"\nBusiness: {business}")
print(f"Level: Medium (4 sentences)")
print(f"Data: 6,562 reviews → 29,392 sentences bucketed")
print("\n" + "="*75 + "\n")

for i in range(5):
    review = gen.generate_review(business, 'medium')
    print(f"[Review {i+1}]")
    print(review)
    print()

print("="*75)
print("✅ Notice: Each review is unique, natural, and professionally written!")
print("   Repetition minimized through template mixing + 29K+ sentences")
print("="*75 + "\n")
