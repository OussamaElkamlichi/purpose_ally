@app.route('/tawasaw')
def send_tasks():
    base_url = "https://api.telegram.org/bot7461407614:AAFb52bSGp-2YRD2p7AEa5Por04Y72Obnc8/sendPoll"
    polls = [
        {"question": "🔻مُهِمَّاتٌ أُولَى \n ⚠️يرجى الحرص على القيام بحقيقة المهمة", "options": [
            "صلاة الصبح جماعة", "صلاة الظهر جماعة", "صلاة العصر جماعة", "صلاة المغرب جماعة", "صلاة العشاء جماعة", "الوتر وقيام الليل", "أذكار الصباح", "أذكار المساء", "أذكار قبل وبعد النوم", "الورد اليومي للقرآن والسُّنة"], "thread": 134, "multi": True},
        {"question": "🔻مُهِمَّاتٌ ثانية \n ⚠️يرجى الحرص على القيام بحقيقة المهمة.", "options": [
            "غض البصر", "حفظ الفرج", "كف الأذى", "الأمر بالمعروف", "النهي عن المنكر", "الرياضة", "الترويح", "لتعارفوا", "ضبط التواجد في مواقع التواصل", "ضبط النوم"], "thread": 316, "multi": True}
    ]

    responses = []
    for poll in polls:
        parameters = {
            "chat_id": "-1002251207506",
            "question": poll['question'],
            "options": json.dumps(poll['options']),
            "is_anonymous": False,
            "allows_multiple_answers": poll['multi'],
            "message_thread_id": poll['thread']
        }

        resp = requests.get(base_url, data=parameters)
        responses.append(resp.text)

    base_url2 = "https://api.telegram.org/bot7461407614:AAFb52bSGp-2YRD2p7AEa5Por04Y72Obnc8/sendMessage"
    message = {
        "chat_id": -1002251207506,
        "text": "✨️مرحبا أيها الفاضل ، كم جمعت من النقاط اليوم ؟ وهل قمت بحقيقة المهمات ؟",
        "message_thread_id": 143
    }
    requests.post(base_url, data=message)
    return "\n".join(responses)
