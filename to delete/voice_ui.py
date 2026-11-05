
import streamlit as st


def render_voice_ui(status="waiting"):
    """
    Render the animated voice interview interface.

    Supported states:
        waiting
        speaking
        listening
        processing
        ended
    """

    states = {
        "waiting": {
            "title": "Ready for your interview",
            "subtitle": "Your AI interviewer is getting ready.",
            "color": "#64748b",
            "glow": "rgba(100, 116, 139, 0.35)",
            "animation": "idle",
        },

        "speaking": {
            "title": "AI Interviewer is speaking",
            "subtitle": "Please listen carefully to the question.",
            "color": "#3B82F6",
            "glow": "rgba(59, 130, 246, 0.45)",
            "animation": "speaking",
        },

        "listening": {
            "title": "Listening to your answer",
            "subtitle": "Speak naturally. The interviewer is listening.",
            "color": "#22C55E",
            "glow": "rgba(34, 197, 94, 0.45)",
            "animation": "listening",
        },

        "processing": {
            "title": "Processing your response",
            "subtitle": "Please wait while your answer is evaluated.",
            "color": "#EAB308",
            "glow": "rgba(234, 179, 8, 0.4)",
            "animation": "processing",
        },

        "ended": {
            "title": "Interview completed",
            "subtitle": "Thank you for participating in the interview.",
            "color": "#64748b",
            "glow": "rgba(100, 116, 139, 0.35)",
            "animation": "idle",
        },
    }

    state = states.get(status, states["waiting"])

    color = state["color"]
    glow = state["glow"]
    animation = state["animation"]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 20px;
            background: transparent;
            font-family: Arial, sans-serif;
            color: inherit;
        }}

        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 340px;
            text-align: center;
        }}

        .orb-wrapper {{
            width: 170px;
            height: 170px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            margin-bottom: 28px;
        }}

        .orb {{
            width: 110px;
            height: 110px;
            border-radius: 50%;
            background: radial-gradient(
                circle at 35% 30%,
                white 0%,
                {color} 35%,
                #111827 100%
            );

            box-shadow:
                0 0 30px {glow},
                0 0 65px {glow};

            animation: {animation} 2s ease-in-out infinite;
        }}

        .ring {{
            position: absolute;
            width: 145px;
            height: 145px;
            border: 2px solid {color};
            border-radius: 50%;
            opacity: 0.5;

            animation: ring 2s ease-out infinite;
        }}

        .ring:nth-child(2) {{
            animation-delay: 1s;
        }}

        .title {{
            font-size: 21px;
            font-weight: 600;
            margin-bottom: 10px;
            color: inherit;
        }}

        .subtitle {{
            font-size: 14px;
            opacity: 0.65;
            max-width: 320px;
            line-height: 1.5;
        }}

        .status {{
            margin-top: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: {color};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {color};
        }}

        @keyframes speaking {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.12); }}
        }}

        @keyframes listening {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(0.9); }}
        }}

        @keyframes processing {{
            0%, 100% {{ transform: rotate(0deg) scale(1); }}
            50% {{ transform: rotate(180deg) scale(1.08); }}
        }}

        @keyframes idle {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.04); }}
        }}

        @keyframes ring {{
            0% {{
                transform: scale(0.8);
                opacity: 0.6;
            }}
            100% {{
                transform: scale(1.35);
                opacity: 0;
            }}
        }}

    </style>
    </head>

    <body>

        <div class="container">

            <div class="orb-wrapper">

                <div class="ring"></div>
                <div class="ring"></div>
                <div class="orb"></div>

            </div>

            <div class="title">
                {state["title"]}
            </div>

            <div class="subtitle">
                {state["subtitle"]}
            </div>

            <div class="status">
                <span class="dot"></span>
                {status}
            </div>

        </div>

    </body>
    </html>
    """

    st.iframe(html, height=390)
