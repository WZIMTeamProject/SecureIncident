import uuid

from core import security


class TestCreateAccessToken:
    def test_create_access_token_payload_includes_family_id(self):
        user_id = uuid.uuid4()
        family_id = uuid.uuid4()

        token = security.create_access_token(user_id, family_id)
        payload = security.decode_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["family_id"] == str(family_id)
        assert isinstance(payload["family_id"], str)
        assert "exp" in payload
        assert "iat" in payload
        assert "jti" in payload

    def test_create_access_token_ttl_is_flat_fifteen_minutes(self):
        token = security.create_access_token(uuid.uuid4(), uuid.uuid4())
        payload = security.decode_token(token)

        lifetime_minutes = (payload["exp"] - payload["iat"]) / 60
        assert 14 <= lifetime_minutes <= 16

    def test_decode_token_validates_fresh_access_token(self):
        user_id = uuid.uuid4()
        token = security.create_access_token(user_id, uuid.uuid4())

        payload = security.decode_token(token)

        assert payload["sub"] == str(user_id)
        assert "exp" in payload
        assert "jti" in payload
