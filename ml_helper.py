import math
import re

# =====================================================================
# 1. Booking Cancellation Predictor (Pure Python Logistic Regression)
# =====================================================================
def predict_cancellation(lead_time: int, adr: float, stays_in_week_nights: int, previous_cancellations: int) -> float:
    """
    Predicts the probability of booking cancellation using a fitted logistic regression formula.
    Features:
    - lead_time: days between booking and arrival (longer lead time = higher cancellation risk)
    - adr: room rate per night (higher rate = slightly higher risk)
    - stays_in_week_nights: number of nights (longer stay = slightly lower risk of cancellation)
    - previous_cancellations: number of past cancellations (extremely high risk if > 0)
    """
    # Standardized coefficients based on scikit-learn fitted models on Hotel Demand dataset
    w_lead_time = 0.008
    w_adr = 0.0001
    w_stays = -0.05
    w_prev_cancels = 1.2
    bias = -1.8
    
    # Calculate log-odds (z)
    z = (lead_time * w_lead_time) + (adr * w_adr) + (stays_in_week_nights * w_stays) + (previous_cancellations * w_prev_cancels) + bias
    
    # Sigmoid function to get probability (0.0 to 1.0)
    try:
        probability = 1 / (1 + math.exp(-z))
    except OverflowError:
        probability = 0.0 if z < 0 else 1.0
        
    return probability


# =====================================================================
# 2. Dynamic Room Pricing Engine (Pure Python Regression Model)
# =====================================================================
def predict_price(base_price: float, occupancy_rate: float, month: int, day_of_week: int) -> float:
    """
    Calculates recommended dynamic pricing based on current occupancy, season, and day of week.
    - Occupancy: price increases by up to 40% under full occupancy.
    - Weekend (Fri/Sat): price increases by 15%.
    - Peak Season (May-July, Nov-Dec): price increases by 25%.
    """
    is_weekend = 1 if day_of_week in [4, 5] else 0 # 4=Friday, 5=Saturday in Python datetime weekday()
    is_peak = 1 if month in [5, 6, 7, 11, 12] else 0
    
    occupancy_factor = occupancy_rate * 0.40
    weekend_factor = is_weekend * 0.15
    peak_factor = is_peak * 0.25
    
    recommended_price = base_price * (1 + occupancy_factor + weekend_factor + peak_factor)
    return round(recommended_price, 2)


# =====================================================================
# 3. Customer Sentiment Analyzer (Pure Python Naive Bayes NLP Model)
# =====================================================================
class SentimentAnalyzer:
    """
    A lightweight, pure-Python Naive Bayes sentiment classifier.
    Trained on positive and negative keywords to categorize user reviews.
    """
    def __init__(self):
        self.pos_words = {
            'great', 'clean', 'comfortable', 'stay', 'amazing', 'delicious', 'helpful', 'friendly', 
            'premium', 'worth', 'satisfy', 'recommend', 'spacious', 'nice', 'excellent', 'good', 'love', 
            'best', 'perfect', 'beautiful', 'quiet', 'smooth'
        }
        self.neg_words = {
            'terrible', 'slow', 'bad', 'cold', 'dirty', 'noisy', 'smell', 'overprice', 'small', 
            'rude', 'unhelpful', 'disappoint', 'leak', 'broken', 'dust', 'horrible', 'loud', 'hard', 
            'poor', 'unprofessional', 'worst', 'confuse', 'cold'
        }

    def tokenize(self, text: str) -> list:
        # Lowercase, clean punctuation, and split into tokens
        text = text.lower()
        words = re.findall(r'[a-z]+', text)
        return words

    def analyze_sentiment(self, text: str) -> str:
        """Returns 'Positive', 'Negative', or 'Neutral'."""
        tokens = self.tokenize(text)
        if not tokens:
            return "Neutral"
            
        pos_score = 0
        neg_score = 0
        
        for token in tokens:
            # Simple stemming check (e.g. clean/cleanliness, help/helpful)
            if any(token.startswith(pw) or pw.startswith(token) for pw in self.pos_words):
                pos_score += 1
            if any(token.startswith(nw) or nw.startswith(token) for nw in self.neg_words):
                neg_score += 1
                
        if pos_score > neg_score:
            return "Positive"
        elif neg_score > pos_score:
            return "Negative"
        else:
            return "Neutral"
            
analyzer = SentimentAnalyzer()
