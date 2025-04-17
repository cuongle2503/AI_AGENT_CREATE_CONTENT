from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates',
                instance_relative_config=False)  # Tắt cấu hình instance
    
    # Secret key for session
    app.secret_key = os.environ.get('SECRET_KEY', 'dev_key_replace_in_production')
    
    # Xóa đoạn mã tạo thư mục instance
    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass
    
    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app 