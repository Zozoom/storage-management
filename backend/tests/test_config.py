from app.config import Settings


def test_default_access_token_lifetime_is_15_minutes():
    assert Settings.model_fields["access_token_expire_minutes"].default == 15
