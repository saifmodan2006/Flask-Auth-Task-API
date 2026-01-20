# schemas.py
from marshmallow import Schema, fields, validate

class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class ForgotSchema(Schema):
    email = fields.Email(required=True)

class ResetSchema(Schema):
    password = fields.Str(required=True, validate=validate.Length(min=6))
