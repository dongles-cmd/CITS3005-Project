from flask import Flask, render_template, request, redirect, url_for, send_from_directory
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

@app.route('/add-data', methods=['GET', 'POST'])
def add_data_route():
    if request.method == 'POST':
        class_type = request.form.get('classType')
        unique_id = request.form.get(f"{class_type}[unique_id]")

        # Load the ontology
        onto = get_ontology(BASE_URI).load()

        try:
            # Check if instance already exists
            existing_instance = onto.search_one(iri=f"{BASE_URI}{unique_id}")

            if class_type == 'Procedure':
                if existing_instance:  # If the instance exists, update it
                    procedure_for = request.form.get('Procedure[procedure_for]')
                    has_name = request.form.get('Procedure[has_name]')
                    procedure_uses_tool = request.form.get('Procedure[procedure_uses_tool]', '')
                    has_step = request.form.get('Procedure[has_step]', '')

                    # Update the existing procedure
                    existing_instance.procedure_for = procedure_for
                    existing_instance.has_name = has_name
                    if procedure_uses_tool:
                        existing_instance.procedure_uses_tool.append(onto.Tool(procedure_uses_tool))
                    if has_step:
                        step_instance = onto.search_one(iri=has_step)
                        if step_instance:
                            existing_instance.has_step.append(step_instance)

                    return redirect(url_for('success_page'))
                else:  # If the instance does not exist, create a new one
                    procedure_for = request.form['Procedure[procedure_for]']
                    has_name = request.form['Procedure[has_name]']

                    # Validate required fields
                    if not procedure_for or not has_name:
                        return redirect(url_for('failure_page'))
                    else:
                        new_procedure = onto.Procedure(unique_id=unique_id, procedure_for=procedure_for, has_name=has_name)
                        if has_step:
                            step_instance = onto.search_one(iri=has_step)
                            if step_instance:
                                new_procedure.has_step.append(step_instance)
                        return redirect(url_for('success_page'))

            elif class_type == 'Step':
                if existing_instance:  # If the instance exists, update it
                    has_text = request.form.get('Step[has_text]')
                    has_image = request.form.get('Step[has_image]', '')
                    step_uses_tool = request.form.get('Step[step_uses_tool]', '')
                    procedure = request.form.get('Step[procedure]')

                    # Update the existing step
                    existing_instance.has_text = has_text
                    if has_image:
                        existing_instance.has_image.append(onto.Image(has_image))
                    if step_uses_tool:
                        existing_instance.step_uses_tool.append(onto.Tool(step_uses_tool))

                    return redirect(url_for('success_page'))
                else:  # If the instance does not exist, create a new one
                    has_text = request.form['Step[has_text]']
                    procedure = request.form['Step[procedure]']

                    # Validate required fields
                    if not has_text or not procedure:
                        return redirect(url_for('failure_page'))
                    else:
                        procedure_instance = onto.search_one(iri=procedure)
                        if procedure_instance:
                            new_step = onto.Step(unique_id=unique_id, has_text=has_text)
                            if has_image:
                                image_instance = onto.search_one(iri=has_image)
                                if image_instance:
                                    new_step.has_image.append(image_instance)
                            if step_uses_tool:
                                tool_instance = onto.search_one(iri=step_uses_tool)
                                if tool_instance:
                                    new_step.step_uses_tool.append(tool_instance)
                            procedure_instance.has_step.append(new_step)
                            return redirect(url_for('success_page'))
                        else:
                            return redirect(url_for('failure_page'))

            elif class_type == 'Part':
                if existing_instance:  # If the instance exists, update it
                    part_of = request.form.get('Part[part_of]')
                    has_name = request.form.get('Part[has_name]')

                    # Update the existing part
                    existing_instance.part_of = part_of
                    existing_instance.has_name = has_name

                    return redirect(url_for('success_page'))
                else:  # If the instance does not exist, create a new one
                    part_of = request.form['Part[part_of]']
                    has_name = request.form['Part[has_name]']

                    # Validate required fields
                    if not part_of or not has_name:
                        return redirect(url_for('failure_page'))
                    else:
                        new_part = onto.Part(unique_id=unique_id, part_of=part_of, has_name=has_name)
                        return redirect(url_for('success_page'))

            elif class_type == 'Tool':
                if existing_instance:  # If the instance exists, update it
                    in_toolbox = request.form.get('Tool[in_toolbox]')
                    has_name = request.form.get('Tool[has_name]')

                    # Update the existing tool
                    existing_instance.in_toolbox = in_toolbox
                    existing_instance.has_name = has_name

                    return redirect(url_for('success_page'))
                else:  # If the instance does not exist, create a new one
                    in_toolbox = request.form['Tool[in_toolbox]']
                    has_name = request.form['Tool[has_name]']

                    # Validate required fields
                    if not in_toolbox or not has_name:
                        return redirect(url_for('failure_page'))
                    else:
                        procedure_instance = onto.search_one(iri=in_toolbox)
                        if procedure_instance:
                            new_tool = onto.Tool(unique_id=unique_id, has_name=has_name)
                            new_tool.in_toolbox.append(procedure_instance)
                            return redirect(url_for('success_page'))
                        else:
                            return redirect(url_for('failure_page'))

            elif class_type == 'Item':
                if existing_instance:  # If the instance exists, update it
                    has_name = request.form.get('Item[has_name]')

                    # Update the existing item
                    existing_instance.has_name = has_name

                    return redirect(url_for('success_page'))
                else:  # If the instance does not exist, create a new one
                    has_name = request.form['Item[has_name]']

                    # Validate required fields
                    if not has_name:
                        return redirect(url_for('failure_page'))
                    else:
                        new_item = onto.Item(unique_id=unique_id, has_name=has_name)
                        return redirect(url_for('success_page'))

            elif class_type == 'Image':
                if existing_instance:  # If the instance exists, update it
                    has_name = request.form.get('Image[has_name]')

                    # Update the existing image
                    existing_instance.has_name = has_name

                    return redirect(url_for('success_page'))
                else:  # If the instance does not exist, create a new one
                    has_name = request.form['Image[has_name]']

                    # Validate required fields
                    if not has_name:
                        return redirect(url_for('failure_page'))
                    else:
                        new_image = onto.Image(unique_id=unique_id, has_name=has_name)
                        return redirect(url_for('success_page'))

            # Redirect back to the form after adding or updating
            return redirect(url_for('add_data_route'))

        except Exception as e:
            return redirect(url_for('failure_page'))

    return render_template('add_to_database.html')


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