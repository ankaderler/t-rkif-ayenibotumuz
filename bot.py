import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

# Bot token ve yapılandırma bilgileri
TOKEN = "8972897472:AAE3qTglBRqA7nNzB7QeoyGq4IBV0DukjoE"
IBAN = "TR06 0001 0021 5470 2002 4550 04"
ALICI = "Zeynep Alkoç"
TUTAR = "400 TL"
CANLI_DESTEK = "@kralicenizeynep"

# Müşteriye teslim edilecek gerçek VIP kanal linkleri
VIP_LINKLERI = [
    "https://t.me/+Aqi4UqSzr4JjZmRk",
    "https://t.me/+H2z-xlyZ6zM0OTE0",
    "https://t.me/+p01bQp6XebkzMmI0",
    "https://t.me/+HqtuwLtoMkkwMWQ0",
    "https://t.me/+BcHhS86B9ocyMWQ0",
]

# Admin Telegram ID'niz (Dekontlar bu ID'ye onay için gelecek)
ADMIN_ID = 123456789  # <--- BURAYI KENDİ TELEGRAM ID'NİZ İLE DEĞİŞTİRİN!

logging.basicConfig(level=logging.INFO)
router = Router()


class PaymentState(StatesGroup):
  waiting_for_receipt = State()


# Başlangıç ve VIP Menü
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
  text = (
      "🔥 **TÜRK VIP KANALLARINA HOŞ GELDİNİZ** 🔥\n\n"
      "Tamamen özel, gizli ve seçkin içeriklerin yer aldığı **5'li VIP Paketimize** anında erişim sağlayın.\n\n"
      "💎 **Paket İçeriği:** 5 Adet Özel VIP Kanalın Tümü\n"
      f"💰 **Toplam Tutar:** `{TUTAR}`\n\n"
      "📋 **Nasıl Satın Alınır?**\n"
      "1️⃣ Aşağıdaki **IBAN'a 400 TL** transfer yapın.\n"
      "2️⃣ Açıklama kısmına sadece kendi kullanıcı adınızı yazın.\n"
      "3️⃣ **'📤 Dekont Gönder'** butonuna basarak dekont fotoğrafınızı bota iletin.\n"
      "4️⃣ Yönetici onayından sonra 5 adet mavi tıklanabilir VIP linkiniz anında gelsin!\n\n"
      f"🏦 **IBAN:** `{IBAN}`\n"
      f"👤 **Alıcı:** `{ALICI}`"
  )

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="📤 Dekont Gönder & Satın Al", callback_data="send_receipt")],
          [InlineKeyboardButton(text="💬 Canlı Destek / İletişim", url=f"https://t.me/{CANLI_DESTEK.lstrip('@')}")]
      ]
  )
  await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "send_receipt")
async def ask_receipt(callback: CallbackQuery, state: FSMContext):
  text = (
      "📸 **Lütfen Dekont Gönderin**\n\n"
      f"Lütfen **{TUTAR}** tutarındaki ödemeyi yukarıdaki IBAN'a yaptıktan sonra dekontunuzun ekran görüntüsünü veya fotoğrafını doğrudan bu sohbete gönderin."
  )
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="🔙 Ana Menüye Dön", callback_data="back_home")]
      ]
  )
  await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
  await state.set_state(PaymentState.waiting_for_receipt)
  await callback.answer()


@router.callback_query(F.data == "back_home")
async def back_home(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  text = (
      "🔥 **TÜRK VIP KANALLARINA HOŞ GELDİNİZ** 🔥\n\n"
      f"💰 **Toplam Tutar:** `{TUTAR}`\n"
      f"🏦 **IBAN:** `{IBAN}`\n"
      f"👤 **Alıcı:** `{ALICI}`"
  )
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="📤 Dekont Gönder & Satın Al", callback_data="send_receipt")],
          [InlineKeyboardButton(text="💬 Canlı Destek / İletişim", url=f"https://t.me/{CANLI_DESTEK.lstrip('@')}")]
      ]
  )
  await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
  await callback.answer()


