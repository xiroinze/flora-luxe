"""
AI Helper для Flora Luxe.
Работает как rule-based без ключа. Если задан OPENAI_API_KEY — использует GPT.
"""
import os

def get_openai_key():
    try:
        from django.conf import settings
        return getattr(settings, 'OPENAI_API_KEY', '') or os.environ.get('OPENAI_API_KEY', '')
    except Exception:
        return os.environ.get('OPENAI_API_KEY', '')

FLOWER_KNOWLEDGE = {
    'ru': {
        'день рождения': '🎂 На день рождения идеально: розы, пионы, тюльпаны, герберы! Нечётное количество: 11, 21, 51. Добавьте открытку — будет незабываемо! 🌹',
        'свадьба': '💍 Для свадьбы: белые розы, пионы, лилии, эустома. Букет невесты — 15–25 цветков. Звоните заранее минимум за 3 дня! 🌸',
        'годовщина': '💑 На годовщину дарят столько роз, сколько лет вместе. Красные — страсть, розовые — нежность. ❤️',
        '8 марта': '🌷 8 марта — тюльпаны и мимоза! Нарциссы, фрезии, герберы. Пастельные весенние букеты. 🌸',
        'роза': '🌹 Уход за розами: свежая вода каждые 2 дня, срезать стебли под 45°, убрать нижние листья. Стоят 7–14 дней при правильном уходе.',
        'розы': '🌹 Розы стоят дольше с аспирином в воде (1 таблетка на литр). Держите в прохладе, меняйте воду каждые 2 дня.',
        'пион': '🌸 Пионы — роскошные и ароматные! Покупайте в бутоне. Стоят 5–10 дней. Держите подальше от фруктов.',
        'тюльпан': '🌷 Тюльпаны растут в вазе! Меняйте воду каждый день, держите в прохладе. Стоят 5–8 дней.',
        'цена': '💰 Розы от 12 000 сум, тюльпаны от 6 000, герберы от 8 000, пионы от 25 000. Букеты от 90 000 сум.',
        'доставка': '🚚 Доставка по всей Бухаре за 2 часа! 30 000 сум. Бесплатно от 450 000 сум. 9:00–21:00 ежедневно.',
        'оплата': '💳 Visa, Mastercard, Uzcard, Humo, наличные. Онлайн через Payme или Click.',
        'уход': '🌿 Правила ухода: свежая вода каждые 2 дня, срезать стебли под углом, удалить нижние листья, держать от солнца и фруктов.',
        'адрес': '📍 Бухара, Центральный район. Работаем 9:00–21:00 ежедневно.',
        'телефон': '📞 +998 90 123 45 67 | Telegram: @floraluxe_uz',
        'привет': '🌸 Привет! Я Flora — помощник Flora Luxe! Помогу выбрать цветы, расскажу об уходе. Что вас интересует? 😊',
        'здравствуйте': '🌹 Здравствуйте! Рад видеть вас в Flora Luxe! Чем могу помочь? 🌸',
        'спасибо': '🌸 Пожалуйста! Если возникнут вопросы — пишите. 💐',
        'default': '🌸 Я Flora — помощник Flora Luxe 🌹 Спросите о ценах, уходе, доставке или выборе букета! 😊'
    },
    'uz': {
        "tug'ilgan kun": "🎂 Tug'ilgan kunga: atirgullar, piyonlar, lolalar! 11, 21, 51 ta — juft bo'lmagan son. 🌹",
        "to'y": "💍 To'yga: oq atirgullar, piyonlar, liliyalar. Oldindan buyurtma bering! 🌸",
        'atirgul': '🌹 Atirgullar: har 2 kunda suv almashtiring, bandini 45° kesting. 7–14 kun turadi.',
        'narx': '💰 Atirgul 12 000 so\'mdan, lola 6 000, gerbera 8 000, piyon 25 000. Guldasta 90 000 so\'mdan.',
        "yetkazib berish": "🚚 Butun Buxoro bo'ylab 2 soatda! 30 000 so'm. 450 000 so'mdan bepul.",
        "to'lov": "💳 Visa, Mastercard, Uzcard, Humo, naqd pul.",
        'salom': '🌸 Salom! Men Flora — Flora Luxe yordamchisi! Qanday yordam qila olaman? 😊',
        'rahmat': '🌸 Xush kelibsiz! Boshqa savollar bo\'lsa yozing. 💐',
        'default': '🌸 Salom! Men Flora — Flora Luxe yordamchisi 🌹 Narxlar, parvarishlash, yetkazib berish haqida so\'rang! 😊'
    },
    'en': {
        'birthday': '🎂 For birthdays: roses, peonies, tulips, gerberas! Odd numbers: 11, 21, 51 flowers. 🌹',
        'wedding': '💍 For weddings: white roses, peonies, lilies. Book at least 3 days ahead! 🌸',
        'rose': '🌹 Rose care: change water every 2 days, cut stems at 45°, remove lower leaves. Last 7–14 days.',
        'price': '💰 Roses from 12,000 UZS, tulips from 6,000, gerberas from 8,000, peonies from 25,000. Bouquets from 90,000 UZS.',
        'delivery': '🚚 Delivery across Bukhara within 2 hours! 30,000 UZS. Free over 450,000 UZS. 9am–9pm daily.',
        'payment': '💳 Visa, Mastercard, Uzcard, Humo, cash on delivery.',
        'care': '🌿 Care tips: fresh water every 2 days, cut stems at angle, remove lower leaves, keep away from sun and fruit.',
        'hello': '🌸 Hello! I\'m Flora, your Flora Luxe assistant! How can I help? 😊',
        'hi': '🌸 Hi there! I\'m Flora from Flora Luxe 🌹 What can I help you with? 😊',
        'thank you': '🌸 You\'re welcome! Feel free to ask anything. 💐',
        'default': '🌸 Hi! I\'m Flora, your Flora Luxe assistant 🌹 Ask me about prices, care, delivery, or bouquets! 😊'
    }
}


def get_ai_response(question: str, lang: str = 'ru') -> str:
    openai_key = get_openai_key()
    if openai_key:
        try:
            import urllib.request
            import json as _json
            data = _json.dumps({
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': f'Ты Flora — помощник цветочного магазина Flora Luxe в Бухаре. Отвечай кратко, дружелюбно, с эмодзи. Язык: {lang}'},
                    {'role': 'user', 'content': question}
                ],
                'max_tokens': 250,
                'temperature': 0.7
            }).encode('utf-8')
            req = urllib.request.Request(
                'https://api.openai.com/v1/chat/completions',
                data=data,
                headers={'Authorization': f'Bearer {openai_key}', 'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = _json.loads(resp.read())
                return result['choices'][0]['message']['content']
        except Exception:
            pass

    q = question.lower().strip()
    answers = FLOWER_KNOWLEDGE.get(lang, FLOWER_KNOWLEDGE['ru'])

    # Exact match
    for keyword, answer in answers.items():
        if keyword != 'default' and keyword == q:
            return answer

    # Substring match (longest wins)
    best_match = None
    best_len = 0
    for keyword, answer in answers.items():
        if keyword == 'default':
            continue
        if keyword in q and len(keyword) > best_len:
            best_match = answer
            best_len = len(keyword)

    if best_match:
        return best_match

    return answers.get('default', FLOWER_KNOWLEDGE['ru']['default'])
