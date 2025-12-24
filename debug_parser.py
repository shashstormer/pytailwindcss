from pytailwind.parser import ClassParser

parser = ClassParser()
tokens = [
    "gap-x-(--my-gap)",
    "space-x-4",
    "space-x-reverse",
    "gap-4",
    "p-4"
]

print(f"{'Class':<20} | {'Utility':<10} | {'Modifier':<10} | {'Value':<10} | {'ValueType'}")
print("-" * 70)

for t in tokens:
    token = parser.parse(t)
    print(f"{t:<20} | {token.utility:<10} | {str(token.modifier):<10} | {token.value:<10} | {token.value_type}")
