# TikTok Clone

A Flask-based web application that replicates core TikTok features with a modern, responsive interface.

## Features

### Video Management
- Upload and watch short videos
- Video player with custom controls:
  - Play/Pause
  - Progress bar with seek functionality
  - Volume control
  - Current time and duration display

### User Interaction
- User authentication (Login/Register)
- User profiles with profile pictures
- Like videos
- Comment on videos
- Follow/Unfollow users

### Social Features
- Interactive comment section
  - Collapsible comment interface
  - Real-time comment updates
  - User profile links in comments

### Search & Discovery
- Search by username or hashtags
- Filter search results by:
  - Users
  - Hashtags
  - All content
- Hashtag support in video captions

### Modern UI Features
- Responsive design for all screen sizes
- Infinite scroll for video feed
- Animated transitions and effects
- Dark theme
- Loading indicators
- Toast notifications

## Tech Stack

### Backend
- Python 3.x
- Flask
- SQLAlchemy (Database ORM)
- Flask-Login (User authentication)
- Werkzeug (Password hashing, file handling)

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)
- Font Awesome (Icons)
- Custom video player implementation

### Database
- SQLite (Development)
- PostgreSQL (Production ready)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ShakeelKhalid1913/tiktok-clone.git
cd tiktok-clone
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///tiktok.db
MAX_CONTENT_LENGTH=100000000  # 100MB max-size
```

5. Initialize the database:
```bash
flask db upgrade
```

6. Run the application:
```bash
flask run
```

Visit `http://localhost:5000` in your browser.

## Project Structure

```
tiktok-clone/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── uploads/
│       ├── profiles/
│       └── videos/
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── profile.html
│   ├── register.html
│   ├── search.html
│   └── upload.html
├── app.py
├── requirements.txt
└── README.md
```

## Configuration

### Video Upload Settings
- Maximum video size: 100MB
- Supported formats: MP4
- Video storage: Local filesystem (uploads directory)

### User Settings
- Profile picture max size: 5MB
- Supported formats: JPG, PNG
- Username requirements: 3-20 characters, alphanumeric

## Development

### Database Migrations
```bash
# Create a new migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade
```

### Running Tests
```bash
python -m pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by TikTok's UI/UX
- Video player implementation based on HTML5 Video API
- Icons from Font Awesome
