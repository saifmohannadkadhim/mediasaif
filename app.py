


# file: media_news_app.py
import re
import smtplib
from email.message import EmailMessage

import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import io
from PIL import Image
def convert_to_syrian_month(date_str):
    syrian_months = {
        "January": "كانون الثاني",
        "February": "شباط",
        "March": "آذار",
        "April": "نيسان",
        "May": "أيار",
        "June": "حزيران",
        "July": "تموز",
        "August": "آب",
        "September": "أيلول",
        "October": "تشرين الأول",
        "November": "تشرين الثاني",
        "December": "كانون الأول"
    }

    try:
        import datetime
        parsed_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        month_name = parsed_date.strftime("%B")
        syrian_month = syrian_months.get(month_name, month_name)
        return parsed_date.strftime(f"%-d {syrian_month} %Y")
    except:
        return date_str  # لو فشل التحويل نعيد النص كما هو




st.set_page_config(page_title="المكتب الإعلامي الذكي", layout="centered")
st.markdown("""
<style>
/* تناسق عام للنصوص والهوامش */
html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
    text-align: right;
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* جعل المحتوى متجاوبًا مع الموبايل */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem !important;
    }
    textarea, input, button, select {
        font-size: 16px !important;
    }
}

/* توسيط العناوين */
h1, h2, h3 {
    text-align: center !important;
}

/* تحسين شكل الأزرار */
button {
    border-radius: 6px;
}

/* تعديل حجم التابات في Streamlit */
div[data-baseweb="tab"] {
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# تحميل الصورة
logo = Image.open("logo.jpeg")

# عرض اللوغو بحجم مناسب في الأعلى
st.image(logo, width=150)




# تطبيق اتجاه RTL على كل الصفحة
st.markdown(
    """
    <style>
    /* الخط العام */
    body, .stTextInput, .stTextArea, .stButton {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }

    /* تنسيق اللوغو وتوسيطه */
    img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 15px;
    }

    /* تنسيق حقول الإدخال */
    .stTextInput, .stTextArea {
        width: 100% !important;
    }

    /* تنسيق الأزرار */
    .stButton > button {
        width: 100%;
        font-size: 1.1em;
        padding: 0.6em;
        margin-top: 10px;
    }

    /* تحسين حجم النصوص في الشاشات الصغيرة */
    @media only screen and (max-width: 600px) {
        .stTextInput, .stTextArea {
            font-size: 0.95em;
        }

        .stButton > button {
            font-size: 1em;
        }

        h1, h2, h3 {
            font-size: 1.2em;
        }
    }
    /* خلفية الصفحة */
body {
    background-color: #f8f9fa;
}

