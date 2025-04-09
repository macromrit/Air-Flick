import uuid

# Generate a random UUID (version 4)
def generateUUID():
    unique_id = uuid.uuid4()
    return unique_id.__str__().replace("-", "")


if __name__ == "__main__":
    print(generateUUID())