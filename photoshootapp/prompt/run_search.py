from image_search import ImageSearch

# Initialize the search engine
search_engine = ImageSearch('mai/image_captions.csv', 'mai/photographer_6')

# Run the search for "women smiling" directly in captions
query = "woman women smiling"  # Search for both singular and plural forms
results = search_engine.search(query, top_k=15)  # Increased from default 5 to 15 results

# Display results
print("\nSearch Results for 'women smiling':")
print("-" * 50)
for i, result in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(f"Image: {result['image_path']}")
    if 'exists' in result:
        print(f"Image exists: {'Yes' if result['exists'] else 'No'}")
    print(f"Caption: {result['caption']}")
    print(f"Similarity Score: {result['similarity_score']:.2f}")
    print(f"Emotion: {result['emotion']}")
    print(f"Demographics: {result['age']} year old {result['gender']}, {result['race']}")
    print("-" * 50)
