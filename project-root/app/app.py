from flask import Flask, render_template, request, redirect, url_for, flash
from app.search_logic import search_procedures
from app.procedure_data import get_procedure_details
from config import BASE_URI, ONTOLOGY, USER_MANUAL
from app.populate_knowledge_graph import add_procedure
from owlready2 import get_ontology
import markdown

app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Search route for fuzzy searching procedures with pagination
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')  # Get the search query from the URL parameter
    page = request.args.get('page', 1, type=int)  # Get the page number, default to 1
    per_page = 20  # Limit to 20 results per page
    
    if query:
        # Perform the fuzzy search using search logic
        all_results = search_procedures(query)
        
        # Slice results based on pagination
        start = (page - 1) * per_page
        end = start + per_page
        results = all_results[start:end]
        
        # Check if there are more results beyond the current page
        has_more = len(all_results) > end
        
        # Render search results with pagination
        return render_template('search_results.html', results=results, query=query, page=page, has_more=has_more)
    
    # Render the initial search form if no query is provided
    return render_template('search.html')

# Route for displaying the procedure details
@app.route('/procedure/<path:procedure_iri>', methods=['GET'])
def procedure_details(procedure_iri):
    procedure_iri = f"{BASE_URI}{procedure_iri}"  # Build the full IRI if needed
    procedure = get_procedure_details(procedure_iri)
    
    if procedure is None:
        return render_template('404.html'), 404  # Handle case if procedure not found
    
    return render_template('procedure_details.html', procedure=procedure)

@app.route('/add-procedure', methods=['GET', 'POST'])
def add_procedure_route():
    if request.method == 'POST':
        # Extract form data
        procedure_data = {
            'Url': request.form['url'],
            'Title': request.form['title'],
            'Category': request.form['category'],
            'Subject': request.form['subject'],
            'Toolbox': [],
            'Steps': []
        }

        # Add tools to the toolbox
        for tool_name, tool_url in zip(request.form.getlist('tool_name'), request.form.getlist('tool_url')):
            procedure_data['Toolbox'].append({'Name': tool_name, 'Url': tool_url})

        # Add steps
        for step_id, step_text, step_images, step_tools in zip(
                request.form.getlist('step_id'),
                request.form.getlist('step_text'),
                request.form.getlist('step_images'),
                request.form.getlist('step_tools')):
            procedure_data['Steps'].append({
                'StepId': step_id,
                'Text_raw': step_text,
                'Images': [img.strip() for img in step_images.split(',') if img.strip()],
                'Tools_extracted': [tool.strip() for tool in step_tools.split(',') if tool.strip()]
            })

        # Load ontology
        onto = get_ontology(ONTOLOGY).load()

        # Add procedure to ontology
        add_procedure(procedure_data, onto)

        flash('Procedure added successfully!')
        return redirect(url_for('add_procedure_route'))

    return render_template('add_procedure.html')

# Route for the user manual
@app.route('/user-manual')
def user_manual():
    # Read the markdown file specified in the configuration
    with open(USER_MANUAL, 'r', encoding='utf-8') as f:
        content = f.read()

    # Convert markdown content to HTML
    manual_html = markdown.markdown(content)

    # Render the HTML in the template
    return render_template('user_manual.html', manual_html=manual_html)

# Route for the resources page
@app.route('/resources')
def resources():
    return render_template('resources.html')

def run_app(debug=True):
    app.run(debug=debug)

if __name__ == "__main__":
    run_app()