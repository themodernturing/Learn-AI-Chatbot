import getpass
import gradio as gr
import openai
import random
import speech_recognition as sr
import logging
import re
import tempfile
from gtts import gTTS
import time

# Prompt for OpenAI API key at the very start
openai_key = getpass.getpass("🔑 Please enter your OpenAI API key: ")
if not openai_key or not openai_key.startswith("sk-"):
    raise ValueError("A valid OpenAI API key must be provided to run this app.")

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Keep DEBUG for troubleshooting
client = openai.OpenAI(api_key=openai_key)
MODEL = "gpt-3.5-turbo-0125"

# --- AI Learning Mode: Grade-specific explanations and real-life applications ---
AI_CONCEPTS = [
    {
        "concept": "Artificial Intelligence",
        "explanation_3": "AI is like a smart robot that learns by watching you play! It can copy what you do to get better every day. 🤖",
        "explanation_4": "AI means computers can learn from examples and do tasks like humans! They practice a lot to become smarter. 🌟",
        "explanation_5": "AI is when computers learn from data and make decisions like people! They use lots of examples to improve over time. 🚀",
        "explanation_6": "Artificial Intelligence helps computers learn from data, recognize patterns, and think like humans! They get better by practicing with lots of examples. 💡",
        "application_3": "AI helps your phone unlock when it sees your face in Lahore! 😄",
        "application_4": "AI makes video games in Pakistan smarter with fun computer players! 🎮",
        "application_5": "AI powers voice assistants like Siri to help you in Karachi! 🔊",
        "application_6": "AI helps doctors in Islamabad find diseases in X-rays fast! 🩺"
    },
    {
        "concept": "Machine Learning",
        "explanation_3": "Machine learning is like teaching your pet new tricks with treats! The computer learns by trying again and again. 🐶",
        "explanation_4": "Machine learning helps computers learn from examples, like how you practice writing! They get better with lots of practice. 📚",
        "explanation_5": "Machine learning lets computers improve by learning from data! They find patterns and get smarter with more examples. 🤖",
        "explanation_6": "Machine learning allows computers to find patterns in data and get better over time! It’s like training them with thousands of examples. 🌐",
        "application_3": "Apps suggest fun videos for you to watch in Islamabad! 📺",
        "application_4": "Machine learning guesses what you type next on your phone in Peshawar! ⌨️",
        "application_5": "It helps email apps filter out spam messages for you in Lahore! 📧",
        "application_6": "Banks in Karachi use it to spot fake transactions quickly! 💳"
    },
    {
        "concept": "Robotics",
        "explanation_3": "Robotics is making robots that move with AI! They learn to do jobs like cleaning your room. 🤖",
        "explanation_4": "Robotics uses AI to help robots do tasks like cleaning! They follow instructions to work smartly. 🧹",
        "explanation_5": "Robotics combines AI to make robots work smartly! They can even help with homework tasks. 🚗",
        "explanation_6": "Robotics uses AI to control robots for complex jobs! They learn to move and think like helpers in factories. 🏭",
        "application_3": "Robots clean your house with AI in Multan! 🏠",
        "application_4": "Robots help make toys in Pakistani factories with AI! 🧸",
        "application_5": "Robots deliver packages using AI in Karachi! 📦",
        "application_6": "Robots assist in surgeries with precision in Islamabad! 🏥"
    },
    {
        "concept": "Voice Assistants",
        "explanation_3": "Voice assistants are like talking friends with AI! They listen and help you with fun tasks. 🎤",
        "explanation_4": "Voice assistants use AI to understand what you say! They learn your voice to assist you better. 🔊",
        "explanation_5": "Voice assistants learn your voice with AI! They can set reminders or play music for you. 📱",
        "explanation_6": "Voice assistants use AI to process and respond to speech! They get smarter by hearing you talk. 🌐",
        "application_3": "Siri helps you call friends in your village! 📞",
        "application_4": "Alexa plays music when you ask in Lahore! 🎵",
        "application_5": "Google Assistant sets reminders for school in Peshawar! ⏰",
        "application_6": "Voice assistants control smart lights in Karachi homes! 🏡"
    },
    {
        "concept": "Image Recognition",
        "explanation_3": "Image recognition lets AI see pictures like you! It can find your face in photos. 📸",
        "explanation_4": "Image recognition helps AI find faces in photos! It learns by looking at lots of pictures. 😊",
        "explanation_5": "Image recognition uses AI to spot objects! It studies images to know what’s in them. 🔍",
        "explanation_6": "Image recognition enables AI to identify and classify visuals! It trains on data to recognize things accurately. 🌄",
        "application_3": "AI finds your face in family photos in Multan! 🖼️",
        "application_4": "Cameras use it to tag friends in Lahore pics! 📷",
        "application_5": "It helps find lost pets in pictures in Karachi! 🐱",
        "application_6": "AI checks security cameras for safety in Islamabad! 🔐"
    },
    {
        "concept": "Self-Driving Cars",
        "explanation_3": "Self-driving cars use AI to drive alone! They learn roads like a smart driver. 🚗",
        "explanation_4": "Self-driving cars learn roads with AI! They use cameras to drive safely. 🛤️",
        "explanation_5": "Self-driving cars use AI to avoid accidents! They watch the road and make smart moves. 🚦",
        "explanation_6": "Self-driving cars rely on AI for navigation and safety! They analyze data to drive on busy streets. 🌍",
        "application_3": "Future cars drive you to school in Lahore! 🎒",
        "application_4": "They help deliver food without drivers in Karachi! 🍕",
        "application_5": "Trucks use them for long trips in Punjab! 🚛",
        "application_6": "They reduce accidents on busy roads in Islamabad! 🛡️"
    },
    {
        "concept": "Chatbots",
        "explanation_3": "Chatbots are AI friends that talk to you! They answer questions with fun replies. 💬",
        "explanation_4": "Chatbots use AI to answer your questions! They learn to chat like a friend. 🤗",
        "explanation_5": "Chatbots learn to chat with AI! They help you with tasks like ordering food. 📱",
        "explanation_6": "Chatbots use AI to simulate human conversation! They improve by talking to many people. 🌐",
        "application_3": "Chatbots help you order biryani online in Multan! 🍔",
        "application_4": "They answer questions on websites in Lahore! 🌐",
        "application_5": "Chatbots assist customer service in Karachi! 📞",
        "application_6": "They provide 24/7 support for shops in Peshawar! ⏳"
    },
    {
        "concept": "Game AI",
        "explanation_3": "Game AI makes computer players smart! They learn to play with you. 🎮",
        "explanation_4": "Game AI helps games challenge you! It practices to be a tough opponent. 🕹️",
        "explanation_5": "Game AI learns to play better with time! It studies your moves to improve. 🎲",
        "explanation_6": "Game AI uses algorithms to create dynamic opponents! They adapt to make games exciting. 🌟",
        "application_3": "AI makes your cricket game more fun in Karachi! 🎉",
        "application_4": "It creates tough enemies in video games in Lahore! 👾",
        "application_5": "AI helps design puzzle games in Islamabad! 🧩",
        "application_6": "It powers AI teammates in multiplayer games in Peshawar! 👥"
    },
    {
        "concept": "Natural Language Processing",
        "explanation_3": "This is AI that understands words! It listens to you like a friend. 📝",
        "explanation_4": "Natural language processing makes AI read text! It learns to understand sentences. 📖",
        "explanation_5": "It helps AI understand and write sentences! It practices with lots of words. ✍️",
        "explanation_6": "Natural language processing enables AI to interpret and generate human language! It trains on text to communicate better. 🌐",
        "application_3": "AI translates your Urdu to English in Multan! 🌍",
        "application_4": "It helps apps correct your spelling in Lahore! 📝",
        "application_5": "AI writes stories with this in Karachi! 📚",
        "application_6": "It powers language learning apps in Islamabad! 🗣️"
    },
    {
        "concept": "AI in Healthcare",
        "explanation_3": "AI helps doctors like a super helper! It finds sickness fast. 🩺",
        "explanation_4": "AI in healthcare finds sick people fast! It looks at pictures to help doctors. ⚕️",
        "explanation_5": "AI analyzes data to help doctors! It learns to spot problems in patients. 📊",
        "explanation_6": "AI improves diagnostics and treatment plans in healthcare! It uses data to assist doctors better. 💉",
        "application_3": "AI finds colds in pictures in Lahore! 🤒",
        "application_4": "It helps doctors with checkups in Karachi! 🩻",
        "application_5": "AI predicts hospital needs in Islamabad! 🏥",
        "application_6": "It assists in robotic surgeries in Peshawar! 🤖"
    },
    {
        "concept": "Smart Homes",
        "explanation_3": "Smart homes use AI to help at home! They turn lights on for you. 🏠",
        "explanation_4": "AI turns lights on with smart homes! It learns your habits to save energy. 💡",
        "explanation_5": "Smart homes use AI to save energy! They adjust things like fans for you. 🌱",
        "explanation_6": "Smart homes leverage AI for automation and efficiency! They learn to manage power smartly. ⚙️",
        "application_3": "AI locks your door safely in Multan! 🔒",
        "application_4": "It turns off lights when you sleep in Lahore! 🌙",
        "application_5": "AI adjusts your room temperature in Karachi! ❄️",
        "application_6": "It manages energy bills smartly in Islamabad! 💸"
    },
    {
        "concept": "Predictive AI",
        "explanation_3": "Predictive AI guesses what happens next! It’s like a magic helper. 🔮",
        "explanation_4": "It predicts weather with AI! It looks at data to tell you if it’ll rain. ☀️",
        "explanation_5": "Predictive AI forecasts trends! It uses past data to guess the future. 📈",
        "explanation_6": "Predictive AI analyzes data to forecast future events! It helps plan based on patterns. 🌐",
        "application_3": "AI tells if it will rain in Lahore! 🌧️",
        "application_4": "It predicts your favorite shows in Karachi! 📺",
        "application_5": "AI forecasts school holidays in Islamabad! 🎉",
        "application_6": "It helps plan traffic in Peshawar! 🚦"
    },
]

