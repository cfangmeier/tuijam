def sec_to_min_sec(sec_tot):
    s = int(sec_tot or 0)
    return s // 60, s % 60


def lookup_keys(*key_ids):
    import base64
    import yaml
    import rsa
    import requests

    from tuijam import CONFIG_FILE

    keys = [None] * len(key_ids)
    # First, check if any are in configuration file
    with open(CONFIG_FILE, "r") as f:
        cfg = yaml.safe_load(f)
        for idx, id_ in enumerate(key_ids):
            try:
                keys[idx] = cfg[id_]
            except KeyError:
                pass

    # Next, if any unspecified in config file, ask the server for them
    to_query = {}
    for idx, (id_, key) in enumerate(zip(key_ids, keys)):
        if key is None:
            # keep track of position of each key so output order matches
            to_query[id_] = idx

    if to_query:
        (pub, priv) = rsa.newkeys(512)  # Generate new RSA key pair. Do not reuse keys!
        host = cfg.get("key_server", "https://tuijam.fangmeier.tech")

        res = requests.post(
            host, json={"public_key": pub.save_pkcs1().decode(), "ids": list(to_query)}
        )

        for id_, key_encrypted in res.json().items():
            # On the server, the api key is encrypted with the public RSA key,
            # and then base64 encoded to be delivered. Reverse that process here.
            key_decrypted = rsa.decrypt(
                base64.decodebytes(key_encrypted.encode()), priv
            ).decode()
            keys[to_query[id_]] = key_decrypted

    return keys