# Müşteri dekontu gönderdiğinde
@router.message(PaymentState.waiting_for_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext):
  photo = message.photo[-1].file_id
  user = message.from_user
  user_name = f"@{user.username}" if user.username else user.full_name
  user_id = user.id

  await message.answer(
      "✅ **Dekontunuz Başarıyla Alındı!**\n\nDekontunuz incelemeye alındı. Yönetici onay verdiğinde VIP kanal linkleriniz otomatik olarak buraya gelecektir. Lütfen bekleyin."
  )
  await state.clear()

  # Admin'e onay bildirimi gönder
  admin_text = (
      "🔔 **Yeni VIP Ödeme Bildirimi!**\n\n"
      f"👤 **Müşteri:** {user_name} (ID: `{user_id}`)\n"
      f"💵 **Tutar:** {TUTAR}\n\n"
      "Lütfen dekontu kontrol edip onaylayın:"
  )

  admin_keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [
              InlineKeyboardButton(
                  text="✅ Onayla ve Linkleri Gönder",
                  callback_data=f"approve_{user_id}",
              )
          ],
          [
              InlineKeyboardButton(
                  text="❌ Reddet", callback_data=f"reject_{user_id}"
              )
          ],
      ]
  )

  try:
    await message.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=photo,
        caption=admin_text,
        reply_markup=admin_keyboard,
        parse_mode="Markdown",
    )
  except Exception as e:
    logging.error(f"Admin'e bildirim gönderilemedi: {e}")


# Admin onay veya ret verdiğinde
@router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def handle_admin_action(callback: CallbackQuery):
  data_parts = callback.data.split("_")
  action = data_parts[0]
  target_user_id = int(data_parts[1])

  if action == "approve":
    # Mavi tıklanabilir linkleri hazırla
    links_text = (
        "🎉 **Ödemeniz Onaylandı! VIP Kanallarına Hoş Geldiniz!** 🎉\n\n"
        "Aşağıdaki özel mavi bağlantılara tıklayarak VIP kanallarımıza hemen katılabilirsiniz:\n\n"
    )

    for i, link in enumerate(VIP_LINKLERI, 1):
      links_text += f"🔗 [VIP Kanal {i} - Tıkla Katıl]({link})\n"

    links_text += (
        "\n⚠️ **Not:** Bu linkler kişiye özeldir, başkalarıyla paylaşılması durumunda erişiminiz kalıcı olarak engellenir."
    )

    try:
      await callback.bot.send_message(
          chat_id=target_user_id, text=links_text, parse_mode="Markdown"
      )
      await callback.message.edit_caption(
          caption=callback.message.caption + "\n\n✅ **DURUM: ONAYLANDI ve Linkler Müşteriye İletildi**",
          reply_markup=None,
      )
      await callback.answer("Onaylandı ve müşteriye iletildi.")
    except Exception as e:
      await callback.answer(
          f"Kullanıcıya mesaj gönderilemedi (Botu engellemiş olabilir): {e}",
          show_alert=True,
      )

  elif action == "reject":
    try:
      await callback.bot.send_message(
          chat_id=target_user_id,
          text="❌ **Ödemeniz Onaylanmadı.**\nDekontunuzda tutar eşleşmiyor veya geçersiz. Destek için: " + CANLI_DESTEK,
      )
      await callback.message.edit_caption(
          caption=callback.message.caption + "\n\n❌ **DURUM: REDDEDİLDİ**",
          reply_markup=None,
      )
      await callback.answer("Ödeme reddedildi.")
    except Exception as e:
      await callback.answer(f"Hata: {e}", show_alert=True)


async def main():
  bot = Bot(token=TOKEN)
  dp = Dispatcher()
  dp.include_router(router)
  await bot.delete_webhook(drop_pending_updates=True)
  await dp.start_polling(bot)


if __name__ == "__main__":
  asyncio.run(main())