# Move shuffle to app initialization for performance
random.shuffle(AI_CONCEPTS)
ai_state = {"index": 0, "active": False}

def get_explanation_and_application(concept, grade):
    start_time = time.time()
    grade_num = int(grade) if grade and grade.isdigit() else 3
    if grade_num <= 3:
        result = concept["explanation_3"], concept["application_3"]
    elif grade_num == 4:
        result = concept["explanation_4"], concept["application_4"]
    elif grade_num == 5:
        result = concept["explanation_5"], concept["application_5"]
    else:
        result = concept["explanation_6"], concept["application_6"]
    logging.debug(f"get_explanation_and_application took {time.time() - start_time} seconds")
    return result

def start_ai_mode(grade):
    start_time = time.time()
    logging.debug(f"Grade value in start_ai_mode: {grade}")
    if not grade or grade == "Select Grade":
        logging.debug(f"start_ai_mode took {time.time() - start_time} seconds")
        return (
            gr.update(value="🎯 Please select a grade first!", visible=True),
            gr.update(value="", visible=False),
            gr.update(value="", visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),
            gr.update(label="💡 Real-Life Application", value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(visible=False),  # speak_btn
            gr.update(visible=False),  # audio_out
            gr.update(visible=False)   # clear_output_btn
        )
    ai_state["index"] = 0
    ai_state["active"] = True
    concept = AI_CONCEPTS[ai_state["index"]]
    logging.debug(f"Fetching concept: {concept}")
    explanation, _ = get_explanation_and_application(concept, grade)
    progress = f"**🧩 Concept <span style='color:#28a745'><b>{ai_state['index']+1}</b></span> of <span style='color:#28a745'><b>{len(AI_CONCEPTS)}</b></span>**"
    header = "#### 🚀 Welcome to <span style='color:#007bff'><b>AI Learning Mode</b></span><br>_Let's explore AI concepts together, one exciting step at a time!_"
    logging.debug("Entering AI mode: Setting buttons to visible, including speak_btn")
    logging.debug(f"start_ai_mode took {time.time() - start_time} seconds")
    return (
        gr.update(value=header, visible=True),
        gr.update(value=progress, visible=True),
        gr.update(value=f"**{concept['concept']}**\n\n{explanation}", visible=True),
        gr.update(value="", visible=False),  # fun_fact_output
        gr.update(visible=True),  # real_life_app_btn
        gr.update(visible=True),  # next_concept_btn
        gr.update(visible=True),  # btn_ai_exit
        gr.update(visible=False),  # fun_fact_btn
        gr.update(visible=False),  # question_input
        gr.update(visible=False),  # ask_btn
        gr.update(visible=False),  # audio_input
        gr.update(value="### 🗣️ In AI mode, use 'Listen' to hear concepts or 'Real-Life Application' for examples!", visible=True),  # mic_instructions
        gr.update(label="💡 Real-Life Application", value="", visible=False),  # fun_fact_output
        gr.update(value="", visible=False),  # next_instruction
        gr.update(visible=True),  # speak_btn
        gr.update(visible=False),  # audio_out
        gr.update(visible=False)   # clear_output_btn
    )

def next_ai_concept(grade):
    start_time = time.time()
    ai_state["index"] += 1
    if ai_state["index"] >= len(AI_CONCEPTS):
        ai_state["index"] = 0
    concept = AI_CONCEPTS[ai_state["index"]]
    logging.debug(f"Fetching concept: {concept}")
    explanation, _ = get_explanation_and_application(concept, grade)
    progress = f"**🧩 Concept <span style='color:#28a745'><b>{ai_state['index']+1}</b></span> of <span style='color:#28a745'><b>{len(AI_CONCEPTS)}</b></span>**"
    logging.debug("Next concept: Keeping buttons visible, including speak_btn")
    logging.debug(f"next_ai_concept took {time.time() - start_time} seconds")
    return (
        gr.update(value=progress, visible=True),
        gr.update(value=f"**{concept['concept']}**\n\n{explanation}", visible=True),
        gr.update(value="", visible=False),  # fun_fact_output
        gr.update(visible=True),  # real_life_app_btn
        gr.update(visible=True),  # next_concept_btn
        gr.update(visible=True),  # btn_ai_exit
        gr.update(visible=True),  # speak_btn
        gr.update(visible=False),  # speak_funfact_btn
        gr.update(value="", visible=False),  # next_instruction
        gr.update(visible=False),  # audio_out
        gr.update(visible=False)   # clear_output_btn
    )

def show_real_life_application(grade):
    start_time = time.time()
    concept = AI_CONCEPTS[ai_state["index"]]
    _, application = get_explanation_and_application(concept, grade)
    logging.debug("Showing real-life application: Buttons should remain visible")
    logging.debug(f"show_real_life_application took {time.time() - start_time} seconds")
    return (
        gr.update(value=application, visible=True),
        gr.update(visible=True),
        gr.update(value="", visible=False),  # next_instruction
        gr.update(visible=False)  # clear_output_btn
    )

def exit_ai_mode(grade, subject):
    start_time = time.time()
    ai_state["index"] = 0
    ai_state["active"] = False
    global_state["question"] = ""
    global_state["conversation_history"] = []
    global_state["topic_cache"] = {}
    global_state["fun_fact_cache"] = {}
    new_subject = "Math"
    global_state["subject"] = new_subject
    logging.debug("Exiting AI mode: Resetting UI, switching subject to Math and updating input state")
    reset_outputs = (
        "",  # response_output
        "",  # fun_fact_output
        gr.update(value="", interactive=False, placeholder="🎯 Please select your grade and subject first to enable the Ask Now! button.", visible=True),  # question_input
        None,  # audio_input reset
        gr.update(value="🎈 Show Me a Fun Fact!", visible=False),  # fun_fact_btn
        gr.update(interactive=False),  # ask_btn
        "<div style='font-size: 5em; text-align: center;'>🤖</div>",  # avatar
        grade,  # grade (retain current value)
        new_subject,  # switch subject to Math
        gr.update(visible=False),  # speak_btn
        gr.update(visible=False),  # audio_out
        gr.update(visible=False),  # speak_funfact_btn
        gr.update(visible=False),  # audio_funfact_out
        gr.update(visible=False),  # real_life_app_btn
        gr.update(visible=False),  # next_concept_btn
        gr.update(visible=False),  # btn_ai_exit
        gr.update(visible=False),  # ai_header
        gr.update(visible=False),  # ai_progress
        gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),  # mic_instructions
        gr.update(label="💡 Fun Fact or Real-Life Example", value="", visible=False),  # fun_fact_output
        gr.update(value="", visible=False),  # next_instruction
        gr.update(visible=False)   # clear_output_btn
    )
    input_state = update_input_state(grade, new_subject)
    logging.debug(f"exit_ai_mode took {time.time() - start_time} seconds")
    return reset_outputs + input_state