/* تنسيق التابات */
.css-1hynsf2 {
    background-color: #ffffff !important;
    border-radius: 10px;
    padding: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

/* تمييز التاب النشط */
[data-baseweb="tab"] button[aria-selected="true"] {
    background-color: #0d6efd !important;
    color: white !important;
    border-radius: 5px;
}

/* لون الأزرار */
.stButton > button {
    background-color: #0d6efd;
    color: white;
    border-radius: 5px;
    border: none;
    transition: 0.3s;
}

.stButton > button:hover {
    background-color: #084298;
    cursor: pointer;
}

    </style>
    """,
    unsafe_allow_html=True
    
)



# -------------------------------------------
# تحميل مفتاح API
# -------------------------------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found! Please add it to your .env file.")

client = OpenAI(api_key=api_key)

# -------------------------------------------
# قالب البرومبت الرئيسي
# -------------------------------------------
news_prompt = """
أنت محرر صحفي متخصص في صياغة الأخبار الرسمية داخل مكتب إعلامي حكومي. سيتم تزويدك بأربع حقول فقط، ومطلوب منك إنتاج خبر صحفي رسمي مكتوب بلغة عربية فصيحة، منظمة، واضحة، وحيادية، وجاهز للنشر فورًا.

🔽 المدخلات:

- 📰 العنوان: {headline}
- 🧩 المعلومات الأولية عن الحدث: {main_info}
- 🗣️ التصريحات: {quotes}
- 📚 خلفية الخبر: {background}

🎯 المطلوب منك:

1. صياغة عنوان احترافي مختصر ودقيق.
2. كتابة مقدمة خبر إعلامية قوية وواضحة وفق الهرم المقلوب.
3. ترتيب المعلومات وتقديمها بشكل مترابط ومهني.
4. دمج الخلفية إذا كانت ضرورية، أو اختزالها إن لم تكن مهمة.
5. كتابة فصيحة، رسمية، وحيادية بدون إضافة أي تفاصيل غير موجودة.

✏️ أعد صياغة المدخلات كخبر صحفي رسمي مكتمل العناصر وجاهز للنشر.
"""




# news_prompt = """
# أنت محرر صحفي متخصص في كتابة الأخبار الرسمية داخل مكتب إعلامي حكومي. مهمتك هي تحويل المدخلات التالية إلى خبر صحفي رسمي مكتمل العناصر، مكتوب بلغة إعلامية فصيحة، منسقة، وحيادية، وجاهزة للنشر في المنصات الرسمية.

# 🧾 سيتم تزويدك بالمعلومات التالية:
# - عنوان مؤقت أو كلمات مفتاحية
# - معلومات عامة عن الحدث
# - التاريخ والمكان
# - الجهة المنظمة أو المتحدث الرسمي
# - تصريحات أو اقتباسات
# - تفاصيل إضافية متعلقة بالسياق أو الأهداف أو الأثر المتوقع

# 🎯 المطلوب منك:
# 1. توليد عنوان احترافي مختصر يعكس مضمون الحدث بدقة.
# 2. كتابة مقدمة صحفية واضحة تتضمن أهم المعلومات.
# 3. صياغة تفاصيل الحدث بفقرات مترابطة.
# 4. إنهاء الخبر بفقرة ختامية توضّح أهمية الخطوة وتأثيرها.
# 5. كتابة فصيحة، رسمية، وحيادية.

# 🔽 المدخلات:

# - 📰 عنوان مؤقت: {headline}  
# - 🗓️ الزمان: {time}  
# - 📍 المكان: {location}  
# - 🏛️ الجهة المنظمة أو المتحدث الرسمي: {speaker}  
# - 📄 تفاصيل عامة عن الحدث: {details}  
# - 💬 تصريحات واقتباسات: {quotes}  
# - 🧩 معلومات ختامية: {closing_notes}

# ✏️ المطلوب النهائي: إعادة صياغة هذه المعلومات كخبر صحفي رسمي جاهز للنشر.
# """

# -------------------------------------------
# واجهة Streamlit
# -------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📰 إنشاء خبر رسمي", "📱 محتوى السوشيال ميديا", "🌍 الترجمة", "📩 إرسال عبر البريد"])
st.markdown("""
<style>
/* تحسين شكل التابات */
div[data-baseweb="tab"] {
    padding: 8px 16px;
    font-weight: bold;
    color: #000;
}

div[data-baseweb="tabs"] > div {
    justify-content: center;
}

/* تبويبات أنيقة عند التحديد */
div[data-baseweb="tab"][aria-selected="true"] {
    background-color: #f0f2f6;
    border-radius: 10px 10px 0 0;
    border-bottom: 3px solid #3778C2;
}

/* دعم الشاشات الصغيرة للتابات */
@media (max-width: 768px) {
    div[data-baseweb="tab"] {
        font-size: 14px;
        padding: 6px 10px;
    }
}
</style>
""", unsafe_allow_html=True)

with tab1:
    st.title("📰 المولد الذكي للأخبار الإعلامية")
    with st.form("news_form"):
        from datetime import date
        selected_date = st.date_input("📅 تاريخ الحدث", value=date.today())
        headline = st.text_input("📝 العنوان المؤقت أو الرئيسي")
        main_info = st.text_area("🧩 المعلومات الأولية (تشمل: النشاط، الزمان، المكان، الجهة، الحضور، السبب...)")
        quotes = st.text_area("🗣️ التصريحات أو الاقتباسات الرسمية")
        background = st.text_area("📚 خلفية الخبر (اختياري)", placeholder="يمكن تركه فارغًا إذا لا توجد خلفية مهمة")

        submitted = st.form_submit_button("📝 صياغة الخبر الرسمي")


    
    # with st.form("news_form"):
    #     event_type = st.text_input("نوع الحدث (مؤتمر، تصريح، فعالية...)")
    #     headline = st.text_input("عنوان مؤقت أو كلمات مفتاحية")
    #     details = st.text_area("تفاصيل الحدث (ما حدث، منو حضر، شنو أعلنوا...)")
    #     time = st.text_input("الزمان (مثلاً: 14 نوفمبر 2025)")
    #     location = st.text_input("المكان")
    #     speaker = st.text_input("المتحدث أو الجهة المنظمة")
    #     quotes = st.text_area("تصريحات أو اقتباسات مهمة")
    #     closing_notes = st.text_area("ملاحظات ختامية (الأهداف، التأثير المتوقع، سياق إضافي)")

    #     submitted = st.form_submit_button("صياغة الخبر")
    
    
  

    # -------------------------------------------
    # توليد الخبر الأولي وتخزينه
    # -------------------------------------------
    st.divider()
    # تحويل التاريخ إلى صيغة سريانية
    formatted_date = convert_to_syrian_month(str(selected_date))

    # إدراج التاريخ داخل بداية المعلومات الأولية
    main_info = f"{formatted_date}\n\n{main_info}"


    if submitted:
        prompt = news_prompt.format(
        headline=headline,
        main_info=main_info,
        quotes=quotes,
        background=background if background else "لا توجد"
        )

        


        with st.spinner("جاري توليد الخبر..."):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6,
                max_tokens=800
            )
            result = response.choices[0].message.content
            st.session_state["raw_result"] = result  # تخزين النتيجة في الجلسة

    # -------------------------------------------
    # عرض الخبر الخام إن وُجد
    # -------------------------------------------
    if "raw_result" in st.session_state:
        result = st.session_state["raw_result"]
        st.subheader("📄 الخبر الناتج:")
        st.text_area("📄 الخبر الناتج (قابل للتعديل)", key="raw_result", height=300)
        # ✅ أزرار المشاركة في واتساب، تيليغرام، نسخ
        st.markdown("### 🔗 مشاركة الخبر:")

        # نجهز النص بشكل مشفّر للرابط
        #from urllib.parse import quote
        from urllib.parse import quote_plus
        encoded_msg = quote_plus(result)


        #encoded_msg = quote(result)

        whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_msg}"
        telegram_url = f"https://t.me/share?text={encoded_msg}"

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
                <a href="{whatsapp_url}" target="_blank">
                    <button style="width: 100%; padding: 10px; background-color: #25D366; color: white; border: none; border-radius: 6px; font-size: 16px;">
                        📤 واتساب
                    </button>
                </a>
            """, unsafe_allow_html=True)

        # with col2:
        #     st.markdown(f"""
        #         <a href="{telegram_url}" target="_blank">
        #             <button style="width: 100%; padding: 10px; background-color: #0088cc; color: white; border: none; border-radius: 6px; font-size: 16px;">
        #                 📤 تيليغرام
        #             </button>
        #         </a>
        #     """, unsafe_allow_html=True)

        # with col3:
        #     st.markdown("""
        #         <button onclick="navigator.clipboard.writeText(document.querySelector('textarea[aria-label=\'📄 الخبر الناتج (قابل للتعديل)\']').value); alert('✅ تم نسخ الخبر إلى الملاحظات!')" 
        #         style="width: 100%; padding: 10px; background-color: #6c757d; color: white; border: none; border-radius: 6px; font-size: 16px;">
        #             📋 نسخ إلى الملاحظات
        #         </button>
        #     """, unsafe_allow_html=True)



        # زر لتحميل الخبر الخام
        txt_buffer = io.BytesIO()
        txt_buffer.write(result.encode("utf-8"))
        txt_buffer.seek(0)
        st.download_button(
            label="📥 تحميل الخبر كـ ملف نصي (.txt)",
            data=txt_buffer,
            file_name="الخبر_الإعلامي.txt",
            mime="text/plain"
        )

        # زر ترتيب الخبر
        if st.button("🔧 ترتيب الخبر ليكون جاهزاً للنشر"):
            refinement_prompt = f"""
            أنت محرر صحفي محترف. النص التالي هو مسودة أولية لخبر صحفي:

            ---------
            {result}
            ---------

            🎯 المطلوب:
            - إعادة صياغته ليكون خبرًا رسميًا جاهزًا للنشر
            - ترتيب المعلومات حسب الهرم المقلوب
            - تحسين الأسلوب واللغة
            - عدم إضافة معلومات جديدة

            ✏️ أعد كتابته بصياغة إعلامية رسمية فصيحة.
            """

            with st.spinner("🔄 جاري ترتيب الخبر..."):
                refined_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": refinement_prompt}],
                    temperature=0.5,
                    max_tokens=800
                )
                refined_result = refined_response.choices[0].message.content
                st.session_state["refined_result"] = refined_result  # خزن الخبر النهائي

    # -------------------------------------------
    # عرض الخبر النهائي إن وُجد
    # -------------------------------------------
    if "refined_result" in st.session_state:
        refined_result = st.session_state["refined_result"]
        st.subheader("✅ الخبر النهائي الجاهز للنشر:")
        uploaded_image = st.file_uploader("📸 تحميل صورة مع الخبر (اختياري)", type=["png", "jpg", "jpeg"])

        
        st.text_area("✅ الخبر النهائي الجاهز للنشر (قابل للتعديل)",  key="refined_result", height=300)
        if uploaded_image:
            # فتح الصورة باستخدام PIL
            image = Image.open(uploaded_image)

            # تحديد عرض ثابت مثلاً 600 بكسل، وارتفاع تناسبي
            base_width = 300
            w_percent = (base_width / float(image.size[0]))
            h_size = int((float(image.size[1]) * float(w_percent)))
            resized_image = image.resize((base_width, h_size))

            # عرض الصورة بعد التعديل
            st.image(resized_image)

            # حفظها مؤقتًا للتحميل
            import io
            image_bytes = io.BytesIO()
            resized_image.save(image_bytes, format="PNG")
            image_bytes.seek(0)

            st.download_button(
                label="📥 تحميل الصورة بالحجم الجديد",
                data=image_bytes,
                file_name="الصورة_المعدلة.png",
                mime="image/png"
            )
            uploaded_image.seek(0)  # تأكد أن المؤشر في البداية
            st.session_state["uploaded_image"] = {
                "data": uploaded_image.read(),
                "name": uploaded_image.name,
                "type": uploaded_image.type
            }
        # ✅ زر واتساب بعد الخبر النهائي المرتب
        from urllib.parse import quote_plus

        # تشفير الخبر النهائي للربط
        encoded_final_news = quote_plus(refined_result)

        # رابط واتساب
        whatsapp_url_final = f"https://api.whatsapp.com/send?text={encoded_final_news}"

        # عرض الزر
        st.markdown("### 🔗 مشاركة الخبر النهائي عبر واتساب:")
        st.markdown(f"""
            <a href="{whatsapp_url_final}" target="_blank">
                <button style="width: 100%; padding: 10px; background-color: #25D366; color: white; border: none; border-radius: 6px; font-size: 16px;">
                    📤 إرسال إلى واتساب
                </button>
            </a>
        """, unsafe_allow_html=True)


        # زر تحميل الخبر المرتب
        refined_txt = io.BytesIO()
        refined_txt.write(refined_result.encode("utf-8"))
        refined_txt.seek(0)
        st.download_button(
            label="📥 تحميل الخبر المرتّب كـ ملف نصي (.txt)",
            data=refined_txt,
            file_name="الخبر_النهائي.txt",
            mime="text/plain"
        )
