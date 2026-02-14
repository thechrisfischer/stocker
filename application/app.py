import json
import logging

from flask import request, render_template, render_template_string, jsonify, g
from sqlalchemy.exc import IntegrityError

from index import app, db, limiter
from .models import User, Company, FinancialData
from .rankings import get_rankings, VALID_STRATEGIES
from .utils.auth import generate_token, requires_auth, verify_token

logger = logging.getLogger(__name__)

REACT_COMPONENT_TEMPLATE = "<div data-react-props='{{props}}' data-react-class={{ name }}></div>"


@app.template_global()
def react_component(name, props={}):
    return render_template_string(REACT_COMPONENT_TEMPLATE, name=name, props=json.dumps(props))


@app.route("/", methods=["GET"])
def index():
    return render_template("templates/index.html")


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(status="ok")


@app.route("/api/create_user", methods=["POST"])
@limiter.limit("5 per minute")
def create_user():
    incoming = request.get_json()
    user = User(
        email=incoming["email"],
        password=incoming["password"],
    )
    db.session.add(user)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(message="User with that email already exists"), 409

    new_user = User.query.filter_by(email=incoming["email"]).first()
    return jsonify(id=user.id, token=generate_token(new_user))


@app.route("/api/get_token", methods=["POST"])
@limiter.limit("10 per minute")
def get_token():
    incoming = request.get_json()
    user = User.get_user_with_email_and_password(
        incoming["email"], incoming["password"]
    )
    if user:
        return jsonify(token=generate_token(user))

    return jsonify(error=True), 403


@app.route("/api/is_token_valid", methods=["POST"])
def is_token_valid():
    incoming = request.get_json()
    is_valid = verify_token(incoming["token"])

    if is_valid:
        return jsonify(token_is_valid=True)
    else:
        return jsonify(token_is_valid=False), 403


@app.route("/api/user", methods=["GET"])
@requires_auth
def get_user():
    return jsonify(result=g.current_user)


# --- Stock data API routes ---


@app.route("/api/rankings/<strategy>", methods=["GET"])
def rankings(strategy):
    if strategy not in VALID_STRATEGIES:
        return jsonify(error="Invalid strategy", valid_strategies=VALID_STRATEGIES), 400
    results = get_rankings(strategy)
    return jsonify(strategy=strategy, rankings=results)


@app.route("/api/companies", methods=["GET"])
def list_companies():
    companies = Company.query.order_by(Company.symbol).all()
    return jsonify(companies=[c.to_dict() for c in companies])


@app.route("/api/companies/<symbol>", methods=["GET"])
def get_company(symbol):
    company = Company.query.filter_by(symbol=symbol.upper()).first()
    if not company:
        return jsonify(error="Company not found"), 404
    financials = FinancialData.query.filter_by(company_id=company.id).first()
    return jsonify(
        company=company.to_dict(),
        financials=financials.to_dict() if financials else None,
    )


@app.route("/api/strategies", methods=["GET"])
def list_strategies():
    return jsonify(strategies=VALID_STRATEGIES)
