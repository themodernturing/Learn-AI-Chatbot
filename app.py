import getpass
import gradio as gr
import random
import speech_recognition as sr
import time
import logging
import re
import tempfile
from gtts import gTTS
import openai
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Prompt for OpenAI API key
openai_key = getpass.getpass("🔑 Please enter your OpenAI API key: ")
if not openai_key or not openai_key.startswith("sk-"):
    raise ValueError("A valid OpenAI API key must be provided.")

client = openai.OpenAI(api_key=openai_key)
MODEL = "gpt-3.5-turbo-0125"

# AI Concepts
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
        "explanation_3": "Machine Learning is like teaching a robot to learn from toys! It gets better by trying again and again. 🧸",
        "explanation_4": "Machine Learning helps computers learn from examples! It’s like practicing to get better at a game. 🎲",
        "explanation_5": "Machine Learning lets computers learn patterns from data! It’s like studying examples to solve puzzles. 🧩",
        "explanation_6": "Machine Learning allows computers to find patterns in data and improve without being told exactly how! It’s like learning from practice. 📊",
        "application_3": "Machine Learning helps Netflix suggest fun cartoons in Peshawar! 📺",
        "application_4": "Machine Learning makes your camera take better photos in Quetta! 📸",
        "application_5": "Machine Learning helps apps recommend songs you love in Lahore! 🎵",
        "application_6": "Machine Learning predicts weather in Karachi to plan your day! ☀️"
    },
    {
        "concept": "Neural Networks",
        "explanation_3": "Neural Networks are like a robot brain with tiny helpers! They work together to solve problems. 🧠",
        "explanation_4": "Neural Networks copy how our brain works! They learn by connecting ideas like a puzzle. 🧩",
        "explanation_5": "Neural Networks are computer brains that learn by linking information! They help solve big problems. 💻",
        "explanation_6": "Neural Networks mimic the human brain to process data and make decisions! They learn by connecting patterns. 🌐",
        "application_3": "Neural Networks help cars in Islamabad know where to go! 🚗",
        "application_4": "Neural Networks make chatbots in Lahore answer your questions! 💬",
        "application_5": "Neural Networks help detect fake photos in Karachi! 🖼️",
        "application_6": "Neural Networks power smart farming tools in Punjab! 🌾"
    },
    {
        "concept": "Natural Language Processing",
        "explanation_3": "NLP is like teaching a robot to talk like you! It understands your words and chats back. 🗣️",
        "explanation_4": "NLP helps computers understand our words! It’s like teaching them to read your messages. 📱",
        "explanation_5": "NLP lets computers understand and reply to what we say! It’s like having a smart friend who listens. 🎤",
        "explanation_6": "Natural Language Processing enables computers to process and respond to human language! It powers chatbots and translators. 🌍",
        "application_3": "NLP lets you talk to Google in Urdu in Lahore! 🗨️",
        "application_4": "NLP helps translate English to Urdu in Karachi apps! 📖",
        "application_5": "NLP makes smart speakers in Islamabad understand you! 🔊",
        "application_6": "NLP helps customer service bots in Pakistan answer fast! 📞"
    },
    {
        "concept": "Computer Vision",
        "explanation_3": "Computer Vision is like giving robots eyes to see! They can look at pictures and understand them. 👀",
        "explanation_4": "Computer Vision helps computers see and understand images! It’s like teaching them to look at photos. 🖼️",
        "explanation_5": "Computer Vision lets computers recognize objects in pictures! It’s like giving them super eyes. 📷",
        "explanation_6": "Computer Vision enables computers to interpret visual data, like identifying objects or faces! It’s used in cameras and drones. 🚁",
        "application_3": "Computer Vision helps cameras in Lahore spot your smile! 😊",
        "application_4": "Computer Vision makes cars in Karachi see road signs! 🚦",
        "application_5": "Computer Vision checks fruits in markets in Islamabad! 🍎",
        "application_6": "Computer Vision powers security cameras in Pakistan! 📹"
    }
]

# Validate AI_CONCEPTS
required_keys = ["concept", "explanation_3", "explanation_4", "explanation_5", "explanation_6",
                "application_3", "application_4", "application_5", "application_6"]
for concept in AI_CONCEPTS:
    if not all(key in concept for key in required_keys):
        logger.error(f"Invalid concept: {concept.get('concept', 'Unknown')}")
        raise ValueError(f"Concept missing required keys: {concept.get('concept')}")

