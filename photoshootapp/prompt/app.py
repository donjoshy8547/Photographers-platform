import os
from flask import Flask, render_template, request, url_for
from image_search import ImageSearch

app = Flask(__name__)

# Initialize the search engine
csv_path = 'mai/image_captions.csv'
image_folder = 'mai/photographer_6'
search_engine = ImageSearch(csv_path, image_folder)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ""
    filters = {}
    min_score = 0.10  # Default minimum score threshold
    
    if request.method == 'POST':
        query = request.form.get('query', '')
        top_k = int(request.form.get('top_k', '15'))
        
        # Get minimum score threshold from form
        min_score = float(request.form.get('min_score', '0.10'))
        
        # Extract filters from form
        gender = request.form.get('gender', '')
        emotion = request.form.get('emotion', '')
        race = request.form.get('race', '')
        
        # Add filters if provided
        if gender:
            filters['Gender'] = gender
        if emotion:
            filters['Emotion'] = emotion
        if race:
            filters['Race'] = race
            
        # Perform search with filters and minimum score threshold
        results = search_engine.search(query, top_k=top_k, filter_criteria=filters, min_score=min_score)
        
        # Convert image paths for display
        for result in results:
            # Get just the filename from the path
            filename = os.path.basename(result['image_path'])
            # Create a URL for the image
            result['image_url'] = url_for('static', filename=f'images/{filename}')
    
    # Get unique values for filter dropdowns
    genders = search_engine.df['gender'].unique().tolist()
    emotions = search_engine.df['emotion'].unique().tolist()
    races = search_engine.df['race'].unique().tolist()
    
    return render_template('index.html', 
                          results=results, 
                          query=query,
                          filters=filters,
                          genders=genders,
                          emotions=emotions,
                          races=races,
                          min_score=min_score)

if __name__ == '__main__':
    # Create static/images directory if it doesn't exist
    os.makedirs('static/images', exist_ok=True)
    
    # Copy images from mai/photographer_6 to static/images
    for filename in os.listdir(image_folder):
        src = os.path.join(image_folder, filename)
        dst = os.path.join('static/images', filename)
        if os.path.isfile(src) and not os.path.exists(dst):
            try:
                with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst:
                    f_dst.write(f_src.read())
                print(f"Copied {filename}")
            except Exception as e:
                print(f"Error copying {filename}: {e}")
    
    app.run(debug=True)
