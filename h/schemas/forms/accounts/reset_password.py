# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import colander
import deform
from itsdangerous import BadData, SignatureExpired

from h import i18n, models
from h.schemas.base import CSRFSchema
from h.schemas.forms.accounts import util

_ = i18n.TranslationString


class ResetCode(colander.SchemaType):

    """Schema type transforming a reset code to a user and back."""

    def serialize(self, node, appstruct):
        if appstruct is colander.null:
            return colander.null
        if not isinstance(appstruct, models.User):
            raise colander.Invalid(node, "%r is not a User" % appstruct)
        request = node.bindings["request"]
        serializer = request.registry.password_reset_serializer
        return serializer.dumps(appstruct.username)

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null

        request = node.bindings["request"]
        serializer = request.registry.password_reset_serializer

        try:
            (username, timestamp) = serializer.loads(
                cstruct, max_age=72 * 3600, return_timestamp=True
            )
        except SignatureExpired:
            raise colander.Invalid(
                node, _("Reset code has expired. Please reset your password again")
            )
        except BadData:
            raise colander.Invalid(node, _("Wrong reset code."))

        user = models.User.get_by_username(
            request.db, username, request.default_authority
        )
        if user is None:
            raise colander.Invalid(node, _("Your reset code is not valid"))
        if user.password_updated is not None and timestamp < user.password_updated:
            raise colander.Invalid(node, _("This reset code has already been used."))
        return user


class ResetPasswordSchema(CSRFSchema):
    # N.B. this is the field into which the user puts their reset code, but we
    # call it `user` because when validated, it will return a `User` object.
    user = colander.SchemaNode(
        ResetCode(),
        title=_("Reset code"),
        hint=_("This will be emailed to you."),
        widget=deform.widget.TextInputWidget(disable_autocomplete=True),
    )
    password = util.new_password_node(
        title=_("New password"),
        widget=deform.widget.PasswordWidget(disable_autocomplete=True),
    )
