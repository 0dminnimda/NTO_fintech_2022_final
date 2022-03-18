import json
import os
import secrets

import requests
from eth_account import Account
from eth_account.messages import encode_defunct

root = "http://127.0.0.1:6969/"
check = root + "check"
graphql = root + "graphql"


def test_check():
    session = requests.Session()

    print(session.post(check))
    print(session.post(check))
    print(session.post(check))
    print(session.post(check))


def poster(session, data):
    resp = session.post(graphql, json={"query": data})
    return resp.json(), resp.text


def asserter(data, need, res):
    assert res == need, f"{data!r}\n -> {res!r}\n != {need!r}"
    print(f"{data!r} -> {res!r}")


def test2():
    # isLandlord = True
    session = requests.Session()

    data = 'query{authentication{address,isLandlord}}'
    need = '{"data": {"authentication": null}}'
    son, text = poster(session, data)
    asserter(data, need, text)

    data = 'mutation {createRoom(room: {internalName: "some-name", area: 100.5, location: "some location"}) {id, internalName, area, location}}'  # noqa
    need = '{"errors": [{"message": "Authentication required"}]}'
    son, text = poster(session, data)
    asserter(data, need, text)

    data = 'mutation {setRoomContractAddress(id: "<room-id>", contractAddress: "<contract-address>") {id, contractAddress}}'  # noqa
    need = '{"errors": [{"message": "Authentication required"}]}'
    son, text = poster(session, data)
    asserter(data, need, text)

    private_key = "0x" + secrets.token_hex(32)
    acc = Account.from_key(private_key)
    data = 'mutation {message: requestAuthentication(address: "' + acc.address + '")}'  # noqa
    son, text = poster(session, data)
    message = son["data"]["message"]

    # if isLandlord:
    #     os.environ["LANDLORD_ADDRESS"] = acc.address

    sig = Account.sign_message(encode_defunct(text=message), private_key)
    vrs = list(map(hex, (sig.v, sig.r, sig.s)))
    data = 'mutation {authentication: authenticate(address: "' + acc.address + '" signedMessage: {v: "' + vrs[0] + '" r: "' + vrs[1] + '" s: "' + vrs[2] + '"}) {address isLandlord}}'  # noqa
    son, text = poster(session, data)
    isLandlord = son["data"]["authentication"]["isLandlord"]
    need = '{"data": {"authentication": {"address": "' + acc.address + '", "isLandlord": ' + json.dumps(isLandlord) + '}}}'  # noqa
    asserter(data, need, text)

    data = 'query{authentication{address,isLandlord}}'
    need = need
    son, text = poster(session, data)
    asserter(data, need, text)

    data = 'mutation {createRoom(room: {internalName: "some-name", area: 100.5, location: "some location"}) {id, internalName, area, location}}'  # noqa
    if isLandlord:
        son, text = poster(session, data)
        room_id = son["data"]["createRoom"]["id"]
        need = '{"data": {"createRoom": {"id": "' + room_id + '", "internalName": "some-name", "area": 100.5, "location": "some location"}}}'  # noqa
        asserter(data, need, text)

        data = 'query {room(id: "' + room_id + '") {id, internalName, area, location}}'  # noqa
        need = '{"data": {"room": {"id": "' + room_id + '", "internalName": "some-name", "area": 100.5, "location": "some location"}}}'  # noqa
        son, text = poster(session, data)
        asserter(data, need, text)

        data = 'mutation {createRoom(room: {internalName: "some-name", area: -1, location: "some location"}) {id, internalName, area, location}}'  # noqa
        need = '{"errors": [{"message": "The room area must be greater than zero"}]}'  # noqa
        son, text = poster(session, data)
        asserter(data, need, text)

        data = 'mutation {createRoom(room: {internalName: "some-name", area: 0, location: "some location"}) {id, internalName, area, location}}'  # noqa
        need = need
        son, text = poster(session, data)
        asserter(data, need, text)
    else:
        need = '{"errors": [{"message": "This method is available only for the landlord"}]}'  # noqa
        son, text = poster(session, data)
        asserter(data, need, text)

    contract_address = "0x" + secrets.token_hex(32)
    if isLandlord:
        data = 'mutation {setRoomContractAddress(id: "' + room_id + '", contractAddress: "' + contract_address + '") {id, contractAddress}}'  # noqa
        need = '{"data": {"setRoomContractAddress": {"id": "' + room_id + '", "contractAddress": "' + contract_address + '"}}}'  # noqa
        son, text = poster(session, data)
        asserter(data, need, text)

        data = 'query {room(id: "' + room_id + '") {id, contractAddress}}'
        need = '{"data": {"room": {"id": "' + room_id + '", "contractAddress": "' + contract_address + '"}}}'  # noqa
        son, text = poster(session, data)
        asserter(data, need, text)

        data = 'mutation {setRoomContractAddress(id: "<nonexisting-room-id>", contractAddress: "<contract-address>") {id, contractAddress}}'
        need = '{"errors": [{"message": "Room with such ID not found"}]}'
        son, text = poster(session, data)
        asserter(data, need, text)
    else:
        data = 'mutation {setRoomContractAddress(id: "<room-id>", contractAddress: "' + contract_address + '") {id, contractAddress}}'  # noqa
        need = '{"errors": [{"message": "This method is available only for the landlord"}]}'  # noqa
        son, text = poster(session, data)
        asserter(data, need, text)


test_check()


test2()


# t1 = "0x" + secrets.token_hex(5)
# pairs = [
#     'mutation {authentication: authenticate(address: "0xCe746b0E2aF26F13C8513b2f985746D65c906f72" signedMessage: {v: "0x1b" r: "0xbe4d9d4de333ca1d6b2697bd5614e7d6006bca8fb9b01f915c04f80dbd579868" s: "0x2f6237bcdd563c0c560faeb3053fb9b0b646317264d2f279c708e118b2ce2fba"}) {address isLandlord}}',
#     '{"errors": [{"message": "Authentication failed"}]}',

#     'mutation {message: requestAuthentication(address: "' + t1 + '")}', None,


#     'query{authentication{address,isLandlord}}', '{"data": {"authentication": null}}',
#     'mutation {message: requestAuthentication(address: "' + t1 + '")}', None,
#     'mutation {message: requestAuthentication(address: "' + t1 + '")}', None,
#     'mutation {message: requestAuthentication(address: "' + "0x" + secrets.token_hex(5) + '")}', None,

#     'mutation {authentication: authenticate(address: "0xCe746b0E2aF26F13C8513b2f985746D65c906f72" signedMessage: {v: "0x1b" r: "0xbe4d9d4de333ca1d6b2697bd5614e7d6006bca8fb9b01f915c04f80dbd579868" s: "0x2f6237bcdd563c0c560faeb3053fb9b0b646317264d2f279c708e118b2ce2fba"}) {address isLandlord}}',
#     '{"data": {"authentication": {"address": "0xCe746b0E2aF26F13C8513b2f985746D65c906f72", "isLandlord": false}}}',

#     'query{authentication{address,isLandlord}}',
#     '{"data": {"authentication": {"address": "0xCe746b0E2aF26F13C8513b2f985746D65c906f72", "isLandlord": false}}}',

# ]

# for data, need in zip(pairs[::2], pairs[1::2]):
#     resp = session.post(graphql, json={"query": data})
#     text = resp.text
#     # resp.json()
#     if need is not None:
#         assert text == need, f"{data!r} -> {text!r} != {need!r}"
#     else:
#         print(f"{data!r} -> {text!r}")

print("SUCCESS")
