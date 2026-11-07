from auth import hash_password, verify_password


def test_password_hashing():
    stored = hash_password("secret123")
    assert stored != "secret123"
    assert verify_password("secret123", stored)
    assert not verify_password("wrong", stored)
