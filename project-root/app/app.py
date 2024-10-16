from flask import Flask, render_template, request
from app.search_logic import search_procedures

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

# Route for displaying procedure details
@app.route('/procedure/<path:procedure_iri>')
def procedure_details(procedure_iri):
    # Placeholder to query the knowledge graph for procedure details based on IRI
    procedure_data = get_procedure_details(procedure_iri)

    # Render the details page
    return render_template('procedure_details.html', procedure=procedure_data)

# Route for the user manual
@app.route('/user-manual')
def user_manual():
    return render_template('user_manual.html')

# Route for the resources page
@app.route('/resources')
def resources():
    return render_template('resources.html')

def run_app(debug=True):
    app.run(debug=debug)

if __name__ == "__main__":
    run_app()