import os, base64, io
from dotenv import load_dotenv
load_dotenv()

def capture_screen_b64() -> str:
    try:
        import pyautogui
        img = pyautogui.screenshot()
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode()
    except Exception as e:
        return f"Erreur capture ecran: {e}"

def capture_camera_b64(camera_index=0) -> str:
    try:
        import cv2
        cap = cv2.VideoCapture(camera_index)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return "Pas de camera detectee (lunettes M01 Pro sans flux USB ?)"
        _, buf = cv2.imencode('.jpg', frame)
        return base64.b64encode(buf).decode()
    except Exception as e:
        return f"Erreur camera: {e}. Installe opencv: pip install opencv-python"

def ask_vision(question: str, image_b64: str, use_screen=True) -> str:
    """Envoie image + question a GPT-4o Vision via OpenRouter"""
    try:
        from openai import OpenAI
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        client = OpenAI(api_key=api_key, base_url=base_url, default_headers={"HTTP-Referer":"https://sara.local","X-Title":"SARA Vision"})
        # Si c'est une erreur string, retourne
        if image_b64.startswith("Erreur") or image_b64.startswith("Pas de"):
            return image_b64
        resp = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            max_tokens=800,
            messages=[{
                "role":"user",
                "content":[
                    {"type":"text","text": question},
                    {"type":"image_url","image_url":{"url": f"data:image/png;base64,{image_b64}"}}
                ]
            }]
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Erreur Vision: {e}"

def see_screen(question="Que vois-tu sur l'ecran ? Decris en francais et aide."):
    b64 = capture_screen_b64()
    return ask_vision(question, b64)

def see_camera(question="Que vois-tu via la camera des lunettes ? Decris et aide."):
    b64 = capture_camera_b64()
    return ask_vision(question, b64)
