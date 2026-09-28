from types import SimpleNamespace

import pytest

from app.core.exceptions import InvalidVerificationTokenError
from app.core.security import create_email_verification_token
from app.services import auth_service, trip_service, user_service


def test_delete_account_removes_trip_files_and_profile_before_database(monkeypatch):
    events = []
    user = SimpleNamespace(
        profile_photo="profiles/1/photo.png",
        trips=[SimpleNamespace(files=[SimpleNamespace(path="trips/4/file.pdf")])],
    )
    monkeypatch.setattr(user_service, "delete_stored_file", lambda path: events.append(path))
    monkeypatch.setattr(user_service, "delete_profile_image", lambda path: events.append(path))
    monkeypatch.setattr(user_service, "delete_user", lambda **kwargs: events.append("database"))
    user_service.delete_current_user(object(), user)
    assert events == ["trips/4/file.pdf", "profiles/1/photo.png", "database"]


def test_delete_trip_keeps_record_if_storage_fails(monkeypatch):
    trip = SimpleNamespace(files=[SimpleNamespace(path="trips/1/file.pdf")])
    monkeypatch.setattr(trip_service, "get_user_trip_by_id", lambda **kwargs: trip)
    monkeypatch.setattr(trip_service, "delete_stored_file", lambda path: (_ for _ in ()).throw(OSError("storage")))
    monkeypatch.setattr(trip_service, "delete_trip_repository", lambda **kwargs: pytest.fail("deleted database despite storage failure"))
    with pytest.raises(OSError):
        trip_service.delete_user_trip(object(), object(), 1)


def test_email_token_is_bound_to_current_address(monkeypatch):
    user = SimpleNamespace(email="new@example.com", email_verified=False)
    monkeypatch.setattr(auth_service, "get_user_by_id", lambda **kwargs: user)
    token = create_email_verification_token("7", "old@example.com")
    with pytest.raises(InvalidVerificationTokenError):
        auth_service.verify_email(object(), token)
    monkeypatch.setattr(auth_service, "update_user", lambda **kwargs: kwargs["user"])
    token = create_email_verification_token("7", "new@example.com")
    auth_service.verify_email(object(), token)
    assert user.email_verified
