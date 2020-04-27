from functools import wraps


class ValidationError(Exception):
    pass


def with_arguments(a=0, b=32, max_length=256):
    def decorator(handler):
        @wraps(handler)
        async def decorated(self, author, args):
            if len(args) < a or len(args) > b:
                raise ValidationError

            for arg in args:
                if len(arg) > max_length:
                    raise ValidationError
            return await handler(self, author, args)
        return decorated
    return decorator
