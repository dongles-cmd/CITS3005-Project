from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from app.search_logic import search_procedures
from app.procedure_data import get_procedure_details
from config import BASE_URI, KNOWLEDGE_GRAPH, USER_MANUAL
from app.populate_knowledge_graph import add_procedure
from owlready2 import get_ontology
import markdown

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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

def check_constraints():
    pass

@app.route('/edit-data', methods=['GET', 'POST'])
def edit_data_route():
    if request.method == 'POST':
        onto = get_ontology(KNOWLEDGE_GRAPH).load()
        action = request.form.get('action')
        submit_type = request.form.get('submit')

        if action == 'class_instance':
            class_name = request.form.get('class_name')
            class_uri = request.form.get('class_uri')
            classes = ["Procedure", "Item", "Part", "Tool", "Step", "Image"]

            if class_name not in classes:
                flash(f"Class type does not exist!")
            elif submit_type == 'add_class':
                # Add Class
                existing_instance = onto.search_one(iri=f"{BASE_URI}{class_uri}")
                if existing_instance:
                    flash(f"Class instance {class_uri} already exists!")
                else:
                    class_to_add = getattr(onto, class_name)
                    class_instance = class_to_add(class_uri)
                    flash(f"Class {class_name} added with URI {class_uri}!")
            elif submit_type == 'delete_class':
                # Delete Class
                class_instance = onto.search_one(iri=f"{BASE_URI}{class_uri}")
                if class_instance:
                    class_instance.destroy()  # Use destroy to remove the instance
                    flash(f"Class instance {class_uri} has been deleted.")
                else:
                    flash(f"Class instance {class_uri} not found!")

        # Adding or Deleting a relation
        elif action == 'relation':
            obj1 = request.form.get('obj1')
            relation = request.form.get('relation')
            obj2 = request.form.get('obj2')

            # Fetch instances of the objects
            obj1_instance = onto.search_one(iri=f"{BASE_URI}{obj1}")
            obj2_instance = onto.search_one(iri=f"{BASE_URI}{obj2}")
            
            # Available properties (relations)
            properties = ["has_name", "has_text", "step_uses_tool", "has_step", "has_image", 
                          "sub_procedure_of", "procedure_for", "part_of", "in_toolbox", "procedure_uses_tool"]

            if relation not in properties:
                flash("Relation does not exist!")
            elif not obj1_instance:
                flash(f"{obj1} does not exist, add it to the knowledge graph first.")
            elif relation == "has_name" or relation == "has_text":
                relation_property = getattr(onto, relation, None)
                if submit_type == 'add_relation':
                    relation_property[obj1_instance].append(obj2)
                    flash(f"Successfully added relation {relation} between {obj1} and {obj2}.")
                elif submit_type == 'delete_relation':
                    if obj2_instance in relation_property[obj1_instance]:
                        relation_property[obj1_instance].remove(obj2)
                        flash(f"Successfully removed relation {relation} between {obj1} and {obj2}.")
            elif not obj2_instance:
                flash(f"{obj2} does not exist, add it to the knowledge graph first.")
            else:
                relation_property = getattr(onto, relation, None)
                if submit_type == 'add_relation':
                    relation_property[obj1_instance].append(obj2_instance)
                    flash(f"Successfully added relation {relation} between {obj1} and {obj2}.")
                elif submit_type == 'delete_relation':
                    if obj2_instance in relation_property[obj1_instance]:
                        relation_property[obj1_instance].remove(obj2_instance)
                        flash(f"Successfully removed relation {relation} between {obj1} and {obj2}.")

        # Save the changes to the ontology
        onto.save(file=KNOWLEDGE_GRAPH)
        return redirect(url_for('edit_data_route'))

    return render_template('edit_database.html')


@app.route('/success')
def success_page():
    return render_template('success.html')

@app.route('/failure')
def failure_page():
    return render_template('failure.html')

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

# Route to serve images from the 'images/' directory in the root project
@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('../images', filename)

# Route for the resources page
@app.route('/resources')
def resources():
    return render_template('resources.html')

def run_app(debug=True):
    app.run(debug=debug)

if __name__ == "__main__":
    run_app()