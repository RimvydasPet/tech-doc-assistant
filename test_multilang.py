"""Test script for multi-language support."""
from language_handler import LanguageHandler
from logger import logger

def test_language_detection():
    """Test language detection functionality."""
    print("=" * 60)
    print("Testing Language Detection")
    print("=" * 60)
    
    handler = LanguageHandler()
    
    test_cases = [
        ("How do I create a pandas DataFrame?", "en"),
        ("¿Cómo crear un DataFrame de pandas?", "es"),
        ("Comment créer un DataFrame pandas?", "fr"),
        ("Wie erstelle ich einen pandas DataFrame?", "de"),
        ("如何创建pandas DataFrame？", "zh"),
        ("pandasのDataFrameを作成する方法は？", "ja"),
    ]
    
    for text, expected_lang in test_cases:
        detected = handler.detect_language(text)
        status = "✓" if detected == expected_lang else "✗"
        print(f"{status} Text: {text[:50]}")
        print(f"  Expected: {expected_lang}, Detected: {detected}")
        print()

def test_translation():
    """Test translation functionality."""
    print("=" * 60)
    print("Testing Translation")
    print("=" * 60)
    
    handler = LanguageHandler()
    
    # Test translation to English
    spanish_text = "¿Cuál es la última versión de numpy?"
    print(f"Original (Spanish): {spanish_text}")
    english_translation = handler.translate_to_english(spanish_text, "es")
    print(f"Translated to English: {english_translation}")
    print()
    
    # Test translation from English
    english_text = "pandas is a powerful data analysis library for Python."
    print(f"Original (English): {english_text}")
    
    for lang_code in ["es", "fr", "de", "zh", "ja"]:
        lang_name = handler.SUPPORTED_LANGUAGES[lang_code]["name"]
        translated = handler.translate_from_english(english_text, lang_code)
        print(f"  → {lang_name} ({lang_code}): {translated}")
    print()

def test_multilingual_query_processing():
    """Test complete multilingual query processing."""
    print("=" * 60)
    print("Testing Multilingual Query Processing")
    print("=" * 60)
    
    handler = LanguageHandler()
    
    queries = [
        "How do I use pandas merge?",
        "¿Cómo uso pandas merge?",
        "Comment utiliser pandas merge?",
    ]
    
    for query in queries:
        print(f"\nProcessing: {query}")
        result = handler.process_multilingual_query(query)
        print(f"  Detected Language: {result['language_name']} ({result['detected_language']})")
        print(f"  English Query: {result['english_query']}")
        print(f"  Needs Translation: {result['needs_translation']}")

def test_supported_languages():
    """Display all supported languages."""
    print("=" * 60)
    print("Supported Languages")
    print("=" * 60)
    
    languages = LanguageHandler.get_supported_languages()
    
    for code, info in languages.items():
        print(f"  {code}: {info['native']} ({info['name']})")
    
    print(f"\nTotal: {len(languages)} languages supported")

if __name__ == "__main__":
    print("\n🌍 Multi-Language Support Test Suite\n")
    
    try:
        test_supported_languages()
        print("\n")
        
        test_language_detection()
        print("\n")
        
        test_translation()
        print("\n")
        
        test_multilingual_query_processing()
        print("\n")
        
        print("=" * 60)
        print("✓ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during testing: {str(e)}")
        logger.error(f"Test error: {str(e)}")