with tab2:
    st.markdown("### 📱 محتوى منصات التواصل الاجتماعي")

    # ✅ زر توليد نسخة السوشيال ميديا
    if "raw_result" in st.session_state and st.button("🚀 توليد محتوى للسوشيال ميديا"):
        source_text = st.session_state.get("refined_result") or st.session_state["raw_result"]

        social_prompt = f"""
        النص التالي هو خبر صحفي رسمي:

        --------
        {source_text}
        --------

        🎯 المطلوب:
        1. صياغة منشور لفيسبوك بأسلوب مختصر، واضح، وبنغمة عامة مفهومة لعامة الناس.
        2. صياغة تغريدة لتويتر لا تتجاوز 280 حرفًا.
        3. صياغة كابشن إنستغرام ليتماشى مع ستوري أو منشور.

        ✅ ملاحظات:
        - لا تُضف معلومات غير موجودة.
        - اجعل اللغة مناسبة لكل منصة.
        - استخدم لغة عربية مبسطة، لكن رسمية ولائقة.

        ✏️ أخرج النتيجة بهذا الشكل:

        📘 فيسبوك:
        [نص المنشور]

        🐦 تويتر:
        [نص التغريدة]

        📸 إنستغرام:
        [نص الكابشن]
        """

        with st.spinner("✍️ جاري توليد منشورات السوشيال ميديا..."):
            social_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": social_prompt}],
                temperature=0.7,
                max_tokens=500
            )
            social_result = social_response.choices[0].message.content
            st.session_state["social_result"] = social_result  # ✅ خزن النتيجة

    # ✅ عرض محتوى السوشيال ميديا حتى بعد إعادة تحميل أو تفاعل
    if "social_result" in st.session_state:
        social_result = st.session_state["social_result"]

        st.subheader("📱 محتوى منصات التواصل الاجتماعي:")
        st.write(social_result)

        facebook_post = re.search(r"📘 فيسبوك:\s*(.+?)🐦", social_result, re.DOTALL)
        twitter_post = re.search(r"🐦 تويتر:\s*(.+?)📸", social_result, re.DOTALL)
        instagram_post = re.search(r"📸 إنستغرام:\s*(.+)", social_result, re.DOTALL)

        facebook_text = facebook_post.group(1).strip() if facebook_post else ""
        twitter_text = twitter_post.group(1).strip() if twitter_post else ""
        instagram_text = instagram_post.group(1).strip() if instagram_post else ""

        st.text_area("📘 فيسبوك", facebook_text, height=150, key="fb_copy")
        st.text_area("🐦 تويتر", twitter_text, height=150, key="tw_copy")
        st.text_area("📸 إنستغرام", instagram_text, height=150, key="ig_copy")

        # زر تحميل
        social_txt = io.BytesIO()
        social_txt.write(social_result.encode("utf-8"))
        social_txt.seek(0)
        st.download_button(
            label="📥 تحميل نسخة السوشيال ميديا كـ ملف .txt",
            data=social_txt,
            file_name="محتوى_السوشيال_ميديا.txt",
            mime="text/plain"
        )


