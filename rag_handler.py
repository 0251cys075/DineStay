import math
import re

document_chunks = []
idf_dict = {}
tfidf_docs = [] # list of dicts: {token: score}

def tokenize(text):
    text = text.lower()
    # Extract alpha-numeric words
    return re.findall(r'[a-z0-9]+', text)

def index_data(hotel_instance):
    """Rebuilds the pure Python TF-IDF search index from database and policies."""
    global document_chunks, idf_dict, tfidf_docs
    
    chunks = []
    
    # 1. Ingest Rooms
    for room in hotel_instance.rooms:
        status = "available" if room.availability_status else "booked"
        chunks.append(f"Room {room.room_number} is a {room.room_type} room priced at INR {room.room_price} per night. Currently {status}.")
        
    # 2. Ingest Menu Items
    for item in hotel_instance.menu:
        chunks.append(f"{item.food_name} is a {item.category} item priced at INR {item.price}.")
        
    # 3. Add Static FAQs & Policies
    chunks.extend([
        "DineStay check-in time is 12:00 PM and check-out time is 11:00 AM.",
        "DineStay restaurant is open from 7:00 AM to 11:00 PM daily.",
        "Free Wi-Fi is available in all rooms and public hotel areas.",
        "Our hotel offers a 100% refund for room cancellations made 24 hours before check-in.",
        "We offer a wide variety of rooms including Deluxe rooms, Standard rooms, and premium suites.",
        "Deluxe rooms feature king-size beds, a private balcony, and flat-screen TVs.",
        "Standard rooms feature queen-size beds and a city view, starting at affordable rates.",
        "For room bookings or help, customers can contact front desk manager Suresh Kumar.",
        "For restaurant queries or special food orders, contact executive chef Anita Nair."
    ])
    
    document_chunks = chunks
    
    if not chunks:
        return
        
    # Compute vocabulary and term frequencies
    doc_tokens = [tokenize(doc) for doc in chunks]
    
    # Calculate DF (document frequency) for each word
    df_dict = {}
    for tokens in doc_tokens:
        unique_tokens = set(tokens)
        for token in unique_tokens:
            df_dict[token] = df_dict.get(token, 0) + 1
            
    # Calculate IDF (inverse document frequency)
    N = len(chunks)
    idf_dict = {}
    for token, df in df_dict.items():
        # Smoothed IDF formula matching standard scikit-learn behavior
        idf_dict[token] = math.log((1 + N) / (1 + df)) + 1
        
    # Calculate TF-IDF vectors for documents
    tfidf_docs = []
    for tokens in doc_tokens:
        if not tokens:
            tfidf_docs.append({})
            continue
            
        tf_dict = {}
        for token in tokens:
            tf_dict[token] = tf_dict.get(token, 0) + 1
            
        tfidf_doc = {}
        for token, count in tf_dict.items():
            tf = count / len(tokens)
            tfidf_doc[token] = tf * idf_dict[token]
        tfidf_docs.append(tfidf_doc)
        
    print(f"Indexed {len(chunks)} text chunks for RAG search (Pure Python TF-IDF).")

def cosine_similarity_pure(vec_a, vec_b):
    """Calculates cosine similarity between two dict sparse vectors."""
    dot_product = 0.0
    for token, val_a in vec_a.items():
        if token in vec_b:
            dot_product += val_a * vec_b[token]
            
    # Norms
    norm_a = math.sqrt(sum(val ** 2 for val in vec_a.values()))
    norm_b = math.sqrt(sum(val ** 2 for val in vec_b.values()))
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
        
    return dot_product / (norm_a * norm_b)

def retrieve_context(user_query, top_k=3):
    global document_chunks, idf_dict, tfidf_docs
    if not document_chunks or not idf_dict or not tfidf_docs:
        return ""
        
    # Tokenize query
    query_tokens = tokenize(user_query)
    if not query_tokens:
        return ""
        
    # Calculate TF-IDF for query
    query_tf = {}
    for token in query_tokens:
        query_tf[token] = query_tf.get(token, 0) + 1
        
    query_vec = {}
    for token, count in query_tf.items():
        if token in idf_dict:
            tf = count / len(query_tokens)
            query_vec[token] = tf * idf_dict[token]
            
    # Compute similarities with all document vectors
    similarities = []
    for doc_vec in tfidf_docs:
        sim = cosine_similarity_pure(query_vec, doc_vec)
        similarities.append(sim)
        
    # Get top-k indices based on similarity score
    sorted_indices = sorted(range(len(similarities)), key=lambda idx: similarities[idx], reverse=True)
    top_indices = sorted_indices[:top_k]
    
    # Filter for positive similarity matching
    retrieved = [document_chunks[idx] for idx in top_indices if similarities[idx] > 0.05]
    
    return "\n".join(retrieved)
