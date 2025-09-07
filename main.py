import os
import requests
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
RUNWAY_KEY = os.getenv("RUNWAY_API_KEY")

def generate_from_runway(prompt: str, mode: str = "image"):
    url = "https://api.runwayml.com/v1/query"
    headers = {"Authorization": f"Bearer {RUNWAY_KEY}"}
    data = {"input": prompt, "model": "stable-diffusion-v1-5" if mode == "image" else "gen-2"}

    # ������ ������
    r = requests.post(url, headers=headers, json=data)
    response = r.json()
    print("Create job response:", response)

    job_id = response.get("id")
    if not job_id:
        return {"error": "�� ������� ������� ������", "details": response}

    # ��� ���������� ������
    status = response.get("status")
    while status != "succeeded":
        time.sleep(3)
        check = requests.get(f"{url}/{job_id}", headers=headers)
        status = check.json().get("status")
        print("Status:", status)
        if status == "failed":
            return {"error": "��������� �� �������", "details": check.json()}

    output = check.json().get("output")
    return {"output": output}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "������! ?\n"
        "������ /img �������� ��� �������� ???\n"
        "��� /vid �������� ��� ����� ??"
    )

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("������ �������� ����� �������!")
        return

    message = await update.message.reply_text("? ��������� �����������...")

    try:
        result = generate_from_runway(prompt, "image")
        if "output" in result and result["output"]:
            image_url = result["output"][0]
            await message.delete()
            await update.message.reply_photo(photo=image_url)
        else:
            await message.edit_text("? ������ ���������: ��������� ������ ��� ������ API.")
    except Exception as e:
        await message.edit_text(f"? ������ ���������: {e}")

async def generate_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("������ �������� ����� �������!")
        return

    message = await update.message.reply_text("? ��������� ����� (����� ������ �� 1�2 �����)...")

    try:
        result = generate_from_runway(prompt, "video")
        if "output" in result and result["output"]:
            video_url = result["output"][0]
            await message.delete()
            await update.message.reply_video(video=video_url)
        else:
            await message.edit_text("? ������ ���������: ��������� ������ ��� ������ API.")
    except Exception as e:
        await message.edit_text(f"? ������ ���������: {e}")

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("img", generate_image))
app.add_handler(CommandHandler("vid", generate_video))

if __name__ == "__main__":
    app.run_polling()
