import os, importlib.util
PLUGINS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")

def load_plugins():
    """Charge tous les .py dans plugins/ comme nouveaux outils JARVIS"""
    tools = []
    mapping = {}
    if not os.path.exists(PLUGINS_DIR):
        os.makedirs(PLUGINS_DIR, exist_ok=True)
        with open(os.path.join(PLUGINS_DIR, "exemple.py"), "w", encoding="utf-8") as f:
            f.write('''# Exemple plugin JARVIS
# Nom de fonction = nom de l'outil. Description dans le docstring.
def salut_perso(nom: str) -> str:
    """Dit bonjour de facon perso"""
    return f"Salut {nom}, c'est JARVIS !"
''')
        return tools, mapping
    for fname in os.listdir(PLUGINS_DIR):
        if not fname.endswith(".py") or fname.startswith("_"):
            continue
        path = os.path.join(PLUGINS_DIR, fname)
        spec = importlib.util.spec_from_file_location(fname[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
            for name in dir(mod):
                fn = getattr(mod, name)
                if callable(fn) and not name.startswith("_"):
                    # docstring = description
                    desc = (fn.__doc__ or f"Plugin {name}").strip().split("\n")[0]
                    # introspection simple des args
                    import inspect
                    sig = inspect.signature(fn)
                    props = {}
                    for pname, param in sig.parameters.items():
                        props[pname] = {"type": "string"}
                    tools.append({"type":"function","function":{"name":name,"description":desc,"parameters":{"type":"object","properties":props,"required":list(props.keys())}}})
                    mapping[name] = fn
        except Exception as e:
            print(f"[Plugins] {fname} erreur: {e}")
    return tools, mapping

def list_plugins():
    _, m = load_plugins()
    return list(m.keys())
