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

# Buraya kendi VIP kanal linklerini ekleyebilirsin (Mavi tıklanabilir olacaklar)
VIP_LINKLERI = [
    "https://t.me/+ornekKanalLink1",
    "https://t.me/+ornekKanalLink2",
    "https://t.me/+ornekKanalLink3",
    "https://t.me/+ornekKanalLink4",
    "https://t.me/+ornekKanalLink5",
]

# Admin Telegram ID'nizi buraya yazın (Dekontlar bu ID'ye onay için gidecek)
# Kendi ID'nizi öğrenmek için @userinfobot kullanabilirsiniz.
ADMIN_ID = 123456789  # <--- BURAYI KENDİ TELEGRAM ID'NİZ İLE DEĞİŞTİRİN!

logging.basicConfig(level=logging.INFO)
router = Router()


class PaymentState(StatesGroup):
  waiting_for_receipt = State()


# Başlangıç ve Ödeme Bilgileri Menüsü
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
  text = (
      "🔥 **Özel VIP Kanalları Paketine Hoş Geldiniz!** 🔥\n\n"
      "Toplam **5 adet özel VIP kanalımızın** tamamına anında erişim sağlamak için aşağıdaki ödeme bilgilerine yatırım yapmanız gerekmektedir.\n\n"
      f"💰 **Tutar:** `{TUTAR}`\n"
      f"🏦 **IBAN:** `{IBAN}`\n"
      f"👤 **Alıcı Adı Soyadı:** `{ALICI}`\n\n"
      "⚠️ **Dikkat:** Açıklama kısmına kullanıcı adınızı yazmayı unutmayın!\n\n"
      "Ödemeyi yaptıktan sonra lütfen **Dekont Gönder** butonuna basarak dekont fotoğrafınızı veya ekran görüntüsünü bota iletin."
  )

  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="📤 Dekont Gönder", callback_data="send_receipt")]
      ]
  )
  await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "send_receipt")
async def ask_receipt(callback: CallbackQuery, state: FSMContext):
  await callback.message.answer(
      "Lütfen yaptığınız ödemeye ait **dekont fotoğrafını** veya ekran görüntüsünü buraya gönderin:"
  )
  await state.set_state(PaymentState.waiting_for_receipt)
  await callback.answer()


# Müşteri dekontu gönderdiğinde
@router.message(PaymentState.waiting_for_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext):
  photo = message.photo[-1].file_id
  user = message.from_user
  user_name = f"@{user.username}" if user.username else user.full_name
  user_id = user.id

  await message.answer(
      "✅ **Dekontunuz başarıyla alındı!**\nYönetici onayından sonra VIP linkleriniz otomatik olarak buraya gönderilecektir. Lütfen bekleyin."
  )
  await state.clear()

  # Admin'e onay bildirimi gönder
  admin_text = (
      "🔔 **Yeni Ödeme Bildirimi!**\n\n"
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
    # Mavi tıklanabilir linkleri hazırla (Markdown formatında)
    links_text = (
        "🎉 **Ödemeniz Onaylandı! VIP Kanallarına Hoş Geldiniz!** 🎉\n\n"
        "Aşağıdaki mavi bağlantılara tıklayarak özel kanallarımıza hemen katılabilirsiniz:\n\n"
    )

    for i, link in enumerate(VIP_LINKLERI, 1):
      links_text += f"🔗 [VIP Kanal {i için tıkla]({link})}\n"

    links_text += (
        "\n⚠️ Lütfen bu linkleri başkalarıyla paylaşmayın, aksi takdirde"
        " erişiminiz kalıcı olarak engellenir."
    )

    try:
      await callback.bot.send_message(
          chat_id=target_user_id, text=links_text, parse_mode="Markdown"
      )
      await callback.message.edit_caption(
          caption=callback.message.caption
          + "\n\n✅ **DURUM: ONAYLANDI ve Linkler Gönderildi**",
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
          text=(
              "❌ **Ödemeniz Onaylanmadı.**\nDekontunuz geçersiz veya tutar"
              " eşleşmiyor. Lütfen destek ile iletişime geçin."
          ),
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
