import json
import os
import secrets

import requests
from eth_account import Account
from eth_account.messages import encode_defunct


print("#"*70 + os.argv[0])


root = "http://127.0.0.1:6969/"
check = root + "check"
graphql = root + "graphql"


def test_check():
    session = requests.Session()

    print(session.post(check))
    print(session.post(check))
    print(session.post(check))
    print(session.post(check))


def test2():
    isLandlord = False
    session = requests.Session()

    data = 'query{authentication{address,isLandlord}}'
    need = '{"data": {"authentication": null}}'
    text = session.post(graphql, json={"query": data}).text
    assert text == need, f"{data!r} -> {text!r} != {need!r}"
    print(f"{data!r} -> {text!r}")

    private_key = "0x" + secrets.token_hex(32)
    acc = Account.from_key(private_key)

    data = 'mutation {message: requestAuthentication(address: "' + acc.address + '")}'
    son = session.post(graphql, json={"query": data}).json()
    message = son["data"]["message"]

    sig = Account.sign_message(encode_defunct(text=message), private_key)
    vrs = list(map(hex, (sig.v, sig.r, sig.s)))

    if isLandlord:
        os.environ["LANDLORD_ADDRESS"] = acc.address

    data = 'mutation {authentication: authenticate(address: "' + acc.address + '" signedMessage: {v: "' + vrs[0] + '" r: "' + vrs[1] + '" s: "' + vrs[2] + '"}) {address isLandlord}}'
    need = '{"data": {"authentication": {"address": "' + acc.address + '", "isLandlord": ' + json.dumps(isLandlord) + '}}}'
    text = session.post(graphql, json={"query": data}).text
    assert text == need, f"{data!r} -> {text!r} != {need!r}"
    # print(f"{data!r} -> {text!r}")

    data = 'query{authentication{address,isLandlord}}'
    need = need
    text = session.post(graphql, json={"query": data}).text
    assert text == need, f"{data!r} -> {text!r} != {need!r}"
    # print(f"{data!r} -> {text!r}")

    data = 'mutation {createRoom(room: {internalName: "some-name", area: 100.5, location: "some location"}) {id, internalName, area, location}}'
    need = {"data": {"createRoom": {"id": "<room-id>", "internalName": "some-name", "area": 100.5, "location": "some location"}}}
    resp = session.post(graphql, json={"query": data})
    son, text = resp.json(), resp.text
    room_id = son["data"]["createRoom"].pop("id")
    assert son == need, f"{data!r} -> {son!r} != {need!r}"
    print(f"{data!r} -> {text!r}")


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
