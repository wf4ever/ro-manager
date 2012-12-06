import json

if __name__ == "__main__":
    f = open("data/generated.json")
    t = f.read()
    j = json.loads(t)

