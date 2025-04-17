from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, Response
from markupsafe import Markup
import os
import uuid
from werkzeug.utils import secure_filename
from .services.product_description import generate_product_description, generate_product_description_multiple
from .services.prompts.model_config import OPENAI_MODELS, DEFAULT_OPENAI_MODEL
import markdown
import re
import time

# Create a blueprint
main_bp = Blueprint('main', __name__)

# Configure upload settings
UPLOAD_FOLDER = 'app/static/uploads'
MARKDOWN_FOLDER = 'app/static/markdown'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(MARKDOWN_FOLDER, exist_ok=True)

# Maximum age of temp files in seconds (24 hours)
MAX_FILE_AGE = 24 * 60 * 60

def cleanup_old_files(directory, max_age=MAX_FILE_AGE):
    """Remove files older than max_age seconds from directory"""
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        # Skip if it's a directory or not a file
        if not os.path.isfile(file_path):
            continue
        # Remove if file is older than max_age
        if current_time - os.path.getmtime(file_path) > max_age:
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error removing {file_path}: {e}")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_markdown(text):
    """Convert plain text to markdown with proper formatting"""
    # Format headings (assume paragraphs that are all caps or end with : are headings)
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Check for potential headings (all caps, or ends with :)
        stripped = line.strip()
        if stripped and (stripped.isupper() or stripped.endswith(':')):
            # Remove any trailing colon
            heading = stripped.rstrip(':')
            formatted_lines.append(f'### {heading}')
        else:
            formatted_lines.append(line)
    
    text = '\n'.join(formatted_lines)
    
    # Format lists
    text = re.sub(r'(?m)^- (.+)$', r'* \1', text)  # Convert - lists to * for markdown
    
    # Add paragraph spacing
    text = re.sub(r'\n\n+', '\n\n', text)  # Normalize multiple newlines to double
    
    # Emphasize important words/phrases
    text = re.sub(r'(?<!\*)\b([A-Z][A-Z0-9]+)\b(?!\*)', r'**\1**', text)  # Capitalize words to bold
    
    return text

def save_markdown_to_file(content, product_name="product"):
    """Save markdown content to a file and return the filename"""
    # Clean up old files first
    cleanup_old_files(MARKDOWN_FOLDER)
    
    # Generate a unique filename
    unique_id = str(uuid.uuid4())[:8]
    safe_product_name = re.sub(r'[^a-zA-Z0-9]', '_', product_name)[:30]
    filename = f"{safe_product_name}_{unique_id}.md"
    file_path = os.path.join(MARKDOWN_FOLDER, filename)
    
    # Save content to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return filename

def get_markdown_content(filename):
    """Get markdown content from a file"""
    file_path = os.path.join(MARKDOWN_FOLDER, filename)
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/markdown')
def show_markdown():
    try:
        with open('README.md', 'r') as f:
            content = f.read()
        html_content = Markup(markdown.markdown(content))
        return render_template('markdown.html', content=html_content)
    except Exception as e:
        return f"Error loading markdown: {str(e)}"

@main_bp.route('/view-markdown/<filename>')
def view_markdown(filename):
    """View a markdown file by filename"""
    content = get_markdown_content(filename)
    if not content:
        return redirect(url_for('main.index'))
    
    html_content = Markup(markdown.markdown(content))
    return render_template('markdown.html', 
                          content=html_content, 
                          title="Product Description", 
                          raw_markdown=content,
                          filename=filename)

