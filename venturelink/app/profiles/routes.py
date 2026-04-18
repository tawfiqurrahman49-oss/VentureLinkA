from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.profiles import profiles_bp
from app.profiles.forms import StartupProfileForm, InvestorProfileForm
from app.models import Profile
from datetime import datetime


@profiles_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    profile = current_user.profile
    if current_user.role == 'startup':
        form = StartupProfileForm()
        if form.validate_on_submit():
            if not profile:
                profile = Profile(user_id=current_user.id)
                db.session.add(profile)
            profile.name = form.name.data
            profile.bio = form.bio.data
            profile.industry = form.industry.data
            profile.location = form.location.data
            profile.website = form.website.data
            profile.stage = form.stage.data
            profile.funding_ask = form.funding_ask.data
            profile.team_size = form.team_size.data
            profile.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Profile saved!', 'success')
            return redirect(url_for('swipe.deck'))
        elif profile:
            form.name.data = profile.name
            form.bio.data = profile.bio
            form.industry.data = profile.industry
            form.location.data = profile.location
            form.website.data = profile.website
            form.stage.data = profile.stage
            form.funding_ask.data = profile.funding_ask
            form.team_size.data = profile.team_size
    else:
        form = InvestorProfileForm()
        if form.validate_on_submit():
            if not profile:
                profile = Profile(user_id=current_user.id)
                db.session.add(profile)
            profile.name = form.name.data
            profile.bio = form.bio.data
            profile.industry = form.industry.data
            profile.location = form.location.data
            profile.website = form.website.data
            profile.check_size = form.check_size.data
            profile.thesis = form.thesis.data
            profile.portfolio = form.portfolio.data
            profile.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Profile saved!', 'success')
            return redirect(url_for('swipe.deck'))
        elif profile:
            form.name.data = profile.name
            form.bio.data = profile.bio
            form.industry.data = profile.industry
            form.location.data = profile.location
            form.website.data = profile.website
            form.check_size.data = profile.check_size
            form.thesis.data = profile.thesis
            form.portfolio.data = profile.portfolio

    return render_template('profiles/edit.html', form=form, role=current_user.role)
