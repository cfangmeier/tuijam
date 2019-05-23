def sec_to_min_sec(sec_tot):
    s = int(sec_tot or 0)
    return s // 60, s % 60


def lookup_keys(*key_ids):
    import rsa
    import base64
    import requests

    (pub, priv) = rsa.newkeys(512)

    host = "https://tuijam.fangmeier.tech"

    res = requests.post(
        host, json={"public_key": pub.save_pkcs1().decode(), "ids": key_ids}
    )

    keys = []
    for id_, key_enc in res.json().items():
        keys.append(rsa.decrypt(base64.decodebytes(key_enc.encode()), priv).decode())
    return keys
