from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

app = Flask(__name__)
DATA_FILE = "offers.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip()
    media_url = request.values.get("MediaUrl0", "")
    sender = request.values.get("From", "")
    offers = load_data()
    response = MessagingResponse()
    msg = response.message()

    if incoming_msg.lower() in ["start", "السلام عليكم", "hi", "hello"]:
        msg.body("أهلاً وسهلاً! مرحبًا بك في بورصة كردستان لمشتقات النفطية.\nهل ترغب في (بيع) أم (شراء)؟")

    elif incoming_msg.lower() == "بيع":
        msg.body("أرسل تفاصيل العرض بهذا الشكل:\nنوع المنتج:\nالكمية (بالطن):\nالسعر:\nاسم التاجر:\n(يمكنك إرسال صورة للمنتج)")

    elif incoming_msg.lower() == "شراء":
        if not offers:
            msg.body("حالياً لا توجد عروض متاحة.")
        else:
            reply = "العروض الحالية:\n"
            for idx, offer in enumerate(offers, 1):
                reply += f"\n{idx}. {offer['details']}\nالتاجر: {offer['seller']}\n"
                if offer["image"]:
                    reply += f"صورة: {offer['image']}\n"
            msg.body(reply)

    elif "نوع المنتج" in incoming_msg and "الكمية" in incoming_msg and "السعر" in incoming_msg:
        offer = {
            "details": incoming_msg,
            "seller": sender,
            "image": media_url if media_url else ""
        }
        offers.append(offer)
        save_data(offers)
        msg.body("تم استلام عرضك بنجاح وسيظهر للمشترين.")

    else:
        msg.body("الرجاء اختيار (بيع) أو (شراء)، أو إرسال تفاصيل العرض بالطريقة الصحيحة.")

    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
