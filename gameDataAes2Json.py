from Crypto.Cipher import AES
import base64
import binascii
import re

_M0 = bytes.fromhex(
    "9693ad9f6e7e7034350c223affd2a0b57b6c76572e511b1c93a0d230c09aede7"
)
_P0 = bytes([5, 2, 7, 0, 6, 3, 1, 4])
_B64_RE = re.compile(rb"^[A-Za-z0-9+/=\s]+$")


def unfold(packed: bytes, order: bytes, salt: int) -> bytes:
    n = len(packed)
    out = bytearray(n)
    for i, dest in enumerate(order[: n // 4]):
        src, dst = i * 4, dest * 4
        out[dst : dst + 4] = packed[src : src + 4]
    s = salt
    for i in range(n):
        out[i] ^= (s + 7 * (i >> 2)) & 0xFF
        s = (s + 13) & 0xFF
    return bytes(out)


AES_KEY = unfold(_M0, _P0, 0xA7)


def _as_bytes(encrypt_data) -> bytes:
    if isinstance(encrypt_data, str):
        encrypt_data = encrypt_data.encode("latin-1", errors="surrogateescape")
    blob = encrypt_data
    stripped = blob.strip()
    if stripped and _B64_RE.fullmatch(stripped) and len(stripped.replace(b"\n", b"").replace(b"\r", b"").replace(b" ", b"")) >= 40:
        s = stripped.replace(b"\n", b"").replace(b"\r", b"").replace(b" ", b"")
        s += b"=" * ((-len(s)) % 4)
        try:
            decoded = base64.b64decode(s)
            if len(decoded) >= 28:
                return decoded
        except Exception:
            pass
    return blob


def rizline_aes_decrypt(encrypt_data, key: bytes = None, iv: bytes = None) -> str | None:
    """Current CN client: AES-256-GCM.

    Body is raw bytes: nonce(12) || ciphertext || tag(16)
    Base64 is accepted if the whole payload is ASCII base64.
    """
    try:
        blob = _as_bytes(encrypt_data)
        if len(blob) < 12 + 16:
            print(f"密文过短: {len(blob)} bytes")
            return None
        nonce, rest = blob[:12], blob[12:]
        cipher = AES.new(AES_KEY, AES.MODE_GCM, nonce=nonce)
        real_data = cipher.decrypt_and_verify(rest[:-16], rest[-16:])
        return real_data.decode("utf-8").strip()
    except UnicodeDecodeError as e:
        print(f"解码异常: {e}")
        print(f"解密原始字节: {binascii.hexlify(real_data).decode()}")
        return real_data.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        print(f"解密失败: {str(e)}")
        print(f"输入类型={type(encrypt_data).__name__} 长度={len(_as_bytes(encrypt_data))}")
        return None


if __name__ == "__main__":
    print("Rizline AES-GCM key:", AES_KEY)
