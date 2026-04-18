from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models import User, Profile, Swipe, Match
 
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
 
TABLE_MAP = {
    'user':    User,
    'profile': Profile,
    'swipe':   Swipe,
    'match':   Match,
}
 
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated
 
 
@admin_bp.route('/')
@login_required
@admin_required
def index():
    stats = {name: model.query.count() for name, model in TABLE_MAP.items()}
    return render_template('admin/index.html', stats=stats)
 
 
@admin_bp.route('/<table>')
@login_required
@admin_required
def table_view(table):
    if table not in TABLE_MAP:
        abort(404)
    model = TABLE_MAP[table]
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    query = model.query
    if q and table == 'user':
        query = query.filter(User.email.ilike(f'%{q}%'))
    elif q and table == 'profile':
        query = query.filter(Profile.name.ilike(f'%{q}%'))
    rows = query.order_by(model.id.desc()).paginate(page=page, per_page=25, error_out=False)
    columns = [c.name for c in model.__table__.columns]
    return render_template('admin/table.html', table=table, rows=rows, columns=columns, q=q)
 
 
@admin_bp.route('/<table>/<int:row_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_row(table, row_id):
    if table not in TABLE_MAP:
        abort(404)
    model = TABLE_MAP[table]
    row = model.query.get_or_404(row_id)
    columns = [c for c in model.__table__.columns if c.name != 'id']
 
    if request.method == 'POST':
        for col in columns:
            val = request.form.get(col.name)
            if col.name == 'password':
                if val:
                    from flask_bcrypt import Bcrypt
                    bcrypt = Bcrypt()
                    setattr(row, col.name, bcrypt.generate_password_hash(val).decode('utf-8'))
            else:
                setattr(row, col.name, val or None)
        db.session.commit()
        flash(f'{table.capitalize()} #{row_id} updated.', 'success')
        return redirect(url_for('admin.table_view', table=table))
 
    return render_template('admin/edit.html', table=table, row=row, columns=columns)
 
 
@admin_bp.route('/<table>/<int:row_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_row(table, row_id):
    if table not in TABLE_MAP:
        abort(404)
    model = TABLE_MAP[table]
    row = model.query.get_or_404(row_id)
    db.session.delete(row)
    db.session.commit()
    flash(f'{table.capitalize()} #{row_id} deleted.', 'success')
    return redirect(url_for('admin.table_view', table=table))