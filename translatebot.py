import os
import re
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import ollama

# チャット（グループ/チャンネル）ごとの翻訳モードを保持する辞書
# 構造: { chat_id: "ja2en" または "ja2tw" }
chat_modes = {}

# Ollamaで実行するTranslateGemmaのモデル名
MODEL_NAME =  "translategemma:12b"

def is_japanese(text: str) -> bool:
    """
    文字列に日本語特有の文字（ひらがな・カタカナ）が含まれているか判定。
    ※台湾華語の漢字（繁体字）と区別するため、漢字のみでの判定は除外しています。
    """
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text))

async def start_ja2en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ja2en コマンドで日本語 ⇄ 英語の相互翻訳を開始"""
    chat_id = update.effective_chat.id
    chat_modes[chat_id] = "ja2en"
    await update.message.reply_text("🔄 **日本語 ⇄ 英語 の相互翻訳モードを有効にしました。**\nこれ以降のテキストを自動で翻訳します。")

async def start_ja2tw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ja2tw コマンドで日本語 ⇄ 台湾華語の相互翻訳を開始"""
    chat_id = update.effective_chat.id
    chat_modes[chat_id] = "ja2tw"
    await update.message.reply_text("🔄 **日本語 ⇄ 台湾華語（繁体字） の相互翻訳モードを有効にしました。**\nこれ以降のテキストを自動で翻訳します。")

async def stop_translation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/stop コマンドで翻訳を停止"""
    chat_id = update.effective_chat.id
    if chat_id in chat_modes:
        del chat_modes[chat_id]
        await update.message.reply_text("⏹️ **翻訳モードを終了しました。**")
    else:
        await update.message.reply_text("現在翻訳モードは設定されていません。")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """メッセージ受信時のハンドラー"""
    chat_id = update.effective_chat.id
    
    # メッセージが空、または翻訳モードが設定されていないチャットの場合はスルー
    if not update.message or not update.message.text:
        return
    if chat_id not in chat_modes:
        return

    text = update.message.text
    mode = chat_modes[chat_id]

    # モードと言語判定に基づくソース言語・ターゲット言語の設定
    if mode == "ja2en":
        if is_japanese(text):
            src_lang, src_code = "Japanese", "ja"
            tgt_lang, tgt_code = "English", "en"
        else:
            src_lang, src_code = "English", "en"
            tgt_lang, tgt_code = "Japanese", "ja"
            
    elif mode == "ja2tw":
        if is_japanese(text):
            src_lang, src_code = "Japanese", "ja"
            tgt_lang, tgt_code = "Traditional Chinese", "zh-TW" # 台湾華語を指定
        else:
            src_lang, src_code = "Traditional Chinese", "zh-TW"
            tgt_lang, tgt_code = "Japanese", "ja"

    # TranslateGemma用のプロンプト構築
    prompt = (
        f"You are a professional {src_lang} ({src_code}) to {tgt_lang} ({tgt_code}) translator. "
        f"Your goal is to accurately convey the meaning and nuances of the original {src_lang} text "
        f"while adhering to {tgt_lang} grammar, vocabulary, and cultural sensitivities. "
        f"Produce only the {tgt_lang} translation, without any additional explanations or commentary. "
        f"Please translate the following {src_lang} text into {tgt_lang}: {text}"
    )

    try:
        response = await asyncio.to_thread(
            ollama.generate,
            model=MODEL_NAME,
            prompt=prompt,
            options={"temperature": 0.0}
        )
        
        translated_text = response.get('response', '').strip()
        
        if translated_text:
            await update.message.reply_text(
                translated_text, 
                reply_to_message_id=update.message.message_id
            )
    except Exception as e:
        print(f"Error during Ollama generation: {e}")

def main() -> None:
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
    
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("エラー: TELEGRAM_BOT_TOKEN を設定してください。")
        return

    application = Application.builder().token(TOKEN).build()

    # コマンドハンドラーの登録
    application.add_handler(CommandHandler("ja2en", start_ja2en))
    application.add_handler(CommandHandler("ja2tw", start_ja2tw)) # 台湾語コマンドを追加
    application.add_handler(CommandHandler("stop", stop_translation))
    
    # メッセージハンドラーの登録
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
