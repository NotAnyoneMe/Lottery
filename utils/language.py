"""
Language support utilities for the Telegram Lottery Bot.
Handles language detection, translation loading, and user language management.
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Any
import logging

# Language mapping from Telegram language codes to our language keys
LANGUAGE_MAPPING = {
    'en': 'english',
    'ar': 'arabic', 
    'ru': 'russian',
    'es': 'spanish',
    'zh': 'chinese',
    'zh-cn': 'chinese',
    'zh-tw': 'chinese',
    # Add more mappings as needed
}

DEFAULT_LANGUAGE = 'english'

# Global variable to store loaded translations
_translations: Optional[Dict[str, Dict[str, str]]] = None

# In-memory storage for user languages (in production, use database)
_user_languages: Dict[int, str] = {}


def load_translations() -> Dict[str, Dict[str, str]]:
    """Load translations from language.json file."""
    global _translations
    
    if _translations is not None:
        return _translations
    
    # Find language.json file
    current_dir = Path(__file__).parent.parent
    language_file = current_dir / 'data' / 'language.json'
    
    try:
        with open(language_file, 'r', encoding='utf-8') as f:
            _translations = json.load(f)
        logging.info(f"Loaded translations for {len(_translations)} languages")
        return _translations
    except FileNotFoundError:
        logging.error(f"Language file not found: {language_file}")
        # Return minimal English translations as fallback
        _translations = {
            'english': {
                'welcome': 'Welcome to Lottery Bot!',
                'add_me': 'Add Me ➕',
                'updates': 'Bot Updates 🔔'
            }
        }
        return _translations
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing language file: {e}")
        _translations = {'english': {'welcome': 'Welcome to Lottery Bot!'}}
        return _translations


def get_user_lang(language_code: Optional[str]) -> str:
    """
    Detect user language from Telegram language code.
    
    Args:
        language_code: Telegram user language code (e.g., 'en', 'ar', 'ru')
        
    Returns:
        Language key that exists in our translations
    """
    if not language_code:
        return DEFAULT_LANGUAGE
    
    # Convert to lowercase and check direct mapping
    lang_code = language_code.lower()
    
    if lang_code in LANGUAGE_MAPPING:
        detected_lang = LANGUAGE_MAPPING[lang_code]
        
        # Verify the language exists in our translations
        translations = load_translations()
        if detected_lang in translations:
            return detected_lang
    
    # Fallback to default language
    return DEFAULT_LANGUAGE


def set_user_language(user_id: int, language: str) -> None:
    """
    Save user's preferred language.
    
    Args:
        user_id: Telegram user ID
        language: Language key
    """
    global _user_languages
    _user_languages[user_id] = language
    logging.info(f"Set language for user {user_id}: {language}")


def get_user_language(user_id: int) -> str:
    """
    Get user's saved language preference.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        User's preferred language or default language
    """
    return _user_languages.get(user_id, DEFAULT_LANGUAGE)


def get_text(user_id: int, key: str, **kwargs) -> str:
    """
    Get translated text for a user.
    
    Args:
        user_id: Telegram user ID
        key: Translation key
        **kwargs: Format parameters for the text
        
    Returns:
        Translated and formatted text
    """
    user_lang = get_user_language(user_id)
    translations = load_translations()
    
    # Get the translation
    if user_lang in translations and key in translations[user_lang]:
        text = translations[user_lang][key]
    elif DEFAULT_LANGUAGE in translations and key in translations[DEFAULT_LANGUAGE]:
        text = translations[DEFAULT_LANGUAGE][key]
        logging.warning(f"Translation key '{key}' not found for language '{user_lang}', using default")
    else:
        logging.error(f"Translation key '{key}' not found in any language")
        return f"[Missing translation: {key}]"
    
    # Format the text with provided parameters
    try:
        return text.format(**kwargs)
    except KeyError as e:
        logging.error(f"Missing format parameter {e} for key '{key}'")
        return text
    except Exception as e:
        logging.error(f"Error formatting text for key '{key}': {e}")
        return text


def get_available_languages() -> list:
    """Get list of available language keys."""
    translations = load_translations()
    return list(translations.keys())


def is_language_available(language: str) -> bool:
    """Check if a language is available in translations."""
    translations = load_translations()
    return language in translations