import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from pathlib import Path
import re
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import nltk

# Download required NLTK data
try:
    nltk.data.find('corpora/wordnet')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('wordnet')
    nltk.download('stopwords')

class ImageSearch:
    def __init__(self, csv_path, image_folder):
        self.df = pd.read_csv(csv_path)
        self.image_folder = image_folder
        
        # Initialize the lemmatizer
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Clean and prepare the captions
        self.df['caption'] = self.df['caption'].fillna('')
        
        # Preprocess the captions
        self.df['processed_caption'] = self.df['caption'].apply(self.preprocess_text)
        
        # Create searchable text that includes all metadata
        self.df['search_text'] = self.df.apply(
            lambda row: f"{row['processed_caption']} {row['gender'].lower()} {row['emotion'].lower()} {row['race'].lower()}", 
            axis=1
        )
        
        # Create a separate vectorizer for exact matching
        self.exact_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams
            min_df=1,
            use_idf=True,
            norm='l2'
        )
        
        # Create a separate vectorizer for semantic matching
        self.semantic_vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 1),  # Only unigrams for semantic
            min_df=1,
            use_idf=True,
            norm='l2'
        )
        
        # Create TF-IDF matrices
        self.exact_tfidf_matrix = self.exact_vectorizer.fit_transform(self.df['search_text'])
        self.semantic_tfidf_matrix = self.semantic_vectorizer.fit_transform(self.df['search_text'])
        
        # Update image paths to use the new image folder
        self.df['local_path'] = self.df['image_path'].apply(
            lambda x: os.path.join(self.image_folder, os.path.basename(x.replace('\\', '/').split('/')[-1]))
        )
        
        # Verify images exist
        self.df['image_exists'] = self.df['local_path'].apply(
            lambda x: os.path.exists(x)
        )
        print(f"Found {self.df['image_exists'].sum()} of {len(self.df)} images in {image_folder}")
    
    def preprocess_text(self, text):
        """Preprocess text by lowercasing, removing special chars, and lemmatizing"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # Tokenize
        tokens = text.split()
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        
        # Join tokens back to string
        return ' '.join(tokens)
    
    def parse_query(self, query):
        """Parse query to extract filters and search terms"""
        # Initialize filters
        filters = {}
        
        # Extract terms with format key:value
        filter_pattern = r'(\w+):(\w+)'
        filter_matches = re.findall(filter_pattern, query)
        
        # Process filter terms
        for key, value in filter_matches:
            if key.lower() in ['gender', 'emotion', 'race']:
                filters[key.capitalize()] = value.capitalize()
        
        # Remove filter terms from query
        clean_query = re.sub(filter_pattern, '', query).strip()
        
        # Preprocess the query
        processed_query = self.preprocess_text(clean_query)
        
        return processed_query, filters
    
    def search(self, query, top_k=5, filter_criteria=None, min_score=0.10):
        """
        Search for images based on query and optional filters
        
        Parameters:
        -----------
        query : str
            The search query
        top_k : int
            Number of results to return
        filter_criteria : dict
            Optional filters like {'gender': 'Woman', 'emotion': 'happy'}
        min_score : float
            Minimum similarity score threshold (0.0 to 1.0)
        """
        # Parse query if filter_criteria not provided
        if not filter_criteria:
            processed_query, extracted_filters = self.parse_query(query)
            filter_criteria = extracted_filters
        else:
            processed_query = self.preprocess_text(query)
        
        # Apply filters
        filtered_df = self.df.copy()
        for key, value in filter_criteria.items():
            if key in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[key].str.lower() == value.lower()]
        
        # If no results after filtering, return empty list
        if len(filtered_df) == 0:
            return []
        
        # Create mask for filtered indices
        mask = np.zeros(len(self.df), dtype=bool)
        mask[filtered_df.index] = True
        
        # Extract key terms from the query
        query_terms = processed_query.split()
        
        # Check for specific gender terms in the query
        gender_terms = {'woman', 'women', 'female', 'girl', 'lady', 'man', 'men', 'male', 'boy', 'guy'}
        has_gender_term = any(term in gender_terms for term in query_terms)
        
        # If query has gender terms but no gender filter, add implicit gender filter
        if has_gender_term and 'Gender' not in filter_criteria:
            for term in query_terms:
                if term in {'woman', 'women', 'female', 'girl', 'lady'}:
                    # Apply additional mask for women
                    gender_mask = self.df['gender'].str.lower() == 'woman'
                    mask = mask & gender_mask
                    break
                elif term in {'man', 'men', 'male', 'boy', 'guy'}:
                    # Apply additional mask for men
                    gender_mask = self.df['gender'].str.lower() == 'man'
                    mask = mask & gender_mask
                    break
        
        # Transform the query using both vectorizers
        exact_query_vector = self.exact_vectorizer.transform([processed_query])
        semantic_query_vector = self.semantic_vectorizer.transform([processed_query])
        
        # Calculate similarity scores
        exact_scores = cosine_similarity(exact_query_vector, self.exact_tfidf_matrix)[0]
        semantic_scores = cosine_similarity(semantic_query_vector, self.semantic_tfidf_matrix)[0]
        
        # Combine scores with more weight on exact matches
        combined_scores = 0.7 * exact_scores + 0.3 * semantic_scores
        
        # Apply mask to similarity scores
        masked_scores = combined_scores.copy()
        masked_scores[~mask] = -1
        
        # Get top k matches
        df_with_scores = self.df.copy()
        df_with_scores['similarity'] = masked_scores
        
        # Sort by existence and similarity
        df_with_scores = df_with_scores.sort_values(
            by=['image_exists', 'similarity'], 
            ascending=[False, False]
        )
        
        # Filter out negative scores (from mask) and scores below threshold
        df_with_scores = df_with_scores[(df_with_scores['similarity'] >= min_score)]
        
        # Get top k indices
        top_indices = df_with_scores.index[:top_k]
        
        # Return results
        results = []
        for idx in top_indices:
            results.append({
                'image_path': self.df['local_path'].iloc[idx],
                'caption': self.df['caption'].iloc[idx],
                'similarity_score': combined_scores[idx],
                'emotion': self.df['emotion'].iloc[idx],
                'age': self.df['age'].iloc[idx],
                'gender': self.df['gender'].iloc[idx],
                'race': self.df['race'].iloc[idx],
                'exists': self.df['image_exists'].iloc[idx]
            })
        
        return results

# Example usage
if __name__ == "__main__":
    csv_path = "mai/image_captions.csv"
    image_folder = "mai/photographer_6"
    
    # Initialize the search engine
    search_engine = ImageSearch(csv_path, image_folder)
    
    while True:
        try:
            # Example search
            query = input("\nEnter your search query (or 'quit' to exit): ")
            if query.lower() == 'quit':
                break
            
            # Perform search
            results = search_engine.search(query)
            
            # Display results
            print("\nSearch Results:")
            print("-" * 50)
            if not results:
                print("No results found matching your criteria.")
            else:
                for i, result in enumerate(results, 1):
                    print(f"\nResult {i}:")
                    print(f"Image: {result['image_path']}")
                    print(f"Image exists: {'Yes' if result['exists'] else 'No'}")
                    print(f"Caption: {result['caption']}")
                    print(f"Similarity Score: {result['similarity_score']:.2f}")
                    print(f"Emotion: {result['emotion']}")
                    print(f"Demographics: {result['age']} year old {result['gender']}, {result['race']}")
                    print("-" * 50)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
