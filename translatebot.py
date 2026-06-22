import os
import re
import asyncio
import time # 追加: 再接続時の待機に使用します
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import ollama

# チャットごとの翻訳モードを保持する辞書
# 構造: { chat_id: "ja2en" | "ja2tw" | "ja2kr" }
chat_modes = {}

MODEL_NAME = "translategemma:12b"

def is_japanese(text: str) -> bool:
    """
    文字列に日本語特有の文字（ひらがな・カタカナ）が含まれているか判定。
    """
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text))

async def start_ja2en(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    chat_modes[chat_id] = "ja2en"
    await update.message.reply_text("🔄 **日本語 ⇄ 英語 の相互翻訳モードを有効にしました。**")

async def start_ja2tw(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    chat_modes[chat_id] = "ja2tw"
    await update.message.reply_text("🔄 **日本語 ⇄ 台湾華語（繁体字） の相互翻訳モードを有効にしました。**")

async def start_ja2kr(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ja2kr コマンドで日本語 ⇄ 韓国語の相互翻訳を開始"""
    chat_id = update.effective_chat.id
    chat_modes[chat_id] = "ja2kr"
    await update.message.reply_text("🔄 **日本語 ⇄ 韓国語（ハングル） の相互翻訳モードを有効にしました。**")

async def stop_translation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id in chat_modes:
        del chat_modes[chat_id]
        await update.message.reply_text("⏹️ **翻訳モードを終了しました。**")
    else:
        await update.message.reply_text("現在翻訳モードは設定されていません。")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    
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
            tgt_lang, tgt_code = "Traditional Chinese", "zh-TW"
        else:
            src_lang, src_code = "Traditional Chinese", "zh-TW"
            tgt_lang, tgt_code = "Japanese", "ja"
            
    elif mode == "ja2kr":
        if is_japanese(text):
            src_lang, src_code = "Japanese", "ja"
            tgt_lang, tgt_code = "Korean", "ko" # 韓国語を指定
        else:
            src_lang, src_code = "Korean", "ko"
            tgt_lang, tgt_code = "Japanese", "ja"

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
    # ⚠️ トークンは必ず再発行し、ここに直接書かずに環境変数などから取得するようにしてください
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("エラー: TELEGRAM_BOT_TOKEN を設定してください。")
        return

    # 無限ループでポーリングを囲むことで、通信エラーで落ちても自動で再起動する
    while True:
        try:
            # ループの中で毎回Applicationをビルドし直すことで、安全に再接続できます
            application = Application.builder().token(TOKEN).build()

            application.add_handler(CommandHandler("ja2en", start_ja2en))
            application.add_handler(CommandHandler("ja2tw", start_ja2tw))
            application.add_handler(CommandHandler("ja2kr", start_ja2kr))
            application.add_handler(CommandHandler("stop", stop_translation))
            
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

            print("Bot is running...")
            # ポーリングを開始。ネットワークエラー等の致命的エラーが起きるとここから例外が飛ぶ
            application.run_polling()
            
        except Exception as e:
            # エラーをキャッチして10秒待機後、whileループの先頭に戻って再接続
            print(f"通信エラーまたは予期せぬエラーで停止しました。10秒後に再接続します: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