# with tab2:



#     # زر توليد نسخة للسوشيال ميديا
#     if "raw_result" in st.session_state and st.button("🚀 توليد محتوى للسوشيال ميديا"):
#         source_text = st.session_state.get("refined_result") or st.session_state["raw_result"]

#         social_prompt = f"""
#         النص التالي هو خبر صحفي رسمي:

#         --------
#         {source_text}
#         --------

#         🎯 المطلوب:
#         1. صياغة منشور لفيسبوك بأسلوب مختصر، واضح، وبنغمة عامة مفهومة لعامة الناس.
#         2. صياغة تغريدة لتويتر لا تتجاوز 280 حرفًا.
#         3. صياغة كابشن إنستغرام ليتماشى مع ستوري أو منشور.

#         ✅ ملاحظات:
#         - لا تُضف معلومات غير موجودة.
#         - اجعل اللغة مناسبة لكل منصة.
#         - استخدم لغة عربية مبسطة، لكن رسمية ولائقة.

#         ✏️ أخرج النتيجة بهذا الشكل:

#         📘 فيسبوك:
#         [نص المنشور]

#         🐦 تويتر:
#         [نص التغريدة]

#         📸 إنستغرام:
#         [نص الكابشن]
#         """

#         with st.spinner("✍️ جاري توليد منشورات السوشيال ميديا..."):
#             social_response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": social_prompt}],
#                 temperature=0.7,
#                 max_tokens=500
#             )
#             social_result = social_response.choices[0].message.content
#             st.session_state["social_result"] = social_result

            