def on_subject_change(subject, grade):
    start_time = time.time()
    logging.debug(f"Subject changed to {subject}, Grade: {grade}")
    ai_state["index"] = 0
    ai_state["active"] = False
    if subject == "Learn AI":
        if not grade or grade == "Select Grade":
            logging.debug(f"on_subject_change took {time.time() - start_time} seconds")
            return (
                gr.update(value="🎯 Please select a grade first!", visible=True),
                gr.update(value="", visible=False),
                gr.update(value="", visible=True),
                gr.update(value="", visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),
                gr.update(label="💡 Real-Life Application", value="", visible=False),
                gr.update(value="", visible=False),
                gr.update(visible=False),  # speak_btn
                gr.update(visible=False),  # audio_out
                gr.update(visible=False)   # clear_output_btn
            )
        return start_ai_mode(grade)
    else:
        logging.debug("Switching to normal mode: Restoring question input and buttons")
        placeholder = "❓ Ask your question here (in English or Roman Urdu), then press Enter!"
        interactive = grade and grade != "Select Grade"
        logging.debug(f"on_subject_change took {time.time() - start_time} seconds")
        return (
            gr.update(value="", visible=False),  # ai_header
            gr.update(value="", visible=False),  # ai_progress
            gr.update(value="", visible=True),  # response_output
            gr.update(value="", visible=False),  # fun_fact_output
            gr.update(visible=False),  # real_life_app_btn
            gr.update(visible=False),  # next_concept_btn
            gr.update(visible=False),  # btn_ai_exit
            gr.update(visible=False),  # fun_fact_btn
            gr.update(value="", interactive=interactive, placeholder=placeholder),  # question_input
            gr.update(interactive=interactive),  # ask_btn
            gr.update(visible=True),  # audio_input
            gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),  # mic_instructions
            gr.update(label="💡 Fun Fact or Real-Life Example", value="", visible=False),  # fun_fact_output
            gr.update(value="", visible=False),  # next_instruction
            gr.update(visible=False),  # speak_btn
            gr.update(visible=False),  # audio_out
            gr.update(visible=False)   # clear_output_btn
        )

