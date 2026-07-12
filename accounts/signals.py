from django.contrib.auth.signals import user_logged_in
from django.contrib.sessions.models import Session
from django.dispatch import receiver

from .models import UserSession


@receiver(user_logged_in)
def one_session_per_user(sender, request, user, **kwargs):
    session_key = request.session.session_key

    if session_key is None:
        request.session.save()
        session_key = request.session.session_key

    try:
        old_session = UserSession.objects.get(user=user)

        if old_session.session_key != session_key:
            Session.objects.filter(session_key=old_session.session_key).delete()

        old_session.session_key = session_key
        old_session.save()

    except UserSession.DoesNotExist:
        UserSession.objects.create(
            user=user,
            session_key=session_key
        )