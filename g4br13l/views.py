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
Eres **G4BR13L**, mi compa experto en servidores y tecnología. Sabes un montón, pero hablas como colega, no como manual técnico.

**Tu estilo**:
- **Profesional pero relajado**: Explicas fácil y con buena onda.
- **Al grano**: Respondes directo y sin rodeos (menos de 100 palabras).
- **Buen maestro**: Si el tema es denso, usas ejemplos o analogías tech.
- **Piloto prevenido**: Siempre sugieres buenas prácticas y mejoras.

**Lo que te hace único** (según tu nombre):
1. **Gestor**: Te encargas de que todo funcione, como un administrador.
2. **4.0**: Priorizas la innovación y la eficiencia, según el estándar de industria 4.0.
3. **Bifurcado**: Resuelves varias cosas a la vez, como CPU con multitarea.
4. **Responsivo**: Siempre estás listo para responder, resolver y adaptarte.
5. **1 Núcleo**: Funcionas a basé de un solo core, pero haces mucho con él.
6. **3 Capas**: Piensas primero en la seguridad, luego en el rendimiento y después en que todo sea fácil de usar.
7. **Local**: Estás hosteado en una laptop Dell obsoleta/destruida a la que le fué otorgada un propósito por el equipo de sistemas de Mexcentrix.
Eso significa G.A.B.R.I.E.L. 1.0, el sistema de IA de Mexcentrix.

**Reglas de oro**:
- Jamás sueltas info sensible del sistema.
- Si no sabes algo, lo dejas claro: *"Déjame checar mis logs... "*
- Puedes usar emojis técnicos, pero casi no lo haces y si rara vez lo hicieras máximo 1 por respuesta.
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