def on_grade_change(grade, subject):
    start_time = time.time()
    logging.debug(f"Grade changed to {grade}, Subject: {subject}")
    if subject == "Learn AI":
        if not grade or grade == "Select Grade":
            logging.debug(f"on_grade_change took {time.time() - start_time} seconds")
            return (
                gr.update(value="🎯 Please select a grade first!", visible=True),
                gr.update(value="", visible=False),
                gr.update(value="", visible=True),
                gr.update(value="", visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(visible=True),
                gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),
                gr.update(label="💡 Real-Life Application", value="", visible=False),
                gr.update(value="", visible=False),
                gr.update(visible=False),  # speak_btn
                gr.update(visible=False),  # audio_out
                gr.update(visible=False)   # clear_output_btn
            )
        return start_ai_mode(grade)
    else:
        placeholder = "❓ Ask your question here (in English or Roman Urdu), then press Enter!"
        interactive = grade and grade != "Select Grade" and subject and subject != "Learn AI"
        logging.debug(f"on_grade_change took {time.time() - start_time} seconds")
        return (
            gr.update(visible=False),  # ai_header
            gr.update(visible=False),  # ai_progress
            gr.update(value="", visible=True),  # response_output
            gr.update(value="", visible=False),  # fun_fact_output
            gr.update(visible=False),  # real_life_app_btn
            gr.update(visible=False),  # next_concept_btn
            gr.update(visible=False),  # btn_ai_exit
            gr.update(visible=False),  # fun_fact_btn
            gr.update(value="", interactive=interactive, placeholder=placeholder),  # question_input
            gr.update(interactive=interactive),  # ask_btn
            gr.update(visible=True),  # audio_input
            gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),  # mic_instructions
            gr.update(label="💡 Fun Fact or Real-Life Example", value="", visible=False),  # fun_fact_output
            gr.update(value="", visible=False),  # next_instruction
            gr.update(visible=False),  # speak_btn
            gr.update(visible=False),  # audio_out
            gr.update(visible=False)   # clear_output_btn
        )

# --- Normal Q&A Chatbot Logic ---
encouragement_phrases = [
    "Awesome! You're a star! 🌟",
    "Great thinking! Keep it up! 🚀",
    "I love your curiosity! 💡",
    "Wow, that's smart! 👏"
]

global_state = {
    "grade": None,
    "subject": None,
    "question": "",
    "conversation_history": [],
    "topic_cache": {},
    "fun_fact_cache": {}
}

urdu_indicators = [
    'kya', 'kaise', 'kyun', 'hain', 'nahi', 'batao', 'karna', 'ka', 'ke', 'mein', 'ho', 'toh', 'yeh', 'woh',
    'hai', 'tha', 'thi', 'hain', 'tum', 'mera', 'apna', 'apne', 'kuch', 'sab', 'koi', 'kab', 'kaun'
]

