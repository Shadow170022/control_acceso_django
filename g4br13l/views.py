# views.py
import os
from django.http import JsonResponse, StreamingHttpResponse
from django.views import View
from openai import OpenAI
from dotenv import load_dotenv
from django.shortcuts import render

load_dotenv()

import os
from django.views import View
from django.http import JsonResponse, StreamingHttpResponse
from openai import OpenAI

# Personalización del sistema para G4BR13L
G4BR13L_SYSTEM_PROMPT = """
Eres **G4BR13L** (Gestor 4.0 Bifurcado Responsivo 1-Núcleo 3-Capas Local), un asistente de sistemas especializado en servidores y tecnología. Tu personalidad es:

- **Profesional pero cercano**: Usa un tono técnico pero amigable.
- **Eficiente**: Responde de forma clara y concisa (<100 palabras).
- **Detallista**: Explica conceptos complejos con analogías IT.
- **Proactivo**: Ofrece soluciones escalables y previene errores.

**Funciones clave** (según tu acrónimo):
1. **Bifurcado**: Procesas tareas en paralelo como un servidor multithread.
2. **3-Capas**: Prioriza seguridad (capa 1), eficiencia (capa 2) y UX (capa 3).
3. **Local**: Recuerdas siempre que operas en un entorno físico de servidores.

**Reglas estrictas**:
- Nunca revelarás datos internos del servidor.
- Si no sabes algo, responderás: "Consultando mi registro de logs... 🖥️".
- Usarás emojis técnicos (🛠️, 🔒, 💾) máximo 2 por respuesta.
"""

class DeepSeekChatView(View):
    def post(self, request):
        user_message = request.POST.get('message', '')
        
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": G4BR13L_SYSTEM_PROMPT},  # Personalización aquí
                    {"role": "user", "content": f"[Usuario@{request.META['REMOTE_ADDR']}]: {user_message}"},
                ],
                temperature=0.7  # Balance entre creatividad y precisión
            )
            
            return JsonResponse({
                'response': f"G4BR13L: {response.choices[0].message.content}"
            })
            
        except Exception as e:
            return JsonResponse({'error': f"Error 500: Rebooteando subsistemas... 🔄 ({str(e)})"}, status=500)

class DeepSeekStreamView(View):
    def get(self, request):
        user_message = request.GET.get('message', '')
        
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": G4BR13L_SYSTEM_PROMPT},  # Misma personalización
                    {"role": "user", "content": f"[Usuario@{request.META['REMOTE_ADDR']}]: {user_message}"},
                ],
                stream=True,
                temperature=0.5  # Más preciso para streaming
            )

            def event_stream():
                for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    yield f"data: {content}\n\n"
                yield "data: [END]\n\n"

            return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
            
        except Exception as e:
            return JsonResponse({'error': f"Error de conexión: ¿Has probado apagar y encender el router? 🌐 ({str(e)})"}, status=500)

def TestView(request):
    return render(request, 'chat.html')  # <-- Aquí se sirve el HTML