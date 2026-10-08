import hashlib
from collections.abc import Mapping, Sequence
from functools import reduce


def _get_dict_hash(d: Mapping[str, object]) -> bytes:
    msg = hashlib.sha3_256()
    for v in d.values():
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
    """
    if len(ls) == 0:
        msg = hashlib.sha3_256()
        msg.update(str([]).encode())
        return msg.digest().hex()

    checksum_bytes = reduce(_xor_bytes, map(_get_dict_hash, ls))
    return checksum_bytes.hex()[:8]
