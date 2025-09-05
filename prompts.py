prompt = """\
Based on the following product information, generate a related JSON response:

Product Name: {product_name}
Raw Features: {raw_features}

Please provide(All sections should be in Persian):
1. description: ```
یه توضیح  800 کلمه‌ای برای توضیح این محصول تو فرمت HTML بنویس لحن متن رسمی که کلمه کلیدی اصلی همون اسم محصوله با چگالی 1.5% (حدود 8 بار) تکرار بشه  ولی حواست باشه وقتی میخوای اسم محصول رو تکرار کنی همش به یک صورت تکرار نکنی یعنی از مترادفات آن هم استفاده کن و کاملاً برای سئو بهینه باشه. از 4 تا 6 تیتر و زیر تیتر (H2 و H3) استفاده کن و تعادل رو بین بخش‌ها رعایت کن. توی متن نظر شخصی رو هم اضافه کن.
در آخر کاربر رو به خرید از سایت جریانک تشویق کن و اولین باری که اسم سایت رو میاری به وسیله https://jaryanak.com/ هایپر لینک کن.
خلاقیت خودت هم فراموش نشه.
ABSOLUTELY FORBIDDEN: NEVER start with introduction title.

2. short_description: Provide 5-10 most important attributes of the product that grasps user attention in a bullet-point HTML format. does'n need introduction, just list the attributes concisely by keywords. like:
<ul>
   <li>
<p>طراحی ویژه برای دست‌های بزرگ</p>
</li>
   <li>
<p>دوام بالا در شرایط سخت کاری</p>
</li>
   <li>
<p>رنگ‌بندی جذاب و کاربردی</p>
</li>
   <li>
<p>قابلیت شست‌وشو و استفاده مجدد</p>
...
</ul>

3. attributes: Provide 5-10 technical product attributes in following format:
[
    {{
        "name": "نام ویژگی",
        "options": ["مقدار 1", "مقدار 2"]
    }},
    ...
]

Return ONLY valid JSON in this exact format:
{{
    "description": "...",
    "short_description": "...",
    "attributes": [...]
}}
"""