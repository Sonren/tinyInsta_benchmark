from google.cloud import datastore

client = datastore.Client()

KIND_LIST = ["User", "Post"]

for kind in KIND_LIST:
    print(f"Deleting all entities of kind: {kind}")

    query = client.query(kind=kind)

    keys = [entity.key for entity in query.fetch()]

    if not keys:
        print("  -> No entities found.")
        continue

    BATCH_SIZE = 500
    for i in range(0, len(keys), BATCH_SIZE):
        batch = keys[i:i+BATCH_SIZE]
        client.delete_multi(batch)
        print(f"  -> Deleted {len(batch)} entities")

print("Datastore reset complete.")