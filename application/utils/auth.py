import datetime
from functools import wraps

import jwt
from flask import request, g, jsonify
from index import app

TWO_WEEKS = datetime.timedelta(weeks=2)


def generate_token(user, expiration=TWO_WEEKS):
    payload = {
        "id": user.id,
        "email": user.email,
        "exp": datetime.datetime.now(datetime.timezone.utc) + expiration,
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")


def verify_token(token):
    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
    return data


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", None)
        if token:
            user = verify_token(token)
            if user:
                g.current_user = user
                return f(*args, **kwargs)

        return jsonify(message="Authentication is required to access this resource"), 401

    return decorated