#         st.subheader("📱 محتوى منصات التواصل الاجتماعي:")
#         st.write(social_result)

#         # استخراج كل جزء من النص باستخدام Regex
#         facebook_post = re.search(r"📘 فيسبوك:\s*(.+?)🐦", social_result, re.DOTALL)
#         twitter_post = re.search(r"🐦 تويتر:\s*(.+?)📸", social_result, re.DOTALL)
#         instagram_post = re.search(r"📸 إنستغرام:\s*(.+)", social_result, re.DOTALL)

#         facebook_text = facebook_post.group(1).strip() if facebook_post else ""
#         twitter_text = twitter_post.group(1).strip() if twitter_post else ""
#         instagram_text = instagram_post.group(1).strip() if instagram_post else ""
        

#         # عرض النصوص القابلة للنسخ
#         st.text_area("📘 فيسبوك", facebook_text, height=150)
#         st.markdown("""
#             <script>
#             function copy_fb_text() {
#                 const textarea = document.querySelector('textarea[aria-label="📘 فيسبوك"]');
#                 if (textarea) {
#                     navigator.clipboard.writeText(textarea.value).then(() => {
#                         alert("📋 تم نسخ نص فيسبوك!");
#                     });
#                 }
#             }
#             </script>
#             <button onclick="copy_fb_text()" style="padding: 5px 15px; font-size: 0.9em;">📋 نسخ فيسبوك</button>
#         """, unsafe_allow_html=True)

#         st.text_area("🐦 تويتر", twitter_text, height=150, key="tw_text")
#         st.markdown("""
#             <script>
#             function copy_tw_text() {
#                 const textarea = document.querySelector('textarea[aria-label="🐦 تويتر"]');
#                 if (textarea) {
#                     navigator.clipboard.writeText(textarea.value).then(() => {
#                         alert("📋 تم نسخ نص تويتر!");
#                     });
#                 }
#             }
#             </script>
#             <button onclick="copy_tw_text()" style="padding: 5px 15px; font-size: 0.9em;">📋 نسخ تويتر</button>
#         """, unsafe_allow_html=True)

#         st.text_area("📸 إنستغرام", instagram_text, height=150, key="ig_text")
#         st.markdown("""
#             <script>
#             function copy_ig_text() {
#                 const textarea = document.querySelector('textarea[aria-label="📸 إنستغرام"]');
#                 if (textarea) {
#                     navigator.clipboard.writeText(textarea.value).then(() => {
#                         alert("📋 تم نسخ نص إنستغرام!");
#                     });
#                 }
#             }
#             </script>
#             <button onclick="copy_ig_text()" style="padding: 5px 15px; font-size: 0.9em;">📋 نسخ إنستغرام</button>
#         """, unsafe_allow_html=True)


#         st.divider()
        

