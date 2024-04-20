import os

import pandas as pd
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.objects import Base
from specklepy.transports.server import ServerTransport

speckle_api_key = os.environ["SPECKLE_API"]
stream_id = os.environ["SPECKLE_STREAM_ID"]
client = SpeckleClient(host="https://app.speckle.systems")
client.authenticate_with_token(speckle_api_key)

def get_speckle_models(**kwargs):
    branches = client.branch.list(stream_id=stream_id)
    branch_names = [branche.name for branche in branches if branche.name != "main"]
    return branch_names


def flatten_base(base: Base):
    if hasattr(base, "elements") and base.elements is not None:
        for element in base["elements"]:
            yield from flatten_base(element)
    yield base


def push_prices_to_speckle(branch_name: str, prices_dict: dict[str, dict[str, float]]):
    branch = client.branch.get(stream_id, branch_name, 1)
    object_id = branch.commits.items[0].referencedObject
    transport = ServerTransport(client=client, stream_id=stream_id)
    received_base = operations.receive(obj_id=object_id, remote_transport=transport)
    if branch_name == "concrete":
        new_base = received_base["@Concrete"]
    else:
        new_base = received_base["@Lighting"]
    # Consume
    print("new base", new_base.__dict__)
    for key, potential_mesh_list in new_base.__dict__.items():
        if isinstance(potential_mesh_list, list):
            for mesh in potential_mesh_list:
                mesh["prices"] = prices_dict[mesh["Name"]]
    transport = ServerTransport(client=client, stream_id=stream_id)
    new_object_id = operations.send(base=received_base, transports=[transport])
    print(f"new ojbect id {new_object_id}")
    commit_id = client.commit.create(
        stream_id=stream_id,
        branch_name=branch_name,
        object_id=new_object_id,
        message="Update from viktor app",
        source_application="viktor"
    )
    print(f"new commit id {commit_id}")


def get_speckle_concrete_volume_dataframe(**kwargs):
    branch = client.branch.get(stream_id, "concrete", 1)
    object_id = branch.commits.items[0].referencedObject
    transport = ServerTransport(client=client, stream_id=stream_id)
    received_base = operations.receive(obj_id=object_id, remote_transport=transport)
    new_base = received_base["@Concrete"]
    # Consume
    l = []
    for key, potential_mesh_list in new_base.__dict__.items():
        if isinstance(potential_mesh_list, list):
            for mesh in potential_mesh_list:
                l.append({mesh["Name"]: mesh["Volume (m³)"]})
    dataframe = pd.DataFrame(l).sum()
    return dataframe


def get_speckle_lighting_dataframe(**kwargs):
    branch = client.branch.get(stream_id, "lighting", 1)
    object_id = branch.commits.items[0].referencedObject
    transport = ServerTransport(client=client, stream_id=stream_id)
    received_base = operations.receive(obj_id=object_id, remote_transport=transport)
    new_base = received_base["@Lighting"]
    # Consume
    l = []
    for key, potential_mesh_list in new_base.__dict__.items():
        if isinstance(potential_mesh_list, list):
            for mesh in potential_mesh_list:
                l.append({mesh["Name"]: 1})
    dataframe = pd.DataFrame(l).sum()
    return dataframe


def get_speckle_concrete_names(**kwargs):
    branch = client.branch.get(stream_id, "concrete", 1)
    object_id = branch.commits.items[0].referencedObject
    transport = ServerTransport(client=client, stream_id=stream_id)
    received_base = operations.receive(obj_id=object_id, remote_transport=transport)
    new_base = received_base["@Concrete"]
    print(new_base.__dict__)
    # Consume
    l = []
    for key, potential_mesh_list in new_base.__dict__.items():
        if isinstance(potential_mesh_list, list):
            for mesh in potential_mesh_list:
                l.append(mesh["Name"])
    print(l)
    return list(set(l))


def get_speckle_lighting_names(**kwargs):
    branch = client.branch.get(stream_id, "lighting", 1)
    object_id = branch.commits.items[0].referencedObject
    transport = ServerTransport(client=client, stream_id=stream_id)
    received_base = operations.receive(obj_id=object_id, remote_transport=transport)
    new_base = received_base["@Lighting"]
    print(new_base.__dict__)
    # Consume
    l = []
    for key, potential_mesh_list in new_base.__dict__.items():
        if isinstance(potential_mesh_list, list):
            for mesh in potential_mesh_list:
                l.append(mesh["Name"])
    print(l)
    return list(set(l))
