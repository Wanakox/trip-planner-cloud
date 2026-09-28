from types import SimpleNamespace
from datetime import UTC, datetime, timedelta

import pytest

from app.core.exceptions import (
    EmailAlreadyRegisteredError,
    PendingRegistrationNotFoundError,
    InvalidVerificationTokenError,
    RegistrationExpiredError,
    VerificationCooldownError,
)
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


def test_delete_account_with_legacy_profile_reference(monkeypatch):
    events = []
    user = SimpleNamespace(
        profile_photo="https://example.com/photo.jpg",
        trips=[SimpleNamespace(files=[SimpleNamespace(path="/old/uploads/file.pdf")])],
    )
    monkeypatch.setattr(user_service, "delete_profile_image", lambda path: pytest.fail("invalid storage key"))
    monkeypatch.setattr(user_service, "delete_stored_file", lambda path: pytest.fail("invalid storage key"))
    monkeypatch.setattr(user_service, "delete_user", lambda **kwargs: events.append("database"))
    user_service.delete_current_user(object(), user)
    assert events == ["database"]


def test_delete_trip_keeps_record_if_storage_fails(monkeypatch):
    trip = SimpleNamespace(files=[SimpleNamespace(path="trips/1/file.pdf")])
    monkeypatch.setattr(trip_service, "get_user_trip_by_id", lambda **kwargs: trip)
    monkeypatch.setattr(trip_service, "delete_stored_file", lambda path: (_ for _ in ()).throw(OSError("storage")))
    monkeypatch.setattr(trip_service, "delete_trip_repository", lambda **kwargs: pytest.fail("deleted database despite storage failure"))
    with pytest.raises(OSError):
        trip_service.delete_user_trip(object(), object(), 1)


def test_email_token_is_bound_to_current_address(monkeypatch):
    user = SimpleNamespace(email="new@example.com", email_verified=False, registration_expires_at=None)
    monkeypatch.setattr(auth_service, "get_user_by_id", lambda **kwargs: user)
    token = create_email_verification_token("7", "old@example.com")
    with pytest.raises(InvalidVerificationTokenError):
        auth_service.verify_email(object(), token)
    monkeypatch.setattr(auth_service, "update_user", lambda **kwargs: kwargs["user"])
    token = create_email_verification_token("7", "new@example.com")
    auth_service.verify_email(object(), token)
    assert user.email_verified


def test_expired_registration_cannot_verify_or_resend(monkeypatch):
    user = SimpleNamespace(id=7, email="ana@example.com", email_verified=False,
                           registration_expires_at=datetime.now(UTC) - timedelta(seconds=1),
                           verification_sent_at=None)
    monkeypatch.setattr(auth_service, "get_user_by_id", lambda **kwargs: user)
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda **kwargs: user)
    with pytest.raises(RegistrationExpiredError):
        auth_service.verify_email(object(), create_email_verification_token("7", user.email))
    with pytest.raises(RegistrationExpiredError):
        auth_service.resend_verification(object(), user.email)


def test_resend_during_cooldown_reports_no_email_was_sent(monkeypatch):
    user = SimpleNamespace(email="ana@example.com", email_verified=False,
                           registration_expires_at=datetime.now(UTC) + timedelta(hours=1),
                           verification_sent_at=datetime.now(UTC))
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda **kwargs: user)
    monkeypatch.setattr(auth_service, "send_verification_email", lambda user: pytest.fail("sent during cooldown"))
    with pytest.raises(VerificationCooldownError):
        auth_service.resend_verification(object(), user.email)


def test_change_pending_email_rejects_registered_address(monkeypatch):
    user = SimpleNamespace(email="ana@example.com", hashed_password="hash", email_verified=False,
                           registration_expires_at=datetime.now(UTC) + timedelta(hours=1))
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda **kwargs:
                        user if kwargs["email"] == user.email else SimpleNamespace(id=2))
    monkeypatch.setattr(auth_service, "verify_password", lambda *args, **kwargs: True)
    with pytest.raises(EmailAlreadyRegisteredError):
        auth_service.change_pending_email(object(), user.email, "correct-password", "used@example.com")
    assert user.email == "ana@example.com"


def test_resend_reports_missing_or_already_verified_email(monkeypatch):
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda **kwargs: None)
    with pytest.raises(PendingRegistrationNotFoundError):
        auth_service.resend_verification(object(), "missing@example.com")
    monkeypatch.setattr(auth_service, "get_user_by_email", lambda **kwargs: SimpleNamespace(email_verified=True))
    with pytest.raises(EmailAlreadyRegisteredError):
        auth_service.resend_verification(object(), "used@example.com")
