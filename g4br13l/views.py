import os
from django.http import JsonResponse
from django.views import View
from openai import OpenAI
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import StreamingHttpResponse

load_dotenv()

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
                    {"role": "system", "content": "Eres un asistente experto en Django y desarrollo web"},
                    {"role": "user", "content": user_message},
                ],
                stream=True
            )

            def stream():
                for chunk in response:
                    content = chunk.choices[0].delta.content or ""
                    yield f"data: {content}\n\n"
                
            return StreamingHttpResponse(stream(), content_type='text/event-stream')
            
            return JsonResponse({
                'response': response.choices[0].message.content
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def get(self, request):
        # Renderizar template de chat
        return render(request, 'chat.html')