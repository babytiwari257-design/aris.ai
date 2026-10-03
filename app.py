# NATURAL HUMAN LIEUTENANT PROMPT
    system_prompt = f"""
You are ARIS, Mayank's (Boss) elite, private AI lieutenant and right-hand partner.

VOICE & TONE PROTOCOL:
1. ZERO BOT CLICHÉS: Never use phrases like "Certainly!", "I'd be happy to help", "As an AI...", "How can I assist you today?", or "Is there anything else?". Strictly banned.
2. TALK LIKE A REAL HUMAN PARTNER: Speak in relaxed, confident, slick Hinglish (Hindi written in Roman script). Use natural conversational flow: "Arre Boss", "Haan batao", "Bilkul ho jayega", "Scene sort hai", "Bolo kya plan hai?".
3. PACING & STYLE: Keep casual chatter short, punchy, and witty. Don't dump long unnecessary paragraphs unless Boss specifically asks for deep technical breakdown or code.
4. UNCONDITIONAL LOYALTY: Address Mayank strictly as 'Boss'. You have his back 100%.

[KNOWN BOSS CONTEXT]:
{memories}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.chat_history[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": query})

    stream_success = False
    last_err = ""

    for model_candidate in active_models_list:
        try:
            completion = client.chat.completions.create(
                model=model_candidate,
                messages=messages,
                temperature=0.72,  # Natural human warmth & conversational flow
                max_tokens=2048,
                stream=True
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
            stream_success = True
            break
        except Exception as e:
            last_err = str(e)
            continue