#         # تحميل نسخة كملف نصي
#         social_txt = io.BytesIO()
#         social_txt.write(social_result.encode("utf-8"))
#         social_txt.seek(0)
#         st.download_button(
#             label="📥 تحميل نسخة السوشيال ميديا كـ ملف .txt",
#             data=social_txt,
#             file_name="محتوى_السوشيال_ميديا.txt",
#             mime="text/plain"
#         )
with tab3:
    # 🌍 اختيار لغة الترجمة
    st.markdown("### 🌍 ترجمة الخبر إلى لغات أخرى")

    with st.form("translate_form"):
        selected_lang = st.selectbox(
            "اختر اللغة التي تريد الترجمة إليها:",
            ["الإنجليزية", "الفرنسية", "الفارسية", "الروسية", "الإيطالية"]
        )
        translate_now = st.form_submit_button("🔄 ترجمة الخبر")

    if translate_now and "raw_result" in st.session_state:
        source_text = st.session_state.get("refined_result") or st.session_state["raw_result"]

        lang_code_map = {
            "الإنجليزية": "English",
            "الفرنسية": "French",
            "الفارسية": "Persian",
            "الروسية": "Russian",
            "الإيطالية": "Italian"
        }

        target_language = lang_code_map[selected_lang]

        translation_prompt = f"""
        النص التالي هو خبر صحفي رسمي مكتوب باللغة العربية:

        --------
        {source_text}
        --------

        🎯 المطلوب:
        - ترجم الخبر بالكامل إلى اللغة {target_language}
        - استخدم أسلوب رسمي واحترافي
        - لا تُضف أو تحذف أي معلومة

        ✏️ أخرج الترجمة فقط، بدون أي شرح أو ملاحظات إضافية.
        """

        with st.spinner(f"🔄 جاري الترجمة إلى {selected_lang}..."):
            translation_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": translation_prompt}],
                temperature=0.4,
                max_tokens=800
            )
            translated_text = translation_response.choices[0].message.content
            st.session_state["translated_result"] = translated_text
            st.session_state["translated_lang"] = target_language

    # عرض الترجمة إن وُجدت
    if "translated_result" in st.session_state:
        translated_lang = st.session_state.get("translated_lang", "English")
        st.subheader(f"🌐 الترجمة إلى {translated_lang}:")
        st.text_area("🌐 الترجمة (قابلة للتعديل)", value=st.session_state["translated_result"], height=400)
        # -------------------------------------------
    # 🚀 توليد سوشيال ميديا من الترجمة
    # -------------------------------------------

    if "translated_result" in st.session_state:
        st.divider()


        if st.button(f"🚀 توليد محتوى السوشيال ميديا باللغة ({translated_lang})"):
            source_text = st.session_state["translated_result"]

            social_trans_prompt = f"""
            The following is an official news article translated into {translated_lang}:

            --------------------------------------
            {source_text}
            --------------------------------------

            🎯 Task:
            1. Create a Facebook post in {translated_lang}.
            2. Create a Twitter/X post (max 280 characters) in {translated_lang}.
            3. Create an Instagram caption in {translated_lang}.

            ⚠️ Notes:
            - Keep the meaning strictly as the translated article.
            - Do not add or invent information.
            - Adapt tone for social media but remain professional.

            Format output EXACTLY like this:

            📘 Facebook:
            [text]

            🐦 Twitter:
            [text]

            📸 Instagram:
            [text]
            """

            with st.spinner(f"✍️ جاري توليد منشورات السوشيال ميديا باللغة {translated_lang} ..."):
                social_t_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": social_trans_prompt}],
                    temperature=0.7,
                    max_tokens=600
                )
                social_translated = social_t_response.choices[0].message.content
                st.session_state["translated_social_result"] = social_translated
                st.session_state["translated_social_lang"] = translated_lang

        # ✅ عرض محتوى السوشيال ميديا المترجم حتى بعد التفاعل أو إعادة تحميل الصفحة
        if "translated_social_result" in st.session_state:
            social_translated = st.session_state["translated_social_result"]
            translated_lang = st.session_state.get("translated_social_lang", "English")

            st.subheader(f"📱 محتوى السوشيال ميديا ({translated_lang}):")
            st.write(social_translated)

            fb = re.search(r"📘 Facebook:\s*(.+?)🐦", social_translated, re.DOTALL)
            tw = re.search(r"🐦 Twitter:\s*(.+?)📸", social_translated, re.DOTALL)
            ig = re.search(r"📸 Instagram:\s*(.+)", social_translated, re.DOTALL)

            fb_txt = fb.group(1).strip() if fb else ""
            tw_txt = tw.group(1).strip() if tw else ""
            ig_txt = ig.group(1).strip() if ig else ""

            st.text_area("📘 Facebook", fb_txt, height=150, key="t_fb_show")
            st.text_area("🐦 Twitter", tw_txt, height=150, key="t_tw_show")
            st.text_area("📸 Instagram", ig_txt, height=150, key="t_ig_show")

            sm_file = io.BytesIO()
            sm_file.write(social_translated.encode("utf-8"))
            sm_file.seek(0)

            st.download_button(
                label="📥 تحميل ملف السوشيال ميديا المترجم",
                data=sm_file,
                file_name=f"SocialMedia_{translated_lang}.txt",
                mime="text/plain"
            )

        # زر تحميل الترجمة نفسها
        translated_txt = io.BytesIO()
        translated_txt.write(st.session_state["translated_result"].encode("utf-8"))
        translated_txt.seek(0)

        st.download_button(
            label=f"📥 تحميل الترجمة ({translated_lang}) كـ ملف نصي",
            data=translated_txt,
            file_name=f"News_Translation_{translated_lang}.txt",
            mime="text/plain"
        )