random.shuffle(AI_CONCEPTS)
ai_state = {"index": 0, "active": False}

def get_explanation_and_application(concept, grade):
    start_time = time.time()
    try:
        grade_num = int(grade) if grade and grade.isdigit() and 3 <= int(grade) <= 6 else 3
        explanation_key = f"explanation_{grade_num}"
        application_key = f"application_{grade_num}"
        if explanation_key not in concept or application_key not in concept:
            raise KeyError(f"Missing key in concept: {explanation_key} or {application_key}")
        result = concept[explanation_key], concept[application_key]
        logger.debug(f"get_explanation_and_application took {time.time() - start_time:.3f} seconds")
        return result
    except Exception as e:
        logger.error(f"Error in get_explanation_and_application: {e}")
        return f"Error: Invalid concept data for grade {grade}", "Error: Unable to fetch application"

def start_ai_mode(grade):
    start_time = time.time()
    logger.debug(f"Entering start_ai_mode with grade: {grade}")
    if not grade or grade == "Select Grade" or not grade.isdigit() or int(grade) < 3 or int(grade) > 6:
        logger.warning(f"Invalid grade: {grade}")
        return (
            gr.update(value="🎯 Please select a valid grade (3–6)!", visible=True),
            gr.update(value="", visible=False),
            gr.update(value="", visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value="", interactive=False, placeholder="🤖 You're in AI Learning Mode! Select a grade to start.", visible=True),
            gr.update(interactive=False),
            gr.update(visible=True),
            gr.update(value="### 🗣️ In AI mode, use 'Listen' to hear concepts or 'Real-Life Application' for examples!", visible=True),
            gr.update(label="💡 Real-Life Application", value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )
    ai_state["index"] = 0
    ai_state["active"] = True
    try:
        concept = AI_CONCEPTS[ai_state["index"]]
        explanation, _ = get_explanation_and_application(concept, grade)
        if "Error" in explanation:
            raise ValueError(explanation)
        progress = f"**🧩 Concept <span style='color:#28a745'><b>{ai_state['index']+1}</b></span> of <span style='color:#28a745'><b>{len(AI_CONCEPTS)}</b></span>**"
        header = "#### 🚀 Welcome to <span style='color:#007bff'><b>AI Learning Mode</b></span><br>_Let's explore AI concepts together, one exciting step at a time!_"
        logger.debug(f"start_ai_mode succeeded, took {time.time() - start_time:.3f} seconds")
        return (
            gr.update(value=header, visible=True),
            gr.update(value=progress, visible=True),
            gr.update(value=f"**{concept['concept']}**\n\n{explanation}", visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value="", interactive=False, placeholder="🤖 You're in AI Learning Mode! Use the buttons on the right to explore AI concepts.", visible=True),
            gr.update(interactive=False),
            gr.update(visible=True),
            gr.update(value="### 🗣️ In AI mode, use 'Listen' to hear concepts or 'Real-Life Application' for examples!", visible=True),
            gr.update(label="💡 Real-Life Application", value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False)
        )
    except Exception as e:
        logger.error(f"start_ai_mode failed: {str(e)}")
        return (
            gr.update(value=f"Error loading AI concept: {str(e)}", visible=True),
            gr.update(value="", visible=False),
            gr.update(value="", visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(value="", interactive=False, placeholder="🤖 Error in AI Mode. Try 'Next Concept'.", visible=True),
            gr.update(interactive=False),
            gr.update(visible=True),
            gr.update(value="### 🗣️ Error occurred. Use 'Next Concept' to continue.", visible=True),
            gr.update(label="💡 Real-Life Application", value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(visible=True),
            gr.update(visible=False),
            gr.update(visible=False)
        )

def next_ai_concept(grade):
    start_time = time.time()
    ai_state["index"] += 1
    if ai_state["index"] >= len(AI_CONCEPTS):
        ai_state["index"] = 0
    concept = AI_CONCEPTS[ai_state["index"]]
    explanation, _ = get_explanation_and_application(concept, grade)
    progress = f"**🧩 Concept <span style='color:#28a745'><b>{ai_state['index']+1}</b></span> of <span style='color:#28a745'><b>{len(AI_CONCEPTS)}</b></span>**"
    logger.debug(f"next_ai_concept took {time.time() - start_time:.3f} seconds")
    return (
        gr.update(value=progress, visible=True),
        gr.update(value=f"**{concept['concept']}**\n\n{explanation}", visible=True),
        gr.update(value="", visible=False),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=False),
        gr.update(value="", visible=False),
        gr.update(visible=False),
        gr.update(visible=False)
    )

def show_real_life_application(grade):
    start_time = time.time()
    concept = AI_CONCEPTS[ai_state["index"]]
    _, application = get_explanation_and_application(concept, grade)
    logger.debug(f"show_real_life_application took {time.time() - start_time:.3f} seconds")
    return (
        gr.update(value=application, visible=True),
        gr.update(visible=True),
        gr.update(value="", visible=False),
        gr.update(visible=False)
    )

def exit_ai_mode(grade, subject):
    start_time = time.time()
    logger.debug(f"Exiting AI mode, grade: {grade}, subject: {subject}")
    ai_state["index"] = 0
    ai_state["active"] = False
    global_state["question"] = ""
    global_state["conversation_history"] = []
    global_state["topic_cache"] = {}
    global_state["fun_fact_cache"] = {}
    reset_outputs = (
        "",
        "",
        gr.update(value="", interactive=False, placeholder="🎯 Please select your grade and subject first to enable the Ask Now! button.", visible=True),
        None,
        gr.update(value="🎈 Show Me a Fun Fact!", visible=False),
        gr.update(interactive=False),
        "<div style='font-size: 5em; text-align: center;'>🤖</div>",
        gr.update(value="Select Grade"),
        gr.update(value=None),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),
        gr.update(label="💡 Fun Fact or Real-Life Example", value="", visible=False),
        gr.update(value="", visible=False),
        gr.update(visible=False)
    )
    input_state = update_input_state("Select Grade", None)
    logger.debug(f"exit_ai_mode took {time.time() - start_time:.3f} seconds")
    return reset_outputs + input_state

def on_subject_change(subject, grade):
    start_time = time.time()
    logger.debug(f"Subject changed to {subject}, Grade: {grade}")
    ai_state["index"] = 0
    ai_state["active"] = False
    if subject == "Learn AI":
        return start_ai_mode(grade)
    else:
        placeholder = "❓ Ask your question here (in English or Roman Urdu), then press Enter!"
        interactive = grade and grade != "Select Grade" and subject and subject != "Learn AI"
        logger.debug(f"on_subject_change took {time.time() - start_time:.3f} seconds")
        return (
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(value="", visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value="", interactive=interactive, placeholder=placeholder, visible=True),
            gr.update(interactive=interactive),
            gr.update(visible=True),
            gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )

def on_grade_change(grade, subject):
    start_time = time.time()
    logger.debug(f"Grade changed to {grade}, Subject: {subject}")
    if subject == "Learn AI":
        return start_ai_mode(grade)
    else:
        placeholder = "❓ Ask your question here (in English or Roman Urdu), then press Enter!"
        interactive = grade and grade != "Select Grade" and subject and subject != "Learn AI"
        logger.debug(f"on_grade_change took {time.time() - start_time:.3f} seconds")
        return (
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(value="", visible=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(value="", interactive=interactive, placeholder=placeholder, visible=True),
            gr.update(interactive=interactive),
            gr.update(visible=True),
            gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )

# Normal Q&A Chatbot Logic
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
        logger.debug(f"is_roman_urdu took {time.time() - start_time:.3f} seconds")
        return False
    text = text.lower()
    count = sum(word in text for word in urdu_indicators)
    logger.debug(f"is_roman_urdu took {time.time() - start_time:.3f} seconds")
    return count >= 2

def clean_latex(text):
    start_time = time.time()
    text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
    text = re.sub(r'\\\[(.*?)\\\]', r'\1', text)
    text = re.sub(r'\${1,2}(.*?)\${1,2}', r'\1', text)
    text = text.replace("\\", "")
    logger.debug(f"clean_latex took {time.time() - start_time:.3f} seconds")
    return text

def validate_inputs(grade, subject, question):
    start_time = time.time()
    if not grade or grade == "Select Grade":
        return "🎯 Please select a grade first!"
    if not subject or subject == "Learn AI":
        return "🎯 Please select your subject!"
    if not question or len(question.strip()) < 3:
        return "❗ Please enter a question with at least 3 characters!"
    logger.debug(f"validate_inputs took {time.time() - start_time:.3f} seconds")
    return ""

def generate_fun_fact(subject, grade, question, language):
    start_time = time.time()
    if question in global_state["fun_fact_cache"]:
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
            max_tokens=100
        )
        fact = clean_latex(response.choices[0].message.content.strip())
        global_state["fun_fact_cache"][question] = fact
        return fact
    except Exception as e:
        logger.error(f"Error generating fun fact: {e}")
        return "Oops! Couldn't fetch a fun fact right now. Please try again later."
    finally:
        logger.debug(f"generate_fun_fact took {time.time() - start_time:.3f} seconds")

def extract_topic(answer, question):
    start_time = time.time()
    if question in global_state["topic_cache"]:
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
        return topic
    except Exception as e:
        logger.error(f"Error extracting topic: {e}")
        return None
    finally:
        logger.debug(f"extract_topic took {time.time() - start_time:.3f} seconds")

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
    result = f"<div style='{style}' role='img' aria-label='Chatbot avatar'>🤖{'💭' if thinking else ''}</div>"
    logger.debug(f"avatar_update took {time.time() - start_time:.3f} seconds")
    return result

def chatbot_response(grade, subject, question):
    start_time = time.time()
    validation_error = validate_inputs(grade, subject, question)
    if validation_error:
        return validation_error, gr.update(value="🎈 Show Me a Fun Fact!", visible=False), avatar_update(False), gr.update(value="", visible=False), gr.update(visible=False)
    global_state.update({"grade": grade, "subject": subject, "question": question})
    global_state["conversation_history"] = []
    history = global_state.get("conversation_history", [])
    history.append({"role": "user", "content": question})
    global_state["conversation_history"] = history
    subject_lower = subject.lower()
    language = "urdu" if is_roman_urdu(question) else "english"
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
            max_tokens=100
        )
        answer = clean_latex(response.choices[0].message.content.strip())
    except Exception as e:
        logger.error(f"Error generating chatbot response: {e}")
        answer = f"Oops! An error occurred: {str(e)}. Please try again later."
    global_state["conversation_history"].append({"role": "assistant", "content": answer})
    encouragement = random.choice(encouragement_phrases)
    topic = extract_topic(answer, question)
    fun_fact_label = f"🎈 Show Me a Fun Fact About {topic}" if topic else "🎈 Show Me a Fun Fact!"
    logger.debug(f"chatbot_response took {time.time() - start_time:.3f} seconds")
    return (
        answer + "\n\n✨ " + encouragement,
        gr.update(value=fun_fact_label, visible=True),
        avatar_update(False),
        gr.update(value="", visible=False),
        gr.update(visible=True)
    )

