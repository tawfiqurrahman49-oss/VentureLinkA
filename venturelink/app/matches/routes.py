from flask import render_template, request, abort
from flask_login import login_required, current_user
from app.matches import matches_bp
from app.models import Match, Message
from app import db


@matches_bp.route('/')
@login_required
def list():
    matches = Match.query.filter(
        (Match.user_a_id == current_user.id) |
        (Match.user_b_id == current_user.id)
    ).order_by(Match.created_at.desc()).all()

    paired = []
    for match in matches:
        other = match.user_b if match.user_a_id == current_user.id else match.user_a
        if other.profile:
            paired.append({'match': match, 'user': other, 'profile': other.profile})

    return render_template('matches/list.html', paired=paired)


@matches_bp.route('/<int:match_id>/chat', methods=['GET', 'POST'])
@login_required
def chat(match_id):
    match = Match.query.get_or_404(match_id)

    if current_user.id not in (match.user_a_id, match.user_b_id):
        abort(403)

    if request.method == 'POST':
        body = request.form.get('body', '').strip()
        if body:
            msg = Message(match_id=match.id, sender_id=current_user.id, body=body)
            db.session.add(msg)
            db.session.commit()

    messages = Message.query.filter_by(match_id=match.id).order_by(Message.created_at.asc()).all()
    other = match.user_b if match.user_a_id == current_user.id else match.user_a

    return render_template('matches/chat.html', match=match, messages=messages, other=other)
