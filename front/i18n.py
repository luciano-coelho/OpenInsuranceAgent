"""
Internationalization (i18n) wrapper using python-i18n.
Provides a stable `i18n.t(key, **kwargs)` API for the app.
"""

from pathlib import Path
import i18n as ext_i18n


LOCALES_DIR = Path(__file__).parent / "locales"


def _configure_i18n(default_locale: str = "pt_BR") -> None:
    """Configure python-i18n with project locales and defaults."""
    # Ensure load path includes our locales dir
    ext_i18n.load_path.clear()
    ext_i18n.load_path.append(str(LOCALES_DIR))
    # Set default and current locale
    ext_i18n.set("fallback", "pt_BR")
    ext_i18n.set("locale", default_locale)
    # Use dot-notation keys like "upload.section"
    ext_i18n.set("filename_format", "{locale}.{format}")
    ext_i18n.set("available_locales", ["pt_BR", "en_US"])


class I18n:
    """Small facade around python-i18n to keep a clear app-facing API."""

    def __init__(self, language: str = "pt_BR") -> None:
        _configure_i18n(language)

    def t(self, key: str, **kwargs) -> str:
        """Translate a key for the current locale."""
        return ext_i18n.t(key, **kwargs)

    def set_language(self, language: str) -> None:
        """Switch to a different language (e.g., "en_US")."""
        ext_i18n.set("locale", language)


# Global instance (defaults to Portuguese for UX)
i18n = I18n("pt_BR")
