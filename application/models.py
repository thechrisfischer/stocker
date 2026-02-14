from index import db, bcrypt


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.active = True
        self.password = User.hashed_password(password)

    @staticmethod
    def hashed_password(password):
        return bcrypt.generate_password_hash(password)

    @staticmethod
    def get_user_with_email_and_password(email, password):
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return None


class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(255))
    sector = db.Column(db.String(255))
    industry = db.Column(db.String(255))
    financials = db.relationship("FinancialData", backref="company", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "sector": self.sector,
            "industry": self.industry,
        }


class FinancialData(db.Model):
    __tablename__ = "financial_data"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    symbol = db.Column(db.String(10), unique=True)
    date = db.Column(db.DateTime)
    ask = db.Column(db.Float)
    book_value = db.Column(db.Float)
    market_cap = db.Column(db.Float)
    ebitda = db.Column(db.Float)
    pe_ratio_ttm = db.Column(db.Float)
    pe_ratio_ftm = db.Column(db.Float)
    eps_estimate_qtr = db.Column(db.Float)
    peg_ratio = db.Column(db.Float)
    garp_ratio = db.Column(db.Float)
    return_on_assets = db.Column(db.Float)
    return_on_equity = db.Column(db.Float)
    change_year_low_per = db.Column(db.Float)
    change_year_high_per = db.Column(db.Float)
    net_income = db.Column(db.Float)
    total_assets = db.Column(db.Float)
    shares_outstanding = db.Column(db.Float)
    one_yr_target_price = db.Column(db.Float)
    dividend_yield = db.Column(db.Float)
    eps_estimate_current_year = db.Column(db.Float)
    eps_estimate_next_year = db.Column(db.Float)
    eps_estimate_next_quarter = db.Column(db.Float)
    magic_formula_trailing = db.Column(db.Float)
    magic_formula_future = db.Column(db.Float)

    # Rank columns
    rank_ebitda = db.Column(db.Float)
    rank_pe_ratio_ttm = db.Column(db.Float)
    rank_pe_ratio_ftm = db.Column(db.Float)
    rank_eps_estimate_qtr = db.Column(db.Float)
    rank_peg_ratio = db.Column(db.Float)
    rank_garp_ratio = db.Column(db.Float)
    rank_return_on_assets = db.Column(db.Float)
    rank_return_on_equity = db.Column(db.Float)
    rank_change_year_low_per = db.Column(db.Float)
    rank_change_year_high_per = db.Column(db.Float)
    rank_dividend_yield = db.Column(db.Float)
    rank_magic_formula_trailing = db.Column(db.Float)
    rank_magic_formula_future = db.Column(db.Float)

    def to_dict(self):
        return {
            "id": self.id,
            "symbol": self.symbol,
            "date": self.date.isoformat() if self.date else None,
            "pe_ratio_ttm": self.pe_ratio_ttm,
            "pe_ratio_ftm": self.pe_ratio_ftm,
            "peg_ratio": self.peg_ratio,
            "garp_ratio": self.garp_ratio,
            "return_on_assets": self.return_on_assets,
            "return_on_equity": self.return_on_equity,
            "dividend_yield": self.dividend_yield,
            "ebitda": self.ebitda,
            "market_cap": self.market_cap,
            "magic_formula_trailing": self.magic_formula_trailing,
            "magic_formula_future": self.magic_formula_future,
        }
