s = "()()"
brackets = ["()", "[]", "{}"]
symbols = ["(", ")", "[", "]", "{", "}"] 

for value in brackets:
    if value in s:
        s = s.replace(value, "")
    if value in s:
        s = s.replace(value, "")

if s == "":
    print(True)

for symbol in symbols:
    if symbol in s:
        print(False)
