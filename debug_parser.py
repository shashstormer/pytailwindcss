from pytailwind.parser import ClassParser, ValueType
parser = ClassParser()
token = parser.parse('text-lg/loose')
print(f"Token: {token}")
print(f"Value type: {token.value_type}")
print(f"FRACTION: {ValueType.FRACTION}")