def show_fun_fact(subject):
    start_time = time.time()
    question = global_state.get("question", "")
    if not question:
        logger.warning("No question provided for fun fact")
        return (
            "Please ask a question first to get a fun fact!",
            gr.update(visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=True)
        )
    if question in global_state["fun_fact_cache"]:
        return (
            global_state["fun_fact_cache"][question],
            gr.update(visible=True),
            gr.update(value="", visible=False),
            gr.update(visible=True)
        )
    lang = "urdu" if is_roman_urdu(question) else "english"
    fact = generate_fun_fact(global_state["subject"], global_state["grade"], question, lang)
    logger.debug(f"show_fun_fact took {time.time() - start_time:.3f} seconds")
    return (
        fact,
        gr.update(visible=True),
        gr.update(value="", visible=False),
        gr.update(visible=True)
    )

def use_transcription(audio):
    start_time = time.time()
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio) as source:
            audio_data = recognizer.record(source)
            result = recognizer.recognize_google(audio_data)
            return result
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return "Sorry, I couldn't understand. Please try again or type your question."
    finally:
        logger.debug(f"use_transcription took {time.time() - start_time:.3f} seconds")

def update_input_state(grade, subject):
    start_time = time.time()
    grade_valid = grade and grade != "Select Grade" and grade.isdigit() and 3 <= int(grade) <= 6
    subject_valid = bool(subject) and subject != "Learn AI"
    is_ai_mode = subject == "Learn AI"
    logger.debug(f"update_input_state: grade_valid={grade_valid}, subject_valid={subject_valid}, is_ai_mode={is_ai_mode}")
    if grade_valid and subject_valid and not is_ai_mode:
        result = (
            gr.update(interactive=True, placeholder="❓ Ask your question here (in English or Roman Urdu), then press Enter!", visible=True),
            gr.update(interactive=True),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False),
            gr.update(visible=False)
        )
    elif grade_valid and is_ai_mode:
        result = (
            gr.update(interactive=False, placeholder="🤖 You're in AI Learning Mode! Use the buttons on the right to explore AI concepts.", visible=True),
            gr.update(interactive=False),
            gr.update(visible=False),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=True),
            gr.update(visible=False)
        )
    else:
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
    logger.debug(f"update_input_state took {time.time() - start_time:.3f} seconds")
    return result

