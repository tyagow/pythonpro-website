from datetime import date

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from model_mommy import mommy

from pythonpro.django_assertions import dj_assert_contains, dj_assert_not_contains, dj_assert_template_used


@pytest.fixture
def home_resp(client):
    return _resp(client)


def _resp(client):
    """Plain function to avoid _pytest.warning_types.RemovedInPytest4Warning: Fixture "resp" called directly."""
    return client.get('/', secure=True)


@pytest.fixture
def home_resp_with_user(django_user_model, client: Client):
    user = mommy.make(django_user_model)
    client.force_login(user)
    return _resp(client)


def test_home_status_code(home_resp):
    assert 200 == home_resp.status_code


def test_thanks_status_code(client):
    resp = client.get(reverse('core:thanks'))
    assert 200 == resp.status_code


def test_home_template(home_resp):
    dj_assert_template_used(home_resp, template_name='core/index.html')


@pytest.mark.parametrize(
    'form_content',
    [
        '<form action="https://python.us17.list-manage.com/subscribe/post?u=ff7c56095f83f9c254edd749e&amp;id'
        '=e3072e0df0"',
        '<input type="text" name="FNAME"',
        '<input type="email" name="EMAIL"',
        '<button type="submit"'
    ]
)
def test_lead_form(form_content, home_resp):
    dj_assert_contains(home_resp, form_content)


@pytest.mark.parametrize(
    'name,value',
    [
        ('day', date.today().strftime('%d')),
        ('month', date.today().strftime('%m')),
        ('year', date.today().strftime('%Y')),
    ]
)
def test_subscription_today_date(name, value, home_resp):
    value = f'<input type="hidden" name="SUBSCRIP[{name}]" value="{value}"'
    dj_assert_contains(home_resp, value)


def test_forum_tab_is_not_present(home_resp):
    """
    Assert Forum tab is no present when user is not logged in
    """
    dj_assert_not_contains(home_resp, f'href="{settings.DISCOURSE_BASE_URL}"')


def test_forum_tab_is_present(home_resp_with_user):
    """
    Assert Forum tab is present when user is logged in
    """
    dj_assert_contains(home_resp_with_user, f'href="{settings.DISCOURSE_BASE_URL}"')


@pytest.fixture
def home_resp_open_subscriptions(settings, client):
    settings.SUBSCRIPTIONS_OPEN = True
    return _resp(client)


def test_payment_link_is_present(home_resp_open_subscriptions):
    """
    Assert Payment link is present on home page when subscriptions are open
    """
    dj_assert_contains(home_resp_open_subscriptions, reverse('payments:options'))


@pytest.fixture
def home_resp_closed_subscriptions(settings, client):
    settings.SUBSCRIPTIONS_OPEN = False
    return _resp(client)


def test_payment_link_is_not_present(home_resp_closed_subscriptions):
    """
    Assert Payment link is not present on home page when subscriptions are closed
    """
    dj_assert_not_contains(home_resp_closed_subscriptions, reverse('payments:options'))
