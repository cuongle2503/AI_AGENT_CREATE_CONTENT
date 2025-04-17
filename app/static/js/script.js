document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload-form');
    const generateBtn = document.getElementById('generate-btn');
    const resultSection = document.getElementById('result-section');
    const loadingSection = document.getElementById('loading');
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    const uploadedImage = document.getElementById('uploaded-image');
    const descriptionContent = document.getElementById('description-content');
    const copyMarkdownBtn = document.getElementById('copy-markdown-btn');
    const downloadMarkdownBtn = document.getElementById('download-markdown-btn');
    
    // Add toggle switch for showing raw markdown
    const toggleContainer = document.createElement('div');
    toggleContainer.className = 'form-check form-switch mb-3';
    toggleContainer.innerHTML = `
        <input class="form-check-input" type="checkbox" id="showMarkdownToggle">
        <label class="form-check-label" for="showMarkdownToggle">Show raw Markdown</label>
    `;
    form.appendChild(toggleContainer);
    
    const markdownToggle = document.getElementById('showMarkdownToggle');
    
    // Add button for viewing as dedicated markdown page
    const viewButtonContainer = document.createElement('div');
    viewButtonContainer.className = 'mt-3';
    viewButtonContainer.innerHTML = `
        <button id="view-markdown-page-btn" class="btn btn-outline-secondary btn-sm d-none">
            <i class="bi bi-file-earmark-text"></i> Open as Markdown Page
        </button>
    `;
    form.appendChild(viewButtonContainer);
    
    const viewMarkdownPageBtn = document.getElementById('view-markdown-page-btn');
    
    let currentDescription = '';
    let currentDescriptionHtml = '';
    let productName = '';
    let viewMarkdownUrl = '';

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Hide any previous results or errors
        resultSection.style.display = 'none';
        errorSection.style.display = 'none';
        viewMarkdownPageBtn.classList.add('d-none');
        
        // Show loading spinner
        loadingSection.style.display = 'block';
        
        // Disable submit button during processing
        generateBtn.disabled = true;
        
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Store both markdown and HTML versions
                currentDescription = data.description;
                currentDescriptionHtml = data.description_html || formatDescription(data.description);
                
                // Set URL for viewing as markdown page
                if (data.view_markdown_url) {
                    viewMarkdownUrl = data.view_markdown_url;
                    viewMarkdownPageBtn.classList.remove('d-none');
                }
                
                // Try to extract a product name for the filename from the first line or heading
                const firstLine = currentDescription.split('\n')[0];
                productName = firstLine.replace(/^#+\s+/, '').substring(0, 30).trim()
                    .replace(/[^a-zA-Z0-9 ]/g, '').replace(/\s+/g, '_');
                
                if (!productName) {
                    productName = 'product_description';
                }
                
                // Display results
                uploadedImage.src = data.image_url;
                
                // Show either raw markdown or rendered HTML based on toggle
                updateDescriptionDisplay();
                
                resultSection.style.display = 'block';
            } else {
                // Show error
                errorMessage.textContent = data.error || 'An error occurred while generating the description.';
                errorSection.style.display = 'block';
            }
        } catch (error) {
            // Show error for any exceptions
            errorMessage.textContent = 'An error occurred while processing your request.';
            errorSection.style.display = 'block';
            console.error('Error:', error);
        } finally {
            // Hide loading spinner and re-enable button
            loadingSection.style.display = 'none';
            generateBtn.disabled = false;
        }
    });
    
    // Toggle between raw markdown and rendered HTML
    markdownToggle.addEventListener('change', updateDescriptionDisplay);
    
    // Open the markdown view in a new tab
    viewMarkdownPageBtn.addEventListener('click', function() {
        window.open(viewMarkdownUrl, '_blank');
    });
    
    // Copy markdown to clipboard
    copyMarkdownBtn.addEventListener('click', function() {
        navigator.clipboard.writeText(currentDescription).then(function() {
            // Show success feedback
            const originalText = copyMarkdownBtn.innerHTML;
            copyMarkdownBtn.innerHTML = '<i class="bi bi-check"></i> Copied!';
            setTimeout(() => {
                copyMarkdownBtn.innerHTML = originalText;
            }, 2000);
        }, function(err) {
            console.error('Could not copy text: ', err);
        });
    });
    
    // Download markdown file
    downloadMarkdownBtn.addEventListener('click', function() {
        const blob = new Blob([currentDescription], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${productName}.md`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
    
    function updateDescriptionDisplay() {
        if (markdownToggle.checked) {
            // Show raw markdown in a pre element
            descriptionContent.innerHTML = `<pre class="markdown-raw">${escapeHtml(currentDescription)}</pre>`;
        } else {
            // Show rendered HTML
            descriptionContent.innerHTML = currentDescriptionHtml;
        }
    }
    
    // Function to format the description text with proper HTML
    function formatDescription(text) {
        // Replace line breaks with paragraph tags
        let formatted = text.replace(/\n\n/g, '</p><p>').replace(/\n/g, '<br>');
        
        // Wrap in paragraph tags if not already
        if (!formatted.startsWith('<p>')) {
            formatted = '<p>' + formatted;
        }
        if (!formatted.endsWith('</p>')) {
            formatted = formatted + '</p>';
        }
        
        return formatted;
    }
    
    // Helper function to escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}); 