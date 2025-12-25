"""Language detection and translation handler for multi-language support."""
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from logger import logger
from config import GOOGLE_API_KEY, GOOGLE_MODEL


class LanguageHandler:
    """Handle language detection and translation using Google Gemini."""
    
    # Supported languages with their codes and native names
    SUPPORTED_LANGUAGES = {
        "en": {"name": "English", "native": "English"},
        "es": {"name": "Spanish", "native": "Español"},
        "fr": {"name": "French", "native": "Français"},
        "de": {"name": "German", "native": "Deutsch"},
        "zh": {"name": "Chinese", "native": "中文"},
        "ja": {"name": "Japanese", "native": "日本語"},
        "pt": {"name": "Portuguese", "native": "Português"},
        "ru": {"name": "Russian", "native": "Русский"},
        "it": {"name": "Italian", "native": "Italiano"},
        "ko": {"name": "Korean", "native": "한국어"},
    }
    
    def __init__(self):
        """Initialize the language handler with Gemini LLM."""
        self.llm = ChatGoogleGenerativeAI(
            model=GOOGLE_MODEL,
            temperature=0,
            google_api_key=GOOGLE_API_KEY
        )
        logger.info("Language handler initialized")
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text to detect language
            
        Returns:
            Language code (e.g., 'en', 'es', 'fr')
        """
        logger.info(f"Detecting language for text: {text[:50]}...")
        
        try:
            prompt = f"""Detect the language of the following text and return ONLY the ISO 639-1 language code (2 letters).
            
Supported codes: {', '.join(self.SUPPORTED_LANGUAGES.keys())}

Text: "{text}"

Return only the 2-letter code, nothing else."""

            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            detected_code = response.content.strip().lower()
            
            # Validate the detected code
            if detected_code in self.SUPPORTED_LANGUAGES:
                logger.info(f"Detected language: {detected_code}")
                return detected_code
            else:
                logger.warning(f"Invalid language code detected: {detected_code}. Defaulting to 'en'")
                return "en"
                
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}. Defaulting to 'en'")
            return "en"
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        """
        Translate text from source language to English.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            
        Returns:
            Translated text in English
        """
        # If already English, return as-is
        if source_lang == "en":
            return text
        
        logger.info(f"Translating from {source_lang} to English")
        
        try:
            source_lang_name = self.SUPPORTED_LANGUAGES.get(source_lang, {}).get("name", source_lang)
            
            prompt = f"""Translate the following text from {source_lang_name} to English.
Return ONLY the translated text, nothing else.

Text to translate: "{text}"

Translation:"""

            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            translated = response.content.strip()
            logger.info(f"Translation successful: {translated[:50]}...")
            return translated
            
        except Exception as e:
            logger.error(f"Error translating to English: {str(e)}")
            return text  # Return original text on error
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        """
        Translate text from English to target language.
        
        Args:
            text: English text to translate
            target_lang: Target language code
            
        Returns:
            Translated text in target language
        """
        # If target is English, return as-is
        if target_lang == "en":
            return text
        
        logger.info(f"Translating from English to {target_lang}")
        
        try:
            target_lang_name = self.SUPPORTED_LANGUAGES.get(target_lang, {}).get("name", target_lang)
            
            prompt = f"""Translate the following text from English to {target_lang_name}.
Return ONLY the translated text, nothing else.
Maintain all markdown formatting, code blocks, and technical terms.

Text to translate: "{text}"

Translation:"""

            messages = [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            translated = response.content.strip()
            logger.info(f"Translation successful: {translated[:50]}...")
            return translated
            
        except Exception as e:
            logger.error(f"Error translating from English: {str(e)}")
            return text  # Return original text on error
    
    def process_multilingual_query(
        self, 
        user_message: str, 
        user_lang: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a multilingual query: detect language, translate to English.
        
        Args:
            user_message: User's message in any supported language
            user_lang: Optional user-specified language code
            
        Returns:
            Dictionary with detected language, original message, and English translation
        """
        logger.info("Processing multilingual query")
        
        # Detect language if not specified
        if user_lang is None:
            detected_lang = self.detect_language(user_message)
        else:
            detected_lang = user_lang if user_lang in self.SUPPORTED_LANGUAGES else "en"
        
        # Translate to English for RAG processing
        english_query = self.translate_to_english(user_message, detected_lang)
        
        return {
            "original_message": user_message,
            "detected_language": detected_lang,
            "language_name": self.SUPPORTED_LANGUAGES[detected_lang]["name"],
            "english_query": english_query,
            "needs_translation": detected_lang != "en"
        }
    
    def process_multilingual_response(
        self, 
        english_response: str, 
        target_lang: str
    ) -> str:
        """
        Translate response from English to target language.
        
        Args:
            english_response: Response in English
            target_lang: Target language code
            
        Returns:
            Translated response
        """
        logger.info(f"Processing response for language: {target_lang}")
        
        if target_lang == "en":
            return english_response
        
        return self.translate_from_english(english_response, target_lang)
    
    @classmethod
    def get_supported_languages(cls) -> Dict[str, Dict[str, str]]:
        """Get list of supported languages."""
        return cls.SUPPORTED_LANGUAGES
