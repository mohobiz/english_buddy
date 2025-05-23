import os
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from src.agent import compiled_graph, AgentState, Message, UserProfile
import openai

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# In-memory state per user (for MVP, not persistent)
user_states = {}

# Default user profile (customize as needed)
def get_user_profile(user_id):
    # For MVP, return a static profile
    return UserProfile(
        proficiency_level='A2',
        learning_goals=['Improve grammar', 'Expand vocabulary']
    )

def synthesize_text_to_ogg(text, output_path):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",  # You can change to another supported voice
        input=text
    )
    with open(output_path, "wb") as f:
        f.write(response.content)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_states[user_id] = []  # Reset message history
    await update.message.reply_text(
        "👋 Welcome to English Buddy!\nSend me a message to start practicing your English."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    messages = user_states.get(user_id, [])
    messages.append(Message(role='user', content=text))
    profile = get_user_profile(user_id)
    state = AgentState(messages=messages.copy(), user_profile=profile)
    updated_state = compiled_graph.invoke(state)
    if not isinstance(updated_state, AgentState):
        updated_state = AgentState.model_validate(updated_state)
    agent_reply = updated_state.messages[-1].content
    # Synthesize reply to voice and send as voice message
    voice_path = f"reply_{user_id}.ogg"
    synthesize_text_to_ogg(agent_reply, voice_path)
    with open(voice_path, "rb") as voice_file:
        await update.message.reply_voice(voice=voice_file)
    # Send feedback as text
    if updated_state.grammar_feedback:
        await update.message.reply_text(f"Grammar: {updated_state.grammar_feedback[-1]}")
    if updated_state.vocabulary_feedback:
        await update.message.reply_text(f"Vocabulary: {updated_state.vocabulary_feedback[-1]}")
    messages.append(Message(role='assistant', content=agent_reply))
    user_states[user_id] = messages

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = f"voice_{user_id}.ogg"
    await file.download_to_drive(file_path)
    openai.api_key = os.getenv('OPENAI_API_KEY')
    with open(file_path, "rb") as audio_file:
        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    user_text = response.text
    messages = user_states.get(user_id, [])
    messages.append(Message(role='user', content=user_text))
    profile = get_user_profile(user_id)
    state = AgentState(messages=messages.copy(), user_profile=profile)
    updated_state = compiled_graph.invoke(state)
    if not isinstance(updated_state, AgentState):
        updated_state = AgentState.model_validate(updated_state)
    agent_reply = updated_state.messages[-1].content
    await update.message.reply_text(f"(Transcribed) You said: {user_text}")
    # Synthesize reply to voice and send as voice message
    voice_path = f"reply_{user_id}.ogg"
    synthesize_text_to_ogg(agent_reply, voice_path)
    with open(voice_path, "rb") as voice_file:
        await update.message.reply_voice(voice=voice_file)
    # Send feedback as text
    if updated_state.grammar_feedback:
        await update.message.reply_text(f"Grammar: {updated_state.grammar_feedback[-1]}")
    if updated_state.vocabulary_feedback:
        await update.message.reply_text(f"Vocabulary: {updated_state.vocabulary_feedback[-1]}")
    messages.append(Message(role='assistant', content=agent_reply))
    user_states[user_id] = messages

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    print('Bot is running...')
    app.run_polling() 