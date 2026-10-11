import hashlib
from collections.abc import Mapping, Sequence
from functools import reduce


def _get_dict_hash(d: Mapping[str, object]) -> bytes:
    msg = hashlib.sha1()
    for key in sorted(d.keys()):
        v = d[key]
        if isinstance(v, str):
            msg.update(v.encode())
        else:
            msg.update(str(v).encode())
    return msg.digest()


def _xor_bytes(bytes1: bytes, bytes2: bytes) -> bytes:
    return bytes([b1 ^ b2 for b1, b2 in zip(bytes1, bytes2)])


def get_dict_list_checksum(ls: Sequence[Mapping[str, object]]) -> str:
    """
    calculate checksum of list of dict objects
    truncates to first 8 characters of checksum
    sha1 is sufficient as there's low risk and low impact of collision in this context
    """
    if len(ls) == 0:
        return hashlib.sha1(str([]).encode()).hexdigest()[:8]

    # use xor so that order of each item doesn't matter
    checksum_bytes = reduce(_xor_bytes, map(_get_dict_hash, ls))
    return checksum_bytes.hex()[:8]