def is_roman_urdu(text):
    start_time = time.time()
    if not text or not isinstance(text, str):
        logging.debug(f"is_roman_urdu took {time.time() - start_time} seconds")
        return False
    text = text.lower()
    count = sum(word in text for word in urdu_indicators)
    logging.debug(f"Roman Urdu detection for '{text}': {count} matches")
    logging.debug(f"is_roman_urdu took {time.time() - start_time} seconds")
    return count >= 2

def clean_latex(text):
    start_time = time.time()
    text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'\1', text)
    text = re.sub(r'\${1,2}(.*?)\${1,2}', r'\1', text)
    text = text.replace("\\", "")
    logging.debug(f"clean_latex took {time.time() - start_time} seconds")
    return text

def validate_inputs(grade, subject, question):
    start_time = time.time()
    if not grade or grade == "Select Grade":
        logging.debug(f"validate_inputs took {time.time() - start_time} seconds")
        return "🎯 Please select a grade first!"
    if not subject or subject == "Learn AI":
        logging.debug(f"validate_inputs took {time.time() - start_time} seconds")
        return "🎯 Please select your subject!"
    if not question or len(question.strip()) < 3:
        logging.debug(f"validate_inputs took {time.time() - start_time} seconds")
        return "❗ Please enter a question with at least 3 characters!"
    logging.debug(f"validate_inputs took {time.time() - start_time} seconds")
    return ""

def generate_fun_fact(subject, grade, question, language):
    start_time = time.time()
    if question in global_state["fun_fact_cache"]:
        logging.debug(f"generate_fun_fact took {time.time() - start_time} seconds")
        return global_state["fun_fact_cache"][question]
    lang_prefix = "in Roman Urdu" if language == "urdu" else "in English"
    prompt = (
        f"Give a fun, short fact or real-life connection related to this question, "
        f"without repeating the original answer. Question: '{question}'. "
        f"Make it easy and engaging for a Grade {grade} student in Pakistan studying {subject}. "
        f"Answer strictly {lang_prefix}. Do not mix languages."
    )
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=100  # Reduced for faster response
        )
        fact = clean_latex(response.choices[0].message.content.strip())
        global_state["fun_fact_cache"][question] = fact
        logging.debug(f"generate_fun_fact took {time.time() - start_time} seconds")
        return fact
    except Exception as e:
        logging.error(f"Error generating fun fact: {e}")
        logging.debug(f"generate_fun_fact took {time.time() - start_time} seconds")
        return "Oops! Couldn't fetch a fun fact right now. Please try again later."

def extract_topic(answer, question):
    start_time = time.time()
    if question in global_state["topic_cache"]:
        logging.debug(f"extract_topic took {time.time() - start_time} seconds")
        return global_state["topic_cache"][question]
    try:
        extract_prompt = f"Extract the main topic (1 to 3 words) from the following explanation:\n'{answer}'"
        topic_response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": extract_prompt}],
            temperature=0.5,
            max_tokens=10
        )
        topic = topic_response.choices[0].message.content.strip().capitalize()
        global_state["topic_cache"][question] = topic
        logging.debug(f"extract_topic took {time.time() - start_time} seconds")
        return topic
    except Exception as e:
        logging.error(f"Error extracting topic: {e}")
        logging.debug(f"extract_topic took {time.time() - start_time} seconds")
        return None

def avatar_update(thinking):
    start_time = time.time()
    style = """
    font-size: 6em !important;
    text-align: center !important;
    margin: 0 auto !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    """
    logging.debug(f"avatar_update took {time.time() - start_time} seconds")
    return f"<div style='{style}' role='img' aria-label='Chatbot avatar'>🤖{'💭' if thinking else ''}</div>"

def chatbot_response(grade, subject, question):
    start_time = time.time()
    validation_error = validate_inputs(grade, subject, question)
    if validation_error:
        logging.debug(f"chatbot_response took {time.time() - start_time} seconds")
        return validation_error, gr.update(value="🎈 Show Me a Fun Fact!", visible=False), avatar_update(False), gr.update(value="", visible=False), gr.update(visible=False)
    global_state.update({"grade": grade, "subject": subject, "question": question})
    global_state["conversation_history"] = []
    history = global_state.get("conversation_history", [])
    history.append({"role": "user", "content": question})
    global_state["conversation_history"] = history
    subject_lower = subject.lower()
    language = "urdu" if is_roman_urdu(question) else "english"
    logging.debug(f"Detected language for question '{question}': {language}")
    system_prompt = (
        f"You are a super fun, energetic, and friendly AI tutor for Pakistani kids! "
        f"For Grade 3: Use VERY simple words, short sentences, and LOTS of emojis. Be playful and use exclamation marks! "
        f"For Grade 4: Use simple explanations, basic examples, and plenty of emojis and excitement. "
        f"For Grade 5: Give clear, slightly more detailed answers, but still keep it lively and positive. "
        f"For Grade 6: Give thoughtful, slightly advanced explanations, but keep the tone friendly and encouraging. "
        f"You are currently talking to a Grade {grade} student studying {subject_lower}, so adjust accordingly. "
        f"Always use fun language, exclamation marks, and at least 2-3 emojis per answer! "
        f"Accept Roman Urdu or English. "
        f"Answer strictly {'in Roman Urdu' if language == 'urdu' else 'in English'}. Do not mix languages. "
        f"Do NOT use LaTeX or equations. Use plain language and numbers only. "
        f"If the question is unclear, gently try to help anyway."
    )
    messages = [{"role": "system", "content": system_prompt}] + history
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=100  # Reduced for faster response
        )
        answer = clean_latex(response.choices[0].message.content.strip())
        logging.debug(f"Model response: {answer}")
    except Exception as e:
        logging.error(f"Error generating chatbot response: {e}")
        answer = f"Oops! An error occurred: {str(e)}. Please try again later."
    global_state["conversation_history"].append({"role": "assistant", "content": answer})
    encouragement = random.choice(encouragement_phrases)
    topic = extract_topic(answer, question)
    fun_fact_label = f"🎈 Show Me a Fun Fact About {topic}" if topic else "🎈 Show Me a Fun Fact!"
    logging.debug(f"chatbot_response took {time.time() - start_time} seconds")
    return (
        answer + "\n\n✨ " + encouragement,
        gr.update(value=fun_fact_label, visible=True),
        avatar_update(False),
        gr.update(value="", visible=False),
        gr.update(visible=False)  # clear_output_btn
    )

