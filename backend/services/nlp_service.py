import re
import logging
import torch
from transformers import AutoTokenizer, AutoModel, pipeline

logger = logging.getLogger(__name__)

# Basic English stopwords list
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for",
    "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's",
    "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll", "i'm",
    "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's", "me", "more", "most", "mustn't",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't",
    "so", "some", "such", "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't",
    "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's",
    "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
    "yourselves", "event", "description", "conference", "meetup", "summit", "workshop", "networking", "assistant",
    "personalized", "smart", "starters"
}

class NLPService:
    def __init__(self, theme_model_name="distilbert-base-uncased", gen_model_name="gpt2"):
        self.theme_model_name = theme_model_name
        self.gen_model_name = gen_model_name
        self.tokenizer = None
        self.model = None
        self.generator = None
        self.models_loaded = False
        self.use_fallback = False

    def load_models(self):
        """Lazy load NLP models to save startup time and memory."""
        if self.models_loaded or self.use_fallback:
            return

        try:
            logger.info("Initializing DistilBERT for theme extraction...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.theme_model_name)
            self.model = AutoModel.from_pretrained(self.theme_model_name)
            
            logger.info("Initializing GPT-2 pipeline for text generation...")
            # Using clean_up_tokenization_spaces to avoid warning
            self.generator = pipeline(
                "text-generation", 
                model=self.gen_model_name,
                clean_up_tokenization_spaces=True
            )
            
            self.models_loaded = True
            logger.info("NLP models loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load NLP models: {e}. Falling back to template-based generator.", exc_info=True)
            self.use_fallback = True

    def extract_themes(self, event_description: str, top_n: int = 3) -> list[str]:
        """
        Extract key themes using DistilBERT token embeddings similarity (KeyBERT-style).
        Falls back to rule-based keyword extraction if models are not loaded/fail.
        """
        if not event_description.strip():
            return []

        # Extract candidate words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', event_description.lower())
        candidates = list(set([w for w in words if w not in STOPWORDS]))

        if not candidates:
            return ["networking", "collaboration"]

        # If models failed to load, use a simple frequency-based fallback
        if self.use_fallback:
            return candidates[:top_n]

        try:
            self.load_models()
            if self.use_fallback: # check again in case load_models failed
                return candidates[:top_n]

            # 1. Compute full text embedding (CLS token)
            inputs = self.tokenizer(event_description, return_tensors="pt", truncation=True, padding=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
            doc_embedding = outputs.last_hidden_state[0, 0]  # CLS token representation [768]

            # 2. Compute embedding for each candidate word
            candidate_similarities = []
            for word in candidates:
                word_inputs = self.tokenizer(word, return_tensors="pt")
                with torch.no_grad():
                    word_outputs = self.model(**word_inputs)
                word_embedding = word_outputs.last_hidden_state[0, 0]  # CLS token [768]

                # Cosine similarity
                similarity = torch.nn.functional.cosine_similarity(
                    doc_embedding.unsqueeze(0), 
                    word_embedding.unsqueeze(0)
                ).item()
                candidate_similarities.append((word, similarity))

            # 3. Sort by similarity
            candidate_similarities.sort(key=lambda x: x[1], reverse=True)
            themes = [word.capitalize() for word, _ in candidate_similarities[:top_n]]
            return themes

        except Exception as e:
            logger.warning(f"Error in theme extraction: {e}. Using fallback strategy.")
            return [c.capitalize() for c in candidates[:top_n]]

    def generate_starters(self, event_description: str, themes: list[str], interests: list[str]) -> list[str]:
        """
        Generate 3 networking conversation starters using GPT-2.
        Falls back to rule-based starter templates if models fail.
        """
        # Clean inputs
        themes_clean = [t.strip() for t in themes if t.strip()]
        interests_clean = [i.strip() for i in interests if i.strip()]

        if not themes_clean:
            themes_clean = ["Networking"]
        if not interests_clean:
            interests_clean = ["collaboration"]

        # Heuristic fallback generator
        fallback_starters = [
            f"Hi there! Are you attending the sessions on {themes_clean[0]}? I'm quite passionate about {interests_clean[0]} and would love to hear your perspective.",
            f"Hello! I noticed this event focuses a lot on {themes_clean[-1] if len(themes_clean) > 1 else themes_clean[0]}. How are you applying that in your own work?",
            f"Hi! Great to meet you. I'm focusing on {interests_clean[-1] if len(interests_clean) > 1 else interests_clean[0]} here today. What are your main goals for this event?"
        ]

        if self.use_fallback:
            return fallback_starters

        try:
            self.load_models()
            if self.use_fallback:
                return fallback_starters

            # Craft prompt for GPT-2
            prompt = (
                f"Event: {event_description}\n"
                f"Themes: {', '.join(themes_clean)}\n"
                f"Interests: {', '.join(interests_clean)}\n"
                f"Write exactly 3 professional conversation starters for this event.\n"
                f"1."
            )

            # Generate starters
            # Setting pad_token_id to eos_token_id to suppress warnings
            outputs = self.generator(
                prompt, 
                max_new_tokens=90, 
                num_return_sequences=1,
                temperature=0.7, 
                do_sample=True,
                pad_token_id=self.generator.model.config.eos_token_id
            )

            generated_text = outputs[0]["generated_text"]
            # Extract only the generated content after the prompt
            new_content = generated_text[len(prompt)-2:].strip() # start around the '1.'

            # Parse lines into list
            starters = []
            # Look for numbered items: 1. ..., 2. ..., 3. ...
            lines = re.split(r'\n+', new_content)
            for line in lines:
                # Strip prefix like "1. ", "2) ", "- " etc.
                cleaned = re.sub(r'^(\d+[\.\)]|\-)\s*', '', line.strip())
                # Remove quotes if present
                cleaned = cleaned.strip('"\'')
                if cleaned and len(cleaned) > 15: # Filter out short fragments
                    starters.append(cleaned)
                if len(starters) == 3:
                    break

            # If parser failed to find 3 valid starters, inject fallback templates
            while len(starters) < 3:
                starters.append(fallback_starters[len(starters)])

            return starters

        except Exception as e:
            logger.warning(f"Error in conversation starter generation: {e}. Using fallback strategy.")
            return fallback_starters

# Global service instance
nlp_service = NLPService()
