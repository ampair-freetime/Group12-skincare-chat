import streamlit as st
import json
from search import chat_with_llm, web_search

st.set_page_config(page_title="Skincare Chat", page_icon="🧴")

#Custom Display (CSS)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;500;600&display=swap');

/* เปลี่ยนฟอนต์ */
body, div, p, h1, h2, h3, h4, h5, h6, label, input, textarea, button {
    font-family: 'Kanit', sans-serif !important;
}

/* สีพื้นหลังหลัก */
.stApp { background-color: #fff0f7 !important; }

/* สี sidebar */
.stSidebar { background-color: #ffd9e3 !important; }

/* ซ่อน footer */
footer {visibility: hidden !important;}

/* สีปุ่มคำถามยอดฮิต */
div.stButton > button {
    background-color: #faf7f8;
    color: #4a0033;
    border-radius: 20px;
    border: none;
    padding: 10px 20px;
    font-weight: 500;
    transition: 0.2s;
}
div.stButton > button:hover {
    background-color: #ffa6b9;
    color: white;
    transform: scale(1.03);
}

</style>
""", unsafe_allow_html=True)

# Sidebar 
with st.sidebar:
    st.header("⚙️ Setting" if st.session_state.get("lang", "en") == "en" else "⚙️ การตั้งค่า")
    
    # Language switch
    if "lang" not in st.session_state:
        st.session_state.lang = "en"

    lang_options = ["🇹🇭 ไทย (TH)", "🇺🇲 English (EN)"]
    default_idx = 0 if st.session_state.lang == "th" else 1

    lang = st.selectbox("🌐 Language / ภาษา", lang_options, index=default_idx)

    new_lang = "th" if "ไทย" in lang else "en"
    if st.session_state.lang != new_lang:
        st.session_state.lang = new_lang
        st.rerun()


    # Clear Chat
    st.subheader("💬 Clear Chat" if st.session_state.lang == "en" else "💬 ล้างแชท")
    if st.button("🗑️ Clear" if st.session_state.lang == "en" else "🗑️ ล้าง"):
        current_lang = st.session_state.lang

        sys_prompt = (
            "You are a skincare expert. Find 3 skincare products based on the user's query."
            if current_lang == "en"
            else "คุณคือผู้เชี่ยวชาญด้านสกินแคร์ ช่วยแนะนำผลิตภัณฑ์ 3 ชนิดตามคำถามของผู้ใช้"
        )
        st.session_state.messages = [{"role": "system", "content": sys_prompt}]
        st.session_state.lang = current_lang
        st.rerun()


#  Language Content 
if st.session_state.lang == "th":
    title = "💬 แชท AI แนะนำสกินแคร์พร้อมค้นหาข้อมูลจากเว็บ"
    info = "พิมพ์ส่วนผสมหรือคำถาม เช่น 'retinol' เพื่อให้ AI แนะนำผลิตภัณฑ์ที่เหมาะสมกับสิ่งที่คุณต้องการ"
    input_placeholder = "พิมพ์คำถามหรือชื่อส่วนผสม..."
    thinking = "🧠 กำลังวิเคราะห์และค้นหาข้อมูล..."
else:
    title = "💬 AI Skincare Chat with Web Search"
    info = "Type an ingredient or question, e.g. 'retinol', and I’ll suggest products that fit you best."
    input_placeholder = "Type your question or ingredient..."
    thinking = "🧠 Thinking and searching..."

st.title(title)
# Color info
st.markdown(f"""
<div style="
    background-color: #ffb3c6;  
    color: #4a0033;             
    border-radius: 10px;
    padding: 12px 18px;
    font-weight: 500;
    font-family: 'Kanit', sans-serif;
">
{info}
</div>
""", unsafe_allow_html=True)

#  Example Questions 
if st.session_state.lang == "th":
    section_title = "### 🔍 คำถามยอดฮิต"
    q1_label = "✨ วิธีเลือกสกินแคร์ให้เหมาะกับผิว"
    q2_label = "💧 ส่วนผสมช่วยให้ผิวชุ่มชื้น"
    q3_label = "☀️ ครีมกันแดดที่เหมาะกับผิวแพ้ง่าย"

    q1_prompt = "วิธีเลือกสกินแคร์ให้เหมาะกับสภาพผิว"
    q2_prompt = "ส่วนผสมที่ช่วยให้ผิวชุ่มชื้นมีอะไรบ้าง"
    q3_prompt = "แนะนำครีมกันแดดที่เหมาะกับผิวแพ้ง่าย"
else:
    section_title = "### 🔍 Popular Questions"
    q1_label = "✨ How to choose the right skincare"
    q2_label = "💧 Hydrating ingredients to look for"
    q3_label = "☀️ Sunscreen for sensitive skin"

    q1_prompt = "How to choose skincare suitable for my skin type"
    q2_prompt = "What ingredients help improve skin hydration"
    q3_prompt = "Recommend sunscreens suitable for sensitive skin"

st.write(section_title)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button(q1_label, key="q1_btn"):
        st.session_state["queued_prompt"] = q1_prompt
        st.rerun()

with col2:
    if st.button(q2_label, key="q2_btn"):
        st.session_state["queued_prompt"] = q2_prompt
        st.rerun()

with col3:
    if st.button(q3_label, key="q3_btn"):
        st.session_state["queued_prompt"] = q3_prompt
        st.rerun()


#  Chat Memory 
if "messages" not in st.session_state:
    sys_prompt = (
        "You are a skincare expert. Find 3 skincare products based on the user's query."
        if st.session_state.lang == "en"
        else "คุณคือผู้เชี่ยวชาญด้านสกินแคร์ ช่วยแนะนำผลิตภัณฑ์ 3 ชนิดตามคำถามของผู้ใช้"
    )
    st.session_state.messages = [{"role": "system", "content": sys_prompt}]

#  Display Chat 
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

#  Handle example question clicks 
if len(st.session_state.messages) > 1 and st.session_state.messages[-1]["role"] == "user" and "prompt_from_button" not in st.session_state:
    last_user_msg = st.session_state.messages[-1]["content"]
    st.session_state["prompt_from_button"] = True  

    with st.chat_message("user"):
        st.markdown(last_user_msg)

    with st.chat_message("assistant"):
        with st.spinner(thinking):
            resp = chat_with_llm(st.session_state.messages)
            assistant_msg = resp.choices[0].message
            st.markdown(assistant_msg.content)
            st.session_state.messages.append({"role": "assistant", "content": assistant_msg.content})

    st.session_state.pop("prompt_from_button", None)

#  Chat Input 
prompt = st.chat_input(input_placeholder)

queued = st.session_state.pop("queued_prompt", None)
effective_prompt = prompt or queued

if effective_prompt:
    st.session_state.messages.append({"role": "user", "content": effective_prompt})
    with st.chat_message("user"):
        st.markdown(effective_prompt)

    # assistant response
    with st.chat_message("assistant"):
        with st.spinner(thinking):
            resp = chat_with_llm(st.session_state.messages)   
            assistant_msg = resp.choices[0].message

            if getattr(assistant_msg, "tool_calls", None):
                assistant_msg_dict = {
                    "role": assistant_msg.role,
                    "content": assistant_msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments or "{}",
                            },
                        }
                        for tc in assistant_msg.tool_calls
                    ],
                }
                st.session_state.messages.append(assistant_msg_dict)

                for tc in assistant_msg.tool_calls:
                    args = json.loads(tc.function.arguments or "{}")
                    result = web_search(
                        query=args.get("query", ""),
                        num_results=args.get("num_results", 5),
                    )

                    if "results" in result:
                        st.markdown("### 🔍 Search Results")
                        for item in result["results"]:
                            st.markdown(f"- **[{item['title']}]({item['url']})**\n  {item['snippet']}")
                    else:
                        st.write(result)

                    st.session_state.messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    })

                final = chat_with_llm(st.session_state.messages)
                answer = final.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})

            else:
                st.markdown(assistant_msg.content)
                st.session_state.messages.append({
                    "role": assistant_msg.role,
                    "content": assistant_msg.content,
                })