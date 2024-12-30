from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiktok.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Increased to 100MB max file size

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Delete database file if it exists
with app.app_context():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tiktok.db')
    if os.path.exists(db_path):
        os.remove(db_path)

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    profile_pic = db.Column(db.String(120), default='default.png')
    bio = db.Column(db.String(200))
    videos = db.relationship('Video', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)
    caption = db.Column(db.String(500))
    hashtags = db.Column(db.String(500))  # Store hashtags as comma-separated string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='video', lazy=True)
    likes = db.relationship('Like', backref='video', lazy=True)
    views = db.Column(db.Integer, default=0)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create all tables
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 5
    videos = Video.query.order_by(Video.timestamp.desc()).paginate(page=page, per_page=per_page)
    return render_template('index.html', videos=videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        bio = request.form.get('bio')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('signup'))
            
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            bio=bio
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
        
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'video' not in request.files:
            flash('No video file')
            return redirect(request.url)
        
        video = request.files['video']
        caption = request.form.get('caption', '')
        hashtags = request.form.get('hashtags', '')  # Get hashtags from form
        
        if video.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if video:
            filename = secure_filename(video.filename)
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            new_video = Video(
                filename=filename,
                caption=caption,
                hashtags=hashtags,  # Save hashtags
                user_id=current_user.id
            )
            db.session.add(new_video)
            db.session.commit()
            
            return redirect(url_for('index'))
    
    return render_template('upload.html')

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    videos = Video.query.filter_by(user_id=user.id).order_by(Video.timestamp.desc()).all()
    return render_template('profile.html', user=user, videos=videos)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        if 'profile_pic' in request.files:
            file = request.files['profile_pic']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join('static/uploads/profiles', filename))
                current_user.profile_pic = filename
        
        current_user.bio = request.form.get('bio')
        db.session.commit()
        return redirect(url_for('profile', username=current_user.username))
        
    return render_template('edit_profile.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    if not query:
        return render_template('search.html', users=[], videos=[], query=query, search_type=search_type)
    
    if search_type == 'users':
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
        return render_template('search.html', users=users, videos=[], query=query, search_type=search_type)
    
    elif search_type == 'hashtags':
        videos = Video.query.filter(Video.hashtags.ilike(f'%{query}%')).order_by(Video.timestamp.desc()).all()
        return render_template('search.html', users=[], videos=videos, query=query, search_type=search_type)
    
    else:  # 'all'
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
        videos = Video.query.filter(
            db.or_(
                Video.hashtags.ilike(f'%{query}%'),
                Video.author.has(User.username.ilike(f'%{query}%'))
            )
        ).order_by(Video.timestamp.desc()).all()
        return render_template('search.html', users=users, videos=videos, query=query, search_type=search_type)

@app.route('/like/<int:video_id>', methods=['POST'])
@login_required
def like_video(video_id):
    video = Video.query.get_or_404(video_id)
    like = Like.query.filter_by(user_id=current_user.id, video_id=video_id).first()
    
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify({'action': 'unliked', 'likes': len(video.likes)})
    else:
        like = Like(user_id=current_user.id, video_id=video_id)
        db.session.add(like)
        db.session.commit()
        return jsonify({'action': 'liked', 'likes': len(video.likes)})

@app.route('/add_comment/<int:video_id>', methods=['POST'])
@login_required
def add_comment(video_id):
    data = request.get_json()
    content = data.get('content')
    if content:
        comment = Comment(
            content=content,
            user_id=current_user.id,
            video_id=video_id
        )
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'id': comment.id,
            'content': comment.content,
            'timestamp': comment.timestamp.isoformat(),
            'user': {
                'username': current_user.username,
                'profile_pic': url_for('static', filename='uploads/profiles/' + current_user.profile_pic)
            }
        })
    
    return jsonify({'error': 'No content provided'}), 400

@app.route('/get_more_comments/<int:video_id>')
def get_more_comments(video_id):
    # Get the last comment ID from the request
    last_comment_id = request.args.get('last_id', 0, type=int)
    
    # Get the next 10 comments
    comments = Comment.query.filter(
        Comment.video_id == video_id,
        Comment.id > last_comment_id
    ).order_by(Comment.timestamp.desc()).limit(10).all()
    
    # Convert comments to JSON
    comments_data = []
    for comment in comments:
        comments_data.append({
            'id': comment.id,
            'content': comment.content,
            'timestamp': comment.timestamp.isoformat(),
            'user': {
                'username': comment.user.username,
                'profile_pic': comment.user.profile_pic
            }
        })
    
    return jsonify(comments_data)

if __name__ == '__main__':
    app.run(debug=True)