@main_bp.route('/download-markdown/<filename>')
def download_markdown(filename):
    """Download a markdown file by filename"""
    content = get_markdown_content(filename)
    if not content:
        return redirect(url_for('main.index'))
    
    return Response(
        content,
        mimetype='text/markdown',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@main_bp.route('/markdown-preview', methods=['POST'])
def markdown_preview():
    """Preview text as markdown"""
    content = request.json.get('content', '')
    html_content = Markup(markdown.markdown(content))
    return jsonify({'html': html_content})

@main_bp.route('/models')
def get_models():
    """Return available models as JSON"""
    return jsonify({
        'openai_models': OPENAI_MODELS,
        'default_model': DEFAULT_OPENAI_MODEL
    })

@main_bp.route('/generate', methods=['POST'])
def generate():
    request_text = request.form.get('request_text', '')
    openai_model = request.form.get('openai_model', DEFAULT_OPENAI_MODEL)
    is_multiple_mode = request.form.get('multiple_mode') == 'true'
    
    # Debug information
    print("Form data keys:", list(request.form.keys()))
    print("Files keys:", list(request.files.keys()))
    print("Multiple mode:", is_multiple_mode)
    
    if is_multiple_mode:
        # Multiple images mode
        print("Handling multiple images mode")
        
        # Get all files with the 'images' field name
        files = request.files.getlist('images')
        print(f"Number of files found: {len(files)}")
        
        if len(files) == 0:
            return jsonify({'error': 'No images provided'}), 400
        
        # Check if all files are allowed
        for file in files:
            if file.filename == '' or not allowed_file(file.filename):
                return jsonify({'error': 'One or more invalid files'}), 400
        
        # Save all files and process each one individually
        results = []
        
        for file in files:
            # Save the file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # Generate description for this image
            try:
                description = generate_product_description(
                    file_path,
                    request_text,
                    openai_model=openai_model
                )
                
                # Convert description to markdown format
                markdown_description = convert_to_markdown(description)
                
                # Try to extract a product name from the first line or heading
                first_line = markdown_description.split('\n')[0]
                product_name = re.sub(r'^#+\s+', '', first_line).strip()[:30]
                
                if not product_name:
                    product_name = f"product_{len(results) + 1}"
                
                # Save to file
                markdown_filename = save_markdown_to_file(markdown_description, product_name)
                
                # Add to results
                results.append({
                    'description': markdown_description,
                    'description_html': Markup(markdown.markdown(markdown_description)),
                    'image_url': f'/static/uploads/{unique_filename}',
                    'view_markdown_url': url_for('main.view_markdown', filename=markdown_filename),
                    'download_url': url_for('main.download_markdown', filename=markdown_filename),
                    'product_name': product_name
                })
                
            except Exception as e:
                print(f"Error generating description for {filename}: {str(e)}")
                # Continue with other images even if one fails
        
        if not results:
            return jsonify({'error': 'Failed to generate descriptions for all images'}), 500
            
        return jsonify({
            'multiple_results': True,
            'results': results,
            'model_used': openai_model
        })
            
    else:
        # Single image mode
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image = request.files['image']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if image.filename == '':
            return jsonify({'error': 'No selected image file'}), 400
        
        if image and allowed_file(image.filename):
            # Save the file to uploads directory
            filename = secure_filename(image.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            image.save(file_path)
            
            # Generate product description
            try:
                description = generate_product_description(
                    file_path, 
                    request_text,
                    openai_model=openai_model
                )
                
                # Convert description to markdown format
                markdown_description = convert_to_markdown(description)
                
                # Try to extract a product name from the first line or heading
                first_line = markdown_description.split('\n')[0]
                product_name = re.sub(r'^#+\s+', '', first_line).strip()[:30]
                
                if not product_name:
                    product_name = "product_description"
                
                # Save to file instead of session
                markdown_filename = save_markdown_to_file(markdown_description, product_name)
                
                return jsonify({
                    'multiple_results': False,
                    'description': markdown_description,
                    'description_html': Markup(markdown.markdown(markdown_description)),
                    'image_url': f'/static/uploads/{filename}',
                    'view_markdown_url': url_for('main.view_markdown', filename=markdown_filename),
                    'download_url': url_for('main.download_markdown', filename=markdown_filename),
                    'model_used': openai_model
                })
            except Exception as e:
                print(f"Error generating description: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400

@main_bp.route('/test')
def test_upload_page():
    """Test page for multiple image uploads"""
    return render_template('test_upload.html')

@main_bp.route('/test_upload', methods=['POST'])
def test_upload():
    """Test endpoint for multiple image uploads"""
    # Debug information
    print("Form data keys:", list(request.form.keys()))
    print("Files keys:", list(request.files.keys()))
    
    result = {
        'form_data': {k: request.form[k] for k in request.form},
        'files_received': []
    }
    
    # Get files with name 'images'
    files = request.files.getlist('images')
    print(f"Number of files received: {len(files)}")
    
    # Process files
    for file in files:
        if file.filename:
            # Save file temporarily
            filename = secure_filename(file.filename)
            unique_filename = f"test_{uuid.uuid4().hex[:8]}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(file_path)
            
            # Add to result
            result['files_received'].append({
                'filename': file.filename,
                'saved_as': unique_filename,
                'size': os.path.getsize(file_path),
                'url': f'/static/uploads/{unique_filename}'
            })
    
    return jsonify(result) 