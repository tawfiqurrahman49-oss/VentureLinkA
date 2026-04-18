from flask import render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.swipe import swipe_bp
from app.models import User, Swipe, Match


def get_candidates():
    """Return users of the opposite role who the current user hasn't swiped on yet."""
    opposite = 'investor' if current_user.role == 'startup' else 'startup'
    swiped_ids = [s.swiped_id for s in current_user.swipes_given.all()]
    candidates = (
        User.query
        .filter(User.role == opposite)
        .filter(User.id != current_user.id)
        .filter(~User.id.in_(swiped_ids))
        .join(User.profile)
        .all()
    )
    return [c for c in candidates if c.profile]


@swipe_bp.route('/')
@login_required
def deck():
    if not current_user.profile:
        return redirect(url_for('profiles.edit'))
    candidates = get_candidates()
    return render_template('swipe/deck.html', candidates=candidates)


@swipe_bp.route('/action', methods=['POST'])
@login_required
def action():
    data = request.get_json()
    swiped_id = data.get('swiped_id')
    direction = data.get('direction')  # 'left' or 'right'

    if not swiped_id or direction not in ('left', 'right'):
        return jsonify({'error': 'invalid'}), 400

    # Prevent duplicate swipes
    existing = Swipe.query.filter_by(swiper_id=current_user.id, swiped_id=swiped_id).first()
    if existing:
        return jsonify({'match': False})

    swipe = Swipe(swiper_id=current_user.id, swiped_id=swiped_id, direction=direction)
    db.session.add(swipe)

    matched = False
    match_user = None
    if direction == 'right':
        # Check if the other person already swiped right on us
        mutual = Swipe.query.filter_by(swiper_id=swiped_id, swiped_id=current_user.id, direction='right').first()
        if mutual:
            # Avoid duplicate matches
            exists = Match.query.filter(
                ((Match.user_a_id == current_user.id) & (Match.user_b_id == swiped_id)) |
                ((Match.user_a_id == swiped_id) & (Match.user_b_id == current_user.id))
            ).first()
            if not exists:
                match = Match(user_a_id=current_user.id, user_b_id=swiped_id)
                db.session.add(match)
                matched = True
                other = User.query.get(swiped_id)
                match_user = {'name': other.profile.name if other.profile else other.email}

    db.session.commit()
    return jsonify({'match': matched, 'match_user': match_user})