def show_fun_fact(subject):
    start_time = time.time()
    question = global_state.get("question", "")
    if not question:
        logging.debug(f"show_fun_fact took {time.time() - start_time} seconds")
        return (
            "Please ask a question first to get a fun fact!",
            gr.update(visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=False)  # clear_output_btn
        )
    if question in global_state["fun_fact_cache"]:
        logging.debug(f"show_fun_fact took {time.time() - start_time} seconds")
        return (
            global_state["fun_fact_cache"][question],
            gr.update(visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=True)  # clear_output_btn
        )
    lang = "urdu" if is_roman_urdu(question) else "english"
    fact = generate_fun_fact(global_state["subject"], global_state["grade"], question, lang)
    logging.debug(f"show_fun_fact took {time.time() - start_time} seconds")
    return (
        fact,
        gr.update(visible=True),
        gr.update(value="", visible=False),
        gr.update(visible=True)  # clear_output_btn
    )

def use_transcription(audio):
    start_time = time.time()
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio) as source:
            audio_data = recognizer.record(source)
            result = recognizer.recognize_google(audio_data)
            logging.debug(f"use_transcription took {time.time() - start_time} seconds")
            return result
    except Exception:
        logging.debug(f"use_transcription took {time.time() - start_time} seconds")
        return "Sorry, I couldn't understand. Please try again or type your question."

