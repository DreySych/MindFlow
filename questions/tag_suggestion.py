import json
import os

import requests
from django.http import JsonResponse


def suggest_tag(request):
    """Подбирает тег для поста через OpenRouter."""
    if request.method != 'POST':
        return JsonResponse({'tag': 'Другое'})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'tag': 'Другое'})

    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()

    with open('questions/available_tags.txt', mode='r', encoding='utf-8') as file:
        tags = [
            tag.strip()
            for tag in file.read().splitlines()
            if tag.strip()
        ]

    api_key = os.getenv('OPENROUTER_API_KEY', '')

    if not api_key:
        return JsonResponse({'tag': 'Другое'})

    prompt = f"""
Проанализируй заголовок и описание поста и выбери один тег строго из списка.

Заголовок: {title}
Описание: {description}

Список тегов:
{", ".join(tags)}

Ответь только одним тегом из списка. Без кавычек и объяснений.
Если подходящего тега нет, ответь: Другое
"""

    try:
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt,
                    }
                ],
            },
            timeout=10,
        )

        result = response.json()

        answer = (
            result.get('choices', [{}])[0]
            .get('message', {})
            .get('content', '')
            .strip()
        )

        if answer not in tags:
            answer = 'Другое'

        return JsonResponse({'tag': answer})

    except requests.RequestException:
        return JsonResponse({'tag': 'Другое'})
