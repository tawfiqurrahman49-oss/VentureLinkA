from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, URL, NumberRange


INDUSTRIES = [
    ('fintech', 'Fintech'), ('healthtech', 'Healthtech'), ('edtech', 'Edtech'),
    ('saas', 'SaaS'), ('ai_ml', 'AI / ML'), ('consumer', 'Consumer'),
    ('deeptech', 'Deep Tech'), ('climate', 'Climate Tech'), ('ecommerce', 'E-Commerce'),
    ('marketplace', 'Marketplace'), ('crypto', 'Crypto / Web3'), ('other', 'Other'),
]

STAGES = [
    ('idea', 'Idea Stage'), ('pre_seed', 'Pre-Seed'), ('seed', 'Seed'),
    ('series_a', 'Series A'), ('series_b', 'Series B+'),
]

CHECK_SIZES = [
    ('25k_100k', '$25K – $100K'), ('100k_500k', '$100K – $500K'),
    ('500k_2m', '$500K – $2M'), ('2m_10m', '$2M – $10M'), ('10m_plus', '$10M+'),
]


class StartupProfileForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    bio = TextAreaField('What do you do?', validators=[DataRequired(), Length(max=500)])
    industry = SelectField('Industry', choices=INDUSTRIES, validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    stage = SelectField('Stage', choices=STAGES, validators=[DataRequired()])
    funding_ask = StringField('Funding Ask (e.g. $500K)', validators=[Optional(), Length(max=50)])
    team_size = IntegerField('Team Size', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Save Profile')


class InvestorProfileForm(FlaskForm):
    name = StringField('Your Name / Fund Name', validators=[DataRequired(), Length(max=100)])
    bio = TextAreaField('About you', validators=[DataRequired(), Length(max=500)])
    industry = SelectField('Focus Industry', choices=INDUSTRIES, validators=[DataRequired()])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    check_size = SelectField('Check Size', choices=CHECK_SIZES, validators=[DataRequired()])
    thesis = TextAreaField('Investment Thesis', validators=[Optional(), Length(max=500)])
    portfolio = StringField('Notable Portfolio (comma-separated)', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Save Profile')