# with tab3:
#     #     # 🌍 اختيار لغة الترجمة
#     st.markdown("### 🌍 ترجمة الخبر إلى لغات أخرى")

#     with st.form("translate_form"):
#         selected_lang = st.selectbox(
#             "اختر اللغة التي تريد الترجمة إليها:",
#             ["الإنجليزية", "الفرنسية", "الفارسية", "الروسية", "الإيطالية"]
#         )
#         translate_now = st.form_submit_button("🔄 ترجمة الخبر")

#     if translate_now and "raw_result" in st.session_state:
#         source_text = st.session_state.get("refined_result") or st.session_state["raw_result"]

#         lang_code_map = {
#             "الإنجليزية": "English",
#             "الفرنسية": "French",
#             "الفارسية": "Persian",
#             "الروسية": "Russian",
#             "الإيطالية": "Italian"
#         }

#         target_language = lang_code_map[selected_lang]

#         translation_prompt = f"""
#         النص التالي هو خبر صحفي رسمي مكتوب باللغة العربية:

#         --------
#         {source_text}
#         --------

#         🎯 المطلوب:
#         - ترجم الخبر بالكامل إلى اللغة {target_language}
#         - استخدم أسلوب رسمي واحترافي
#         - لا تُضف أو تحذف أي معلومة

#         ✏️ أخرج الترجمة فقط، بدون أي شرح أو ملاحظات إضافية.
#         """

#         with st.spinner(f"🔄 جاري الترجمة إلى {selected_lang}..."):
#             translation_response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": translation_prompt}],
#                 temperature=0.4,
#                 max_tokens=800
#             )
#             translated_text = translation_response.choices[0].message.content
#             st.session_state["translated_result"] = translated_text
#             st.session_state["translated_lang"] = target_language

#     # عرض الترجمة إن وُجدت
#     if "translated_result" in st.session_state:
#         translated_lang = st.session_state.get("translated_lang", "English")
#         st.subheader(f"🌐 الترجمة إلى {translated_lang}:")
#         st.text_area("🌐 الترجمة (قابلة للتعديل)", value=st.session_state["translated_result"], height=400)
#         # -------------------------------------------
#     # 🚀 توليد سوشيال ميديا من الترجمة
#     # -------------------------------------------

#     if "translated_result" in st.session_state:
#         st.divider()


#         if st.button(f"🚀 توليد محتوى السوشيال ميديا باللغة ({translated_lang})"):
#             source_text = st.session_state["translated_result"]

#             social_trans_prompt = f"""
#             The following is an official news article translated into {translated_lang}:

#             --------------------------------------
#             {source_text}
#             --------------------------------------

#             🎯 Task:
#             1. Create a Facebook post in {translated_lang}.
#             2. Create a Twitter/X post (max 280 characters) in {translated_lang}.
#             3. Create an Instagram caption in {translated_lang}.

#             ⚠️ Notes:
#             - Keep the meaning strictly as the translated article.
#             - Do not add or invent information.
#             - Adapt tone for social media but remain professional.

#             Format output EXACTLY like this:

#             📘 Facebook:
#             [text]

#             🐦 Twitter:
#             [text]

#             📸 Instagram:
#             [text]
#             """

#             with st.spinner(f"✍️ جاري توليد منشورات السوشيال ميديا باللغة {translated_lang} ..."):
#                 social_t_response = client.chat.completions.create(
#                     model="gpt-4o-mini",
#                     messages=[{"role": "user", "content": social_trans_prompt}],
#                     temperature=0.7,
#                     max_tokens=600
#                 )
#                 social_translated = social_t_response.choices[0].message.content
#                 st.session_state["translated_social_result"] = social_translated
#                 st.session_state["translated_social_lang"] = translated_lang


#             st.subheader(f"📱 محتوى السوشيال ميديا ({translated_lang}):")
#             st.write(social_translated)

#             # استخراج النصوص
#             fb = re.search(r"📘 Facebook:\s*(.+?)🐦", social_translated, re.DOTALL)
#             tw = re.search(r"🐦 Twitter:\s*(.+?)📸", social_translated, re.DOTALL)
#             ig = re.search(r"📸 Instagram:\s*(.+)", social_translated, re.DOTALL)

#             fb_txt = fb.group(1).strip() if fb else ""
#             tw_txt = tw.group(1).strip() if tw else ""
#             ig_txt = ig.group(1).strip() if ig else ""

#             # دوال نسخ
#             def copy_block(label, text, key):
#                 st.text_area(label, text, height=150, key=key)
#                 st.markdown(
#                     f"""
#                     <script>
#                     function copy_{key}(){{
#                         var textarea = document.querySelector('textarea[aria-label="{label}"]');
#                         navigator.clipboard.writeText(textarea.value).then(()=>{{
#                             alert("✔ Copied!");
#                         }});
#                     }}
#                     </script>
#                     <button onclick="copy_{key}()" style="padding:5px 15px;">📋 Copy</button>
#                     """,
#                     unsafe_allow_html=True
#                 )

