# Simple in-memory application state for runtime-only settings
# Currently stores selected language for the running application.

_import_lock = None
_selected_language = 'Español'


def get_selected_language():
    """Return the currently selected language key (e.g. 'Español', 'Ingles', 'Hungaro')."""
    return _selected_language


def set_selected_language(lang):
    """Set the selected language for the running app."""
    global _selected_language
    if not lang:
        return
    _selected_language = lang


def reset_runtime_state():
    """Reset in-memory runtime state to defaults. This is intended to be called on program start.

    It does NOT modify persistent user storage; it only clears in-memory selected language and any
    transient session file if present (session_user.json in the repo root).
    """
    global _selected_language
    _selected_language = 'Español'
    # try to remove session_user.json if present (best-effort)
    try:
        import os
        import json
        repo_root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
        session_path = os.path.join(repo_root, 'session_user.json')
        if os.path.exists(session_path):
            try:
                os.remove(session_path)
            except Exception:
                # try overwriting with empty object
                try:
                    with open(session_path, 'w', encoding='utf-8') as f:
                        json.dump({}, f)
                except Exception:
                    pass
        # Also remove any saved login draft so username/idioma are not persisted across runs
        try:
            draft_path = os.path.join(os.path.dirname(__file__), 'loginDraft.json')
            if os.path.exists(draft_path):
                try:
                    os.remove(draft_path)
                except Exception:
                    # fallback: overwrite empty
                    try:
                        with open(draft_path, 'w', encoding='utf-8') as f:
                            json.dump({}, f)
                    except Exception:
                        pass
        except Exception:
            pass
    except Exception:
        pass