def clear_all(grade, subject):
    start_time = time.time()
    logger.debug(f"Clearing all, grade: {grade}, subject: {subject}")
    ai_state["index"] = 0
    ai_state["active"] = False
    global_state["question"] = ""
    global_state["conversation_history"] = []
    global_state["topic_cache"] = {}
    global_state["fun_fact_cache"] = {}
    reset_outputs = (
        "",
        "",
        gr.update(value="", interactive=False, placeholder="🎯 Please select your grade and subject first to enable the Ask Now! button.", visible=True),
        None,
        gr.update(value="🎈 Show Me a Fun Fact!", visible=False),
        gr.update(interactive=False),
        "<div style='font-size: 5em; text-align: center;'>🤖</div>",
        gr.update(value="Select Grade"),
        gr.update(value=None),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!", visible=True),
        gr.update(label="💡 Fun Fact or Real-Life Example", value="", visible=False),
        gr.update(value="", visible=False),
        gr.update(visible=False)
    )
    input_state = update_input_state("Select Grade", None)
    logger.debug(f"clear_all took {time.time() - start_time:.3f} seconds")
    return reset_outputs + input_state

def tts_output(text):
    start_time = time.time()
    if not text.strip():
        return None
    try:
        tts = gTTS(text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        logger.error(f"Error in tts_output: {e}")
        return None
    finally:
        logger.debug(f"tts_output took {time.time() - start_time:.3f} seconds")

def show_speaker(text):
    start_time = time.time()
    result = gr.update(visible=bool(text.strip()))
    logger.debug(f"show_speaker took {time.time() - start_time:.3f} seconds")
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
    background: #e7f5ff !important;
    font-size: 1.5em !important;
    text-align: center !important;
    color: #007bff !important;
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
                elem_id="subject_radio",
                value=None
            )
            question_input = gr.Textbox(
                label="❓ Ask Your Question (in English or Roman Urdu)",
                lines=1,
                elem_id="question_input",
                placeholder="🎯 Please select your grade and subject first to enable the Ask Now! button.",
                interactive=False,
                show_label=True,
                submit_btn=None,
                value=""
            )
            mic_instructions = gr.Markdown(
                value="### 🗣️ Prefer speaking? Tap the mic below and ask your question out loud!",
                visible=True,
                elem_id="mic_instructions"
            )
            audio_input = gr.Audio(
                sources=["microphone"],
                type="filepath",
                label="🎤 Speak Your Question",
                elem_id="audio_input",
                visible=True
            )
            with gr.Row():
                ask_btn = gr.Button(
                    "✅ Ask Now!",
                    variant="primary",
                    elem_id="ask_btn",
                    visible=True,
                    interactive=False
                )
                clear_btn = gr.Button(
                    "🧼 Clear",
                    variant="secondary",
                    elem_id="clear_btn"
                )
        with gr.Column(elem_classes="output-panel"):
            ai_header = gr.Markdown("", visible=False, elem_id="ai_header")
            ai_progress = gr.Markdown("", visible=False, elem_id="ai_progress")
            avatar = gr.Markdown(
                "<div class='avatar' role='img' aria-label='Chatbot Avatar'>🤖</div>",
                elem_id="avatar",
                visible=True
            )
            response_output = gr.Textbox(
                label="My Classmate AI Says:",
                visible=True,
                lines=5,
                elem_id="response_output",
                placeholder=None,
                interactive=False
            )
            with gr.Row():
                gr.Markdown("", visible=False)
                speak_btn = gr.Button("🔊 Listen", elem_id="speak_btn", visible=False, size="sm")
            audio_out = gr.Audio(
                label="Audio Output",
                elem_id="audio_out",
                interactive=False,
                visible=False
            )
            fun_fact_btn = gr.Button(
                "🎈 Show Me a Fun Fact!",
                elem_id="fun_fact_btn",
                visible=False,
                variant="primary"
            )
            real_life_app_btn = gr.Button(
                "💡 Real-Life Application",
                elem_id="real_life_app_btn",
                visible=False,
                variant="secondary"
            )
            fun_fact_output = gr.Textbox(
                label="💡 Fun Fact or Real-Life Example",
                lines=3,
                elem_id="fun_fact_output",
                interactive=False,
                visible=False
            )
            with gr.Row():
                speak_funfact_btn = gr.Button("🔊 Listen", elem_id="speak_funfact_btn", visible=False, size="sm")
            audio_funfact_out = gr.Audio(
                label="Fun Fact Audio",
                elem_id="audio_funfact_out",
                interactive=False,
                visible=False
            )
            with gr.Row():
                next_concept_btn = gr.Button("Next Concept", variant="primary", visible=False, elem_id="next_concept_btn")
                btn_ai_exit = gr.Button("Exit AI Mode", variant="secondary", visible=False, elem_id="exit_ai_btn")
            next_instruction = gr.Markdown("", visible=False, elem_classes="next-instruction")
            with gr.Row():
                clear_output_btn = gr.Button(
                    "🧼 Start New Question!",
                    variant="primary",
                    visible=False,
                    elem_id="clear_output_btn"
                )

    gr.Markdown(
        """<div class='footer-note' role='contentinfo'>
        <strong>Made with ❤️ by <a href='https://astramentors.com' target='_blank'>Astra Mentors</a> | Contact: <a href='mailto:ceo@astramentors.com'>ceo@astramentors.com</a></strong>
        <br>
        <em>We respect your privacy. No student data is stored or shared.</em>
        </div>"""
    )

    grade.change(
        fn=on_grade_change,
        inputs=[grade, subject],
        outputs=[
            ai_header, ai_progress, response_output, real_life_app_btn, next_concept_btn,
            btn_ai_exit, fun_fact_btn, question_input, ask_btn, audio_input,
            mic_instructions, next_instruction, speak_btn, audio_out, clear_output_btn
        ]
    ).then(
        fn=update_input_state,
        inputs=[grade, subject],
        outputs=[question_input, ask_btn, fun_fact_btn, real_life_app_btn, next_concept_btn, btn_ai_exit, clear_output_btn]
    )
    subject.change(
        fn=on_subject_change,
        inputs=[subject, grade],
        outputs=[
            ai_header, ai_progress, response_output, real_life_app_btn, next_concept_btn,
            btn_ai_exit, fun_fact_btn, question_input, ask_btn, audio_input,
            mic_instructions, next_instruction, speak_btn, audio_out, clear_output_btn
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
            ai_progress, response_output, fun_fact_output, real_life_app_btn, next_concept_btn,
            btn_ai_exit, speak_btn, speak_funfact_btn, next_instruction, audio_out, clear_output_btn
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
            response_output, fun_fact_output, question_input, audio_input, fun_fact_btn,
            ask_btn, avatar, grade, subject, speak_btn, audio_out, speak_funfact_btn,
            audio_funfact_out, real_life_app_btn, next_concept_btn, btn_ai_exit,
            ai_header, ai_progress, mic_instructions, fun_fact_output, next_instruction,
            clear_output_btn
        ]
    )
    real_life_app_btn.click(
        fn=show_real_life_application,
        inputs=grade,
        outputs=[fun_fact_output, speak_funfact_btn, next_instruction, clear_output_btn]
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
        outputs=[fun_fact_output, speak_funfact_btn, next_instruction, clear_output_btn]
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
            response_output, fun_fact_output, question_input, audio_input, fun_fact_btn,
            ask_btn, avatar, grade, subject, speak_btn, audio_out, speak_funfact_btn,
            audio_funfact_out, real_life_app_btn, next_concept_btn, btn_ai_exit,
            ai_header, ai_progress, mic_instructions, fun_fact_output, next_instruction,
            clear_output_btn
        ]
    )
    clear_output_btn.click(
        fn=clear_all,
        inputs=[grade, subject],
        outputs=[
            response_output, fun_fact_output, question_input, audio_input, fun_fact_btn,
            ask_btn, avatar, grade, subject, speak_btn, audio_out, speak_funfact_btn,
            audio_funfact_out, real_life_app_btn, next_concept_btn, btn_ai_exit,
            ai_header, ai_progress, mic_instructions, fun_fact_output, next_instruction,
            clear_output_btn
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

if __name__ == "__main__":
    start_time = time.time()
    demo.launch(share=False)
    logger.info(f"App launch took {time.time() - start_time:.3f} seconds")
