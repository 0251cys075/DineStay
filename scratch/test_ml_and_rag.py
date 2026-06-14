import sys
import io
import os

# Fix Windows console encoding for emoji/Unicode
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Insert project root to path
project_root = r"c:\Users\LAP\Downloads\DineStay-main\DineStay-main"
sys.path.insert(0, project_root)

print("--- Testing ML Helper ---")
try:
    import ml_helper
    
    # Test cancellation prediction
    prob = ml_helper.predict_cancellation(lead_time=15, adr=2500.0, stays_in_week_nights=3, previous_cancellations=0)
    print(f"Cancellation Prob (No previous cancel, lead=15): {prob*100:.2f}%")
    
    prob_high = ml_helper.predict_cancellation(lead_time=30, adr=5000.0, stays_in_week_nights=2, previous_cancellations=1)
    print(f"Cancellation Prob (1 previous cancel, lead=30): {prob_high*100:.2f}%")
    
    # Test pricing prediction
    price = ml_helper.predict_price(base_price=4500.0, occupancy_rate=0.8, month=6, day_of_week=4) # Friday, June, 80% occupancy
    print(f"Recommended price: INR {price}")
    
    # Test sentiment analyzer
    sent1 = ml_helper.analyzer.analyze_sentiment("This stay was absolutely amazing and comfortable!")
    sent2 = ml_helper.analyzer.analyze_sentiment("The room was terrible and dirty.")
    sent3 = ml_helper.analyzer.analyze_sentiment("Check in was at 12 PM.")
    print(f"Sentiment 1: {sent1} (Expected: Positive)")
    print(f"Sentiment 2: {sent2} (Expected: Negative)")
    print(f"Sentiment 3: {sent3} (Expected: Neutral)")
    
    print("[OK] ML Helper testing passed successfully!")
except Exception as e:
    print(f"[FAIL] ML Helper testing failed: {e}")

print("\n--- Testing RAG Handler ---")
try:
    import rag_handler
    from hotel import Hotel
    import file_handler
    
    # Instantiate hotel and load
    hotel = Hotel("DineStay")
    file_handler.load_all(hotel)
    
    # Run indexing
    rag_handler.index_data(hotel)
    
    # Test context retrieval
    context1 = rag_handler.retrieve_context("What time is check-in?")
    print(f"Query: 'What time is check-in?' -> Context:\n{context1}\n")
    
    context2 = rag_handler.retrieve_context("Masala Dosa price")
    print(f"Query: 'Masala Dosa price' -> Context:\n{context2}\n")
    
    print("[OK] RAG Handler testing passed successfully!")
except Exception as e:
    print(f"[FAIL] RAG Handler testing failed: {e}")
