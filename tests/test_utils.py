# ----- tests/test_utils.py -----
# Tests for Base62 encoding/decoding and random code generation.

from app.utils import encode_base62, decode_base62, generate_random_code


class TestBase62:
    """Tests for Base62 encoding & decoding."""

    def test_encode_zero(self):
        assert encode_base62(0) == "0"

    def test_encode_small_number(self):
        assert encode_base62(1) == "1"
        assert encode_base62(61) == "Z"

    def test_encode_62(self):
        assert encode_base62(62) == "10"

    def test_roundtrip(self):
        """Encoding then decoding should return the original number."""
        for num in [0, 1, 42, 100, 9999, 123456, 999999999]:
            assert decode_base62(encode_base62(num)) == num

    def test_decode_known_value(self):
        encoded = encode_base62(123456)
        assert decode_base62(encoded) == 123456


class TestRandomCode:
    """Tests for random code generation."""

    def test_default_length(self):
        code = generate_random_code()
        assert len(code) == 6

    def test_custom_length(self):
        code = generate_random_code(10)
        assert len(code) == 10

    def test_unique_codes(self):
        """Two generated codes should (almost certainly) be different."""
        codes = {generate_random_code() for _ in range(100)}
        assert len(codes) == 100  # all unique
