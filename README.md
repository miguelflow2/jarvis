# JARVIS - Agent Vocal Complet

**Contrôle total de ton PC à la voix depuis tes lunettes Bluetooth.**

- 🎤 Vocal FR naturel (Whisper + Edge-TTS DeniseNeural)
- ☁️ Cerveau Cloud GPT-4o
- 🕶️ Bluetooth lunettes -> PC (auto-détection)
- ⚙️ Autonomie totale: cherche, installe, code s'il ne trouve pas

## Installation (2 min)

1. **Clé OpenAI:**
   ```powershell
   Copy-Item .env.example .env
   # Edite .env et colle ta clé https://platform.openai.com/api-keys
   notepad .env
   ```

2. **Dépendances:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Appaire tes lunettes en Bluetooth:**
   Windows > Paramètres > Bluetooth > Ajouter > Tes lunettes -> Connecté (doit apparaître comme Casque)

4. **Lance JARVIS:**
   ```powershell
   python jarvis.py
   ```
   Parle dans tes lunettes: "Jarvis ouvre Chrome" -> il s'exécute et te répond dans les lunettes.

## Commandes exemples

- "Jarvis ouvre Spotify et mets du jazz"
- "Jarvis ferme tout"
- "Jarvis cherche et installe Blender"
- "Jarvis crée moi un script python qui trie mes photos"
- "Jarvis montre moi l'état du système"
- "Jarvis va sur youtube.com"
- "Jarvis capture mon écran"

## Dépannage Bluetooth

```powershell
python -c "from core.bluetooth import print_diagnostic; print_diagnostic()"
python -c "from core.voice import list_microphones; list_microphones()"
```
- Si lunettes non détectées: vérifie qu'elles sont bien en mode "Casque" et pas seulement "Audio"
- Dans Windows Son > Entrée > choisis tes lunettes comme micro par défaut

## Structure

```
JARVIS/
  jarvis.py          # Lanceur principal vocal
  core/brain.py      # Cerveau GPT-4o + tools
  core/voice.py      # STT Whisper + TTS FR
  core/bluetooth.py  # Détection lunettes
  core/tools/        # Contrôle PC complet
  config/config.json
```