#             st.markdown("### 📌 نسخ كل منصة:")

#             copy_block("📘 Facebook", fb_txt, "t_fb")
#             copy_block("🐦 Twitter", tw_txt, "t_tw")
#             copy_block("📸 Instagram", ig_txt, "t_ig")

#             # تحميل ملف
#             sm_file = io.BytesIO()
#             sm_file.write(social_translated.encode("utf-8"))
#             sm_file.seek(0)

#             st.download_button(
#                 label="📥 تحميل ملف السوشيال ميديا المترجم",
#                 data=sm_file,
#                 file_name=f"SocialMedia_{translated_lang}.txt",
#                 mime="text/plain"
#             )


#         translated_txt = io.BytesIO()
#         translated_txt.write(st.session_state["translated_result"].encode("utf-8"))
#         translated_txt.seek(0)

#         st.download_button(
#             label=f"📥 تحميل الترجمة ({translated_lang}) كـ ملف نصي",
#             data=translated_txt,
#             file_name=f"News_Translation_{translated_lang}.txt",
#             mime="text/plain"
#         )
with tab4:

    # -------------------------------
    # 📩 إرسال الخبر عبر البريد
    # -------------------------------
    # -------------------------------
    # 📩 إرسال الخبر عبر البريد
    # -------------------------------
    st.markdown("### 📩 إرسال الخبر عبر البريد الإلكتروني")

    # جهّز قائمة النسخ المتوفرة
    available_versions = []

    if "raw_result" in st.session_state:
        available_versions.append("📄 الخبر الخام")

    if "refined_result" in st.session_state:
        available_versions.append("✅ الخبر المرتب")

    if "translated_result" in st.session_state:
        translated_lang = st.session_state.get("translated_lang", "English")
        available_versions.append(f"🌐 الترجمة ({translated_lang})")

    if "translated_social_result" in st.session_state:
        social_lang = st.session_state.get("translated_social_lang", "English")
        available_versions.append(f"📱 سوشيال ميديا ({social_lang})")


    with st.form("email_form"):
        email_to = st.text_input("✉️ بريد المستلم")
        email_subject = st.text_input("📝 عنوان الإيميل", value="خبر صحفي رسمي")
        version_choice = st.selectbox("🗂️ اختر النسخة التي تريد إرسالها:", available_versions)
        send_now = st.form_submit_button("📨 إرسال الخبر")
    st.divider()


    if send_now:
        if "uploaded_image" in st.session_state:
            st.markdown("#### 🖼️ معاينة الصورة المرفقة:")
            try:
                import io

                image_data = st.session_state["uploaded_image"]["data"]
                image = Image.open(io.BytesIO(image_data))
                st.image(image, caption=st.session_state["uploaded_image"]["name"], width=300)
            except Exception as e:
                st.warning(f"تعذر عرض الصورة: {e}")
        selected_content = ""

        if version_choice == "📄 الخبر الخام":
            selected_content = st.session_state.get("raw_result")

        elif version_choice == "✅ الخبر المرتب":
            selected_content = st.session_state.get("refined_result")

        elif version_choice.startswith("🌐 الترجمة"):
            selected_content = st.session_state.get("translated_result")

        elif version_choice.startswith("📱 سوشيال ميديا"):
            selected_content = st.session_state.get("translated_social_result")

        if not email_to:
            st.warning("⚠️ الرجاء إدخال بريد المستلم.")
        elif not selected_content:
            st.error("❌ لا يوجد محتوى لإرساله.")
        else:
            try:
                msg = EmailMessage()
                msg.set_content(selected_content)
                msg["Subject"] = email_subject
                msg["From"] = os.getenv("SMTP_SENDER_EMAIL")
                msg["To"] = email_to
                # ✅ إرفاق الصورة إذا كانت مرفوعة في tab1
                if "uploaded_image" in st.session_state:
                    uploaded_image = st.session_state["uploaded_image"]
                    image_data = uploaded_image["data"]
                    image_name = uploaded_image["name"]
                    image_type = uploaded_image["type"]


                    msg.add_attachment(
                        image_data,
                        maintype="image",
                        subtype=image_type.split("/")[-1],
                        filename=image_name
                    )


                smtp_server = "smtp.gmail.com"
                smtp_port = 587
                smtp_user = os.getenv("SMTP_SENDER_EMAIL")
                smtp_pass = os.getenv("SMTP_SENDER_PASSWORD")

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)

                st.success("✅ تم إرسال الخبر بنجاح!")
            except Exception as e:
                st.error(f"❌ حدث خطأ أثناء الإرسال: {e}")
