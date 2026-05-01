import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models.user import db
from controllers.auth_controller import auth_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql://root:root@localhost/ats_db')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_secret_key')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(auth_bp)

    @app.route('/api/health')
    def health():
        return {'status': 'ok'}

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)


# --- Resume Recommendation Endpoint ---
@app.route('/api/recommend_resume', methods=['POST'])
def recommend_resume():
    data = request.get_json()
    job_desc = data.get('job_description', '')
    resume = data.get('resume', '')

    # Simple keyword matching (placeholder for AI/ML logic)
    job_keywords = set(re.findall(r'\b\w+\b', job_desc.lower()))
    resume_words = set(re.findall(r'\b\w+\b', resume.lower()))
    missing_keywords = job_keywords - resume_words

    recommendations = []
    if missing_keywords:
        recommendations.append(f"Consider including these keywords from the job description: {', '.join(list(missing_keywords)[:10])}")
    else:
        recommendations.append("Your resume covers most keywords from the job description.")

    # Placeholder for more advanced AI/ML suggestions

    return jsonify({
        'recommendations': recommendations
    })

if __name__ == '__main__':
    app.run(debug=True)
