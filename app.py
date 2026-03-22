from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes
import random

import os
TOKEN = os.getenv("TOKEN")

TOKEN = "8680065940:AAFCqNfMUrYL0NEoeUHWPHSx0kc4qITlAx4"

game = {
    "players": 0,
    "spies": 1,
    "word": "",
    "roles": [],
    "turn": 0,
    "category": ""
}

# Կատեգորիաներ
categories = {
    "prof": ["բժիշկ", "ծրագրավորող", "ուսուցիչ", "ոստիկան", "վարորդ"],
    "place": ["դպրոց", "հիվանդանոց", "օդանավակայան", "ռեստորան", "պարկ"],
    "famous": ["Մեսսի", "Ռոնալդու", "Էյնշտեյն", "Շեքսպիր"],
    "animal": ["շուն", "կատու", "առյուծ", "փիղ"],
    "action": ["վազել", "կարդալ", "խաղալ", "քնել"],
    "feeling": ["ուրախ", "տխուր", "զայրացած", "վախեցած"]
}

# MENUS
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 Սկսել խաղը", callback_data="start")]
    ])

def category_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Մասնագիտություններ", callback_data="c_prof")],
        [InlineKeyboardButton("Տեղամասեր", callback_data="c_place")],
        [InlineKeyboardButton("Հայտնի մարդիկ", callback_data="c_famous")],
        [InlineKeyboardButton("Կենդանիներ", callback_data="c_animal")],
        [InlineKeyboardButton("Գործողություն", callback_data="c_action")],
        [InlineKeyboardButton("Զգացմունք", callback_data="c_feeling")]
    ])

def players_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("3", callback_data="p3"),
         InlineKeyboardButton("4", callback_data="p4"),
         InlineKeyboardButton("5", callback_data="p5")],
        [InlineKeyboardButton("6", callback_data="p6"),
         InlineKeyboardButton("7", callback_data="p7")]
    ])

def spies_menu(players):
    buttons = []
    row = []

    for i in range(1, players):  # չպետք է հավասար լինի players-ին
        row.append(InlineKeyboardButton(f"{i} լրտես", callback_data=f"s{i}"))
        if len(row) == 2:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    return InlineKeyboardMarkup(buttons)

def view_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👁 Տեսնել", callback_data="view")],
        [InlineKeyboardButton("❌ Փակել", callback_data="close")]
    ])

def restart_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Նորից խաղալ", callback_data="restart")]
    ])

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Սեղմիր 👇", reply_markup=main_menu())

# BUTTON HANDLER
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # START
    if data == "start":
        await query.edit_message_text("Ընտրիր կատեգորիա 👇", reply_markup=category_menu())

    # CATEGORY
    elif data.startswith("c_"):
        game["category"] = data.split("_")[1]
        await query.edit_message_text("Քանի խաղացող 👇", reply_markup=players_menu())

    # PLAYERS
    elif data.startswith("p"):
        game["players"] = int(data[1:])
        await query.edit_message_text(
            "Քանի լրտես 👇",
            reply_markup=spies_menu(game["players"])
        )

    # SPIES
    elif data.startswith("s"):
        spies = int(data[1:])

        if spies >= game["players"]:
            await query.answer("❌ Չի կարող լինել այդքան լրտես", show_alert=True)
            return

        game["spies"] = spies

        words = categories[game["category"]]
        game["word"] = random.choice(words)

        roles = ["Spy"] * spies + ["Word"] * (game["players"] - spies)
        random.shuffle(roles)

        game["roles"] = roles
        game["turn"] = 0

        await query.edit_message_text(
            "Խաղը սկսվեց 🎮\nԽաղացող 1 👇",
            reply_markup=view_buttons()
        )

    # VIEW
    elif data == "view":
        role = game["roles"][game["turn"]]

        text = "🤫 Դու լրտես ես" if role == "Spy" else f"🎯 Քո բառը՝ {game['word']}"

        try:
            await query.edit_message_text(text, reply_markup=view_buttons())
        except:
            pass

    # CLOSE
    elif data == "close":
        game["turn"] += 1

        if game["turn"] < game["players"]:
            await query.edit_message_text(
                f"Հաջորդ խաղացող՝ {game['turn'] + 1}",
                reply_markup=view_buttons()
            )
        else:
            await query.edit_message_text(
                "Բոլորը տեսան 👌\nԽաղը սկսվեց 🕵️‍♂️",
                reply_markup=restart_button()
            )

    # RESTART
    elif data == "restart":
        await query.edit_message_text("Նոր խաղ 👇", reply_markup=main_menu())

# APP
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

app.run_polling()