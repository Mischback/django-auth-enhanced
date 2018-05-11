# -*- coding: utf-8 -*-
"""Includes tests targeting the app's management commands.

    - target file: auth_enhanced/management/commands/_lib.py
    - included tags: 'command'"""


# Python imports
from unittest import skip  # noqa

# Django imports
from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.test import override_settings, tag  # noqa

# app imports
from auth_enhanced.management.commands.authenhanced import (
    check_admin_notification, check_email_uniqueness,
)

# app imports
from .utils.testcases import AuthEnhancedTestCase

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


@tag('command')
class CheckAuthEnhancedCommand(AuthEnhancedTestCase):
    """This tests target the parts of the command logic, that is not really
    involved in checking."""

    def test_unknown_command(self):
        """Unknown commands raise an error."""

        # prepare test environment to capture stdout
        out = StringIO()

        with self.assertRaisesMessage(CommandError, "No valid command was provided!"):
            call_command('authenhanced', 'foo', stdout=out)


@tag('command')
class CheckAdminNotificationTests(AuthEnhancedTestCase):
    """These tests target the 'check_admin_notification()'-function.

    See auth_enhanced/management/commands/_lib.py"""

    fixtures = ['tests/utils/fixtures/test_different_users.json']

    @override_settings(DAE_ADMIN_SIGNUP_NOTIFICATION=(
        ('django', 'django@localhost', ('mail', )),
        ('foo', 'foo@localhost', ('mail', )),
    ))
    def test_all_valid(self):
        """Returns True, if the setting is completely valid."""

        self.assertTrue(check_admin_notification())

    @override_settings(DAE_ADMIN_SIGNUP_NOTIFICATION=(
        ('django', 'django@localhost', ('mail', )),
        ('foo', 'foo@localhost', ('mail', )),
        ('bar', 'bar@localhost', ('mail', )),
    ))
    def test_address_unverified(self):
        """Raises an exception, if one of the accounts has an unverified email
        address."""

        with self.assertRaisesMessage(
            CommandError,
            "The following accounts do not have a verified email address: bar. "
            "Administrative notifications will only be sent to verfified email "
            "addresses."
        ):
            check_admin_notification()

    @override_settings(DAE_ADMIN_SIGNUP_NOTIFICATION=(
        ('django', 'django@localhost', ('mail', )),
        ('foo', 'foo@localhost', ('mail', )),
        ('baz', 'baz@localhost', ('mail', )),
    ))
    def test_insufficient_permissions(self):
        """Raises an exception, if one of the accounts does not have sufficient
        permissions."""

        with self.assertRaisesMessage(
            CommandError,
            "The following accounts do not have the sufficient permissions to "
            "actually modify accounts: baz."
        ):
            check_admin_notification()


@tag('command')
class CheckEmailUniquenessTests(AuthEnhancedTestCase):
    """These tests target the 'check_email_uniqueness()'-function.

    See auth_enhanced/management/commands/_lib.py"""

    def test_all_addresses_unique(self):
        """Returns True, if all email addresses are unique."""

        user_model = get_user_model()

        # create two users
        u = user_model.objects.create_user(**{          # noqa
            user_model.USERNAME_FIELD: 'django',        # noqa
            user_model.EMAIL_FIELD: 'django@localhost'  # noqa
        })                                              # noqa
        v = user_model.objects.create_user(**{          # noqa
            user_model.USERNAME_FIELD: 'foo',           # noqa
            user_model.EMAIL_FIELD: 'foo@localhost'     # noqa
        })                                              # noqa

        self.assertTrue(check_email_uniqueness())

    def test_addresses_not_unique(self):
        """Raises an exception, if the email addresses are not unique."""

        user_model = get_user_model()

        # create two users
        u = user_model.objects.create_user(**{          # noqa
            user_model.USERNAME_FIELD: 'django',        # noqa
            user_model.EMAIL_FIELD: 'django@localhost'  # noqa
        })                                              # noqa
        v = user_model.objects.create_user(**{          # noqa
            user_model.USERNAME_FIELD: 'foo',           # noqa
            user_model.EMAIL_FIELD: 'django@localhost'  # noqa
        })                                              # noqa

        with self.assertRaisesMessage(
            CommandError,
            "The following accounts don't have unique email addresses: django, foo"
        ):
            check_email_uniqueness()