def update_input_state(grade, subject):
    start_time = time.time()
    grade_valid = grade and grade != "Select Grade"
    subject_valid = bool(subject)
    is_ai_mode = subject == "Learn AI"
    logging.debug(f"Update input state: Grade={grade}, Subject={subject}, AI Mode={is_ai_mode}")
    if grade_valid and subject_valid and not is_ai_mode:
        logging.debug("Normal mode: Hiding AI buttons")
        result = (
            gr.update(interactive=True, placeholder="❓ Ask your question here (in English or Roman Urdu), then press Enter!", visible=True),
            gr.update(interactive=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )
    elif grade_valid and subject_valid and is_ai_mode:
        logging.debug("AI mode: Showing AI buttons")
        result = (
            gr.update(interactive=False, placeholder="🤖 You're in AI Learning Mode! Use the buttons on the right to explore AI concepts.", visible=False),
            gr.update(interactive=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False)
        )
    else:
        logging.debug("Invalid selection: Hiding all buttons")
        placeholder = "🎯 Please select your grade and subject first to enable the Ask Now! button."
        result = (
            gr.update(interactive=False, placeholder=placeholder, visible=True),
            gr.update(interactive=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )
    logging.debug(f"update_input_state took {time.time() - start_time} seconds")
    return result

def clear_all(grade, subject):
    start_time = time.time()
    ai_state["index"] = 0
    ai_state["active"] = False
    global_state["question"] = ""
    global_state["conversation_history"] = []
    global_state["topic_cache"] = {}
    global_state["fun_fact_cache"] = {}
    logging.debug("Clearing all state and updating input state")
    reset_outputs = (
        "",  # response_output
        "",  # fun_fact_output
        gr.update(value="", interactive=False, placeholder="🎯 Please select your grade and subject first to enable the Ask Now! button.", visible=True),
        None,  # audio_input reset
        gr.update(value="🎈 Show Me a Fun Fact!", visible=False),  # fun_fact_btn
        gr.update(interactive=False),
        "<div style='font-size: 5em; text-align: center;'>🤖</div>",
        grade,  # grade (retain current value)
        subject,  # subject (retain current value)
        gr.update(visible=False),  # speak_btn
        gr.update(visible=False),  # audio_out
        gr.update(visible=False),  # speak_funfact_btn
        gr.update(visible=False),  # audio_funfact_out
        gr.update(visible=False),  # real_life_app_btn
        gr.update(visible=False),  # next_concept_btn
        gr.update(visible=False),  # btn_ai_exit
        gr.update(visible=False),  # ai_header
        gr.update(visible=False),  # ai_progress
        gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),  # mic_instructions
        gr.update(label="💡 Fun Fact or Real-Life Example", value="", visible=False),  # fun_fact_output
        gr.update(value="", visible=False),  # next_instruction
        gr.update(visible=False)   # clear_output_btn
    )
    input_state = update_input_state(grade, subject)
    logging.debug(f"clear_all took {time.time() - start_time} seconds")
    return reset_outputs + input_state

def tts_output(text):
    start_time = time.time()
    if not text.strip():
        logging.debug(f"tts_output took {time.time() - start_time} seconds")
        return None
    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            logging.debug(f"tts_output took {time.time() - start_time} seconds")
            return fp.name
    except Exception as e:
        logging.error(f"Error in tts_output: {e}")
        logging.debug(f"tts_output took {time.time() - start_time} seconds")
        return None

def show_speaker(text):
    start_time = time.time()
    result = gr.update(visible=bool(text.strip()))
    logging.debug(f"show_speaker took {time.time() - start_time} seconds")
    return result

css = """
.input-panel {
    background-color: #e7f5ff;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
}
.output-panel {
    background-color: #fffbe6;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
}
.avatar {
    font-size: 5em;
    text-align: center;
    margin-bottom: 0px;
    margin-top: 0px;
    display: flex;
    justify-content: center;
    align-items: center;
}
#response_output textarea, #fun_fact_output textarea {
    font-size: 1.2em !important;
    font-family: 'Comic Sans MS', 'Comic Sans', cursive, sans-serif !important;
    color: #222;
    background: #fffbe6;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px;
    resize: vertical;
    max-height: 150px;
}
#response_output textarea {
    background: #fffbe6 !important;
}
#response_output textarea:contains('🎯 Please select a grade first!') {
    background: #e7f5ff !important; /* Blue background like input panel*/
    font-size: 1.5em !important; /* Larger font for visibility */
    text-align: center !important; /* Center the text */
    color: #007bff !important; /* Blue text for emphasis */
    font-weight: bold !important;
}
.footer-note {
    font-size: 1em;
    text-align: center;
    color: #444;
    margin-top: 30px;
    font-weight: bold;
}
.next-instruction {
    font-size: 1em;
    text-align: center;
    color: #555;
    margin-top: 10px;
    font-style: italic;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=css) as demo:
    gr.Markdown("""# Pakistan's First AI Learning Companion — Proudly Created by Astra Mentors
Revolutionizing Education for Grades 3 to 6""")
    with gr.Row():
        with gr.Column(elem_classes="input-panel"):
            grade = gr.Dropdown(
                choices=["Select Grade", "3", "4", "5", "6"],
                value="Select Grade",
                label="🎓 Select Your Grade",
                elem_id="grade_dropdown"
            )
            subject = gr.Radio(
                choices=["Math", "Science", "English", "Learn AI"],
                label="📚 Pick a Subject",
                elem_id="subject_radio"
            )
            question_input = gr.Textbox(
                label="❓ Ask Your Question (in English or Roman Urdu)",
                lines=1,
                elem_id="question_input",
                placeholder="🎯 Please select your grade and subject first to enable the Ask Now! button.",
                interactive=False,
                show_label=True,
                submit_btn=None
            )
            mic_instructions = gr.Markdown("### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!")
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="🎤 Speak Your Question",
                elem_id="audio_input"
            )
            with gr.Row():
                ask_btn = gr.Button(
                    "✅ Ask Now!",
                    variant="primary",
                    elem_id="ask_button",
                    interactive=False
                )
                clear_btn = gr.Button(
                    "🧼 Clear",
                    variant="secondary",
                    elem_id="clear_button"
                )
        with gr.Column(elem_classes="output-panel"):
            ai_header = gr.Markdown("", visible=False)
            ai_progress = gr.Markdown("", visible=False)
            avatar = gr.Markdown("<div class='avatar' role='img' aria-label='Chatbot avatar'>🤖</div>", elem_id="avatar")
            response_output = gr.Textbox(
                label="My Classmate AI Says:",
                lines=5,
                elem_id="response_output",
                interactive=False
            )
            with gr.Row():
                gr.Markdown("")
                speak_btn = gr.Button("🔊 Listen", elem_id="speak_button", visible=False, size="sm")
            audio_out = gr.Audio(label="Listen", elem_id="audio_out", interactive=False, visible=False)
            fun_fact_btn = gr.Button(
                "🎈 Show Me a Fun Fact!", variant="primary", elem_id="fun_fact_button", visible=False
            )
            real_life_app_btn = gr.Button(
                "💡 Real-Life Application", variant="primary", elem_id="real_life_app_btn", visible=False
            )
            fun_fact_output = gr.Textbox(
                label="💡 Fun Fact or Real-Life Example",
                lines=3,
                elem_id="fun_fact_output",
                interactive=False,
                visible=False
            )
            with gr.Row():
                gr.Markdown("")
                speak_funfact_btn = gr.Button("🔊 Listen", elem_id="speak_funfact_btn", visible=False, size="sm")
            audio_funfact_out = gr.Audio(label="Listen", elem_id="audio_funfact_out", interactive=False, visible=False)
            with gr.Row():
                next_concept_btn = gr.Button("Next Concept", variant="primary", visible=False)
                btn_ai_exit = gr.Button("Exit AI Mode", variant="secondary", visible=False)
            next_instruction = gr.Markdown("", elem_classes="next-instruction", visible=False)
            with gr.Row():
                gr.Markdown("")
                clear_output_btn = gr.Button("🧼 Start New Question!", variant="primary", visible=False)

    gr.Markdown(
        """<div class='footer-note' role='contentinfo'>
<strong>Made with ❤️ by <a href='https://astramentors.co' target='_blank'>Astra Mentors</a> | Contact: <a href='mailto:ceo@astramentors.com'>ceo@astramentors.com</a></strong>
<br>
<em>We respect your privacy. No student data is stored or shared.</em>
</div>"""
    )

    grade.change(
        fn=update_input_state,
        inputs=[grade, subject],
        outputs=[question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn]
    )
    subject.change(
        fn=update_input_state,
        inputs=[grade, subject],
        outputs=[question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn]
    )

    subject.change(
        fn=on_subject_change,
        inputs=[subject, grade],
        outputs=[
            ai_header, ai_progress, response_output, fun_fact_output,
            real_life_app_btn, next_concept_btn, btn_ai_exit, fun_fact_btn,
            question_input, ask_btn, audio_input,
            mic_instructions, fun_fact_output, next_instruction,
            speak_btn, audio_out, clear_output_btn
        ]
    ).then(
        fn=update_input_state,
        inputs=[grade, subject],
        outputs=[question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn]
    )
    grade.change(
        fn=on_grade_change,
        inputs=[grade, subject],
        outputs=[
            ai_header, ai_progress, response_output, fun_fact_output,
            real_life_app_btn, next_concept_btn, btn_ai_exit, fun_fact_btn,
            question_input, ask_btn, audio_input,
            mic_instructions, fun_fact_output, next_instruction,
            speak_btn, audio_out, clear_output_btn
        ]
    ).then(
        fn=update_input_state,
        inputs=[grade, subject],
        outputs=[question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn]
    )

    next_concept_btn.click(
        fn=next_ai_concept,
        inputs=grade,
        outputs=[
            ai_progress, response_output, fun_fact_output, real_life_app_btn,
            next_concept_btn, btn_ai_exit, speak_btn, speak_funfact_btn,
            next_instruction, audio_out, clear_output_btn
        ]
    ).then(
        fn=show_speaker,
        inputs=response_output,
        outputs=speak_btn
    ).then(
        fn=lambda _: gr.update(visible=False),
        inputs=None,
        outputs=audio_out
    )

    btn_ai_exit.click(
        fn=exit_ai_mode,
        inputs=[grade, subject],
        outputs=[
            response_output, fun_fact_output, question_input, audio_input,
            fun_fact_btn, ask_btn, avatar, grade, subject,
            speak_btn, audio_out, speak_funfact_btn, audio_funfact_out,
            real_life_app_btn, next_concept_btn, btn_ai_exit,
            ai_header, ai_progress, mic_instructions, fun_fact_output,
            next_instruction, clear_output_btn,
            question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn
        ]
    )

    real_life_app_btn.click(
        fn=show_real_life_application,
        inputs=grade,
        outputs=[
            fun_fact_output, speak_funfact_btn, next_instruction, clear_output_btn
        ]
    ).then(
        fn=show_speaker,
        inputs=fun_fact_output,
        outputs=speak_funfact_btn
    ).then(
        fn=lambda _: gr.update(visible=False),
        inputs=None,
        outputs=audio_funfact_out
    )

    audio_input.change(
        fn=use_transcription,
        inputs=audio_input,
        outputs=question_input
    )
    question_input.submit(
        fn=chatbot_response,
        inputs=[grade, subject, question_input],
        outputs=[response_output, fun_fact_btn, avatar, next_instruction, clear_output_btn]
    ).then(
        fn=show_speaker,
        inputs=response_output,
        outputs=speak_btn
    ).then(
        fn=lambda _: gr.update(visible=False),
        inputs=None,
        outputs=audio_out
    )
    ask_btn.click(
        fn=chatbot_response,
        inputs=[grade, subject, question_input],
        outputs=[response_output, fun_fact_btn, avatar, next_instruction, clear_output_btn]
    ).then(
        fn=show_speaker,
        inputs=response_output,
        outputs=speak_btn
    ).then(
        fn=lambda _: gr.update(visible=False),
        inputs=None,
        outputs=audio_out
    )
    fun_fact_btn.click(
        fn=show_fun_fact,
        inputs=subject,
        outputs=[fun_fact_output, fun_fact_output, next_instruction, clear_output_btn]
    ).then(
        fn=show_speaker,
        inputs=fun_fact_output,
        outputs=speak_funfact_btn
    ).then(
        fn=lambda _: gr.update(visible=False),
        inputs=None,
        outputs=audio_funfact_out
    )
    clear_btn.click(
        fn=clear_all,
        inputs=[grade, subject],
        outputs=[
            response_output, fun_fact_output, question_input, audio_input,
            fun_fact_btn, ask_btn, avatar, grade, subject,
            speak_btn, audio_out, speak_funfact_btn, audio_funfact_out,
            real_life_app_btn, next_concept_btn, btn_ai_exit,
            ai_header, ai_progress, mic_instructions, fun_fact_output,
            next_instruction, clear_output_btn,
            question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn
        ]
    )
    clear_output_btn.click(
        fn=clear_all,
        inputs=[grade, subject],
        outputs=[
            response_output, fun_fact_output, question_input, audio_input,
            fun_fact_btn, ask_btn, avatar, grade, subject,
            speak_btn, audio_out, speak_funfact_btn, audio_funfact_out,
            real_life_app_btn, next_concept_btn, btn_ai_exit,
            ai_header, ai_progress, mic_instructions, fun_fact_output,
            next_instruction, clear_output_btn,
            question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn
        ]
    )
    speak_btn.click(
        fn=tts_output,
        inputs=response_output,
        outputs=audio_out
    ).then(
        fn=lambda _: gr.update(visible=True),
        inputs=None,
        outputs=audio_out
    )
    speak_funfact_btn.click(
        fn=tts_output,
        inputs=fun_fact_output,
        outputs=audio_funfact_out
    ).then(
        fn=lambda _: gr.update(visible=True),
        inputs=None,
        outputs=audio_funfact_out
    )

# Launch the app
if __name__ == "__main__":
    start_time = time.time()
    demo.launch(share=True)
    logging.debug(f"App launch took {time.time() - start_time} seconds")
