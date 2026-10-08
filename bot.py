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

# Teslim edilecek VIP kanal linkleri
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


def get_main_menu():
  return InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="💎 VIP Üyelik Satın Al (400 TL)", callback_data="buy_vip")],
          [InlineKeyboardButton(text="📖 Nasıl Satın Alınır?", callback_data="how_to_buy")],
          [InlineKeyboardButton(text="⭐ VIP Özellikler", callback_data="vip_features")],
          [InlineKeyboardButton(text="💬 7/24 Canlı Destek", url=f"https://t.me/{CANLI_DESTEK.lstrip('@')}")]
      ]
  )


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
  await state.clear()
  text = (
      "🔥 **ELİT VIP ARŞİV — MERKEZİNE HOŞ GELDİNİZ** 🔥\n\n"
      "Tamamen gizli ve özel içeriklerin paylaşıldığı VIP arşiv sistemimize anında adım atın.\n\n"
      "👇 Aşağıdaki menüden işlemlerini yönetebilirsin:"
  )
  await message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")


@router.callback_query(F.data == "back_home")
async def back_home(callback: CallbackQuery, state: FSMContext):
  await state.clear()
  text = (
      "🔥 **ELİT VIP ARŞİV — MERKEZİNE HOŞ GELDİNİZ** 🔥\n\n"
      "Tamamen gizli ve özel içeriklerin paylaşıldığı VIP arşiv sistemimize anında adım atın.\n\n"
      "👇 Aşağıdaki menüden işlemlerini yönetebilirsin:"
  )
  try:
    await callback.message.edit_text(text, reply_markup=get_main_menu(), parse_mode="Markdown")
  except Exception:
    await callback.message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")
  await callback.answer()


@router.callback_query(F.data == "how_to_buy")
async def how_to_buy(callback: CallbackQuery):
  text = (
      "📖 **VIP Üyelik Nasıl Satın Alınır?**\n\n"
      "1️⃣ **'VIP Üyelik Satın Al'** butonuna basarak güncel IBAN ve ödeme bilgilerine ulaş.\n"
      "2️⃣ Belirtilen tutarı ilgili IBAN hesabına Havale / FAST ile gönder.\n"
      "3️⃣ Ödeme sonrasında dekontun ekran görüntüsünü veya PDF dosyasını doğrudan bu sohbet penceresine gönder.\n"
      "4️⃣ Sistem dekontu onayladığı an özel VIP davet linkleriniz saniyeler içinde otomatik olarak gelecektir!"
  )
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="🔙 Ana Menüye Dön", callback_data="back_home")]
      ]
  )
  await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
  await callback.answer()


@router.callback_query(F.data == "vip_features")
async def vip_features(callback: CallbackQuery):
  text = (
      "⭐ **VIP Arşiv Özellikleri**\n\n"
      "• 🚀 Sınırsız ve kesintisiz ömür boyu erişim\n"
      "• 🎬 5 Adet Seçkin VIP Kanalın Tamamı\n"
      "• 🔄 Sürekli güncellenen taze içerikler\n"
      "• 🔒 Güvenli ve hızlı otomatik teslimat altyapısı"
  )
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="🔙 Ana Menüye Dön", callback_data="back_home")]
      ]
  )
  await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
  await callback.answer()


@router.callback_query(F.data == "buy_vip")
async def buy_vip(callback: CallbackQuery, state: FSMContext):
  text = (
      "💎 **ELİT VIP — GÜVENLİ ÖDEME ARAYÜZÜ**\n\n"
      "📦 **Paket:** Sınırsız Premium VIP Erişimi\n"
      f"💵 **Tutar:** `{TUTAR}`\n\n"
      "🏦 **Resmi Havale / FAST Bilgileri**\n"
      f"• **IBAN:** `{IBAN}`\n"
      f"• **Alıcı Adı:** `{ALICI}`\n\n"
      "━━━━━━━━━━━━━━━━━━━\n"
      "1️⃣ Yukarıdaki IBAN hesabına tam **400 TL** gönderin.\n"
      "2️⃣ İşlem sonrasında **Dekontu / Ekran Görüntüsünü (veya PDF)** doğrudan bu sohbet penceresine gönderin.\n"
      "3️⃣ Sistem dekontu onayladığı an özel VIP davet linkleriniz saniyeler içinde otomatik gelecektir! 🚀"
  )
  keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="🔙 Ana Menüye Dön", callback_data="back_home")]
      ]
  )
  await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
  await state.set_state(PaymentState.waiting_for_receipt)
  await callback.answer()


@router.message(PaymentState.waiting_for_receipt, F.photo | F.document)
async def receive_receipt(message: Message, state: FSMContext):
  user = message.from_user
  user_name = f"@{user.username}" if user.username else user.full_name
  user_id = user.id

  await message.answer(
      "✅ **Dekontunuz başarıyla alındı!**\n\nYönetici kontrolü sağlanıyor. Onay verildiğinde VIP linkleriniz anında buraya gönderilecektir.",
      reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Ana Menüye Dön", callback_data="back_home")]]))
  await state.clear()

  admin_text = (
      "🔔 **YENİ ÖDEME BİLDİRİMİ!**\n\n"
      f"👤 **Müşteri:** {user_name} (ID: `{user_id}`)\n"
      f"💵 **Tutar:** {TUTAR}\n\n"
      "Lütfen dekontu inceleyip onaylayın:"
  )

  admin_keyboard = InlineKeyboardMarkup(
      inline_keyboard=[
          [InlineKeyboardButton(text="✅ Onayla ve Linkleri Gönder", callback_data=f"approve_{user_id}")],
          [InlineKeyboardButton(text="❌ Reddet", callback_data=f"reject_{user_id}")]
      ]
  )

  try:
    if message.photo:
      file_id = message.photo[-1].file_id
      await message.bot.send_photo(chat_id=ADMIN_ID, photo=file_id, caption=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
    elif message.document:
      file_id = message.document.file_id
      await message.bot.send_document(chat_id=ADMIN_ID, document=file_id, caption=admin_text, reply_markup=admin_keyboard, parse_mode="Markdown")
  except Exception as e:
    logging.error(f"Admin'e bildirim iletilemedi: {e}")


@router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def handle_admin_action(callback: CallbackQuery):
  data_parts = callback.data.split("_")
  action = data_parts[0]
  target_user_id = int(data_parts[1])

  if action == "approve":
    links_text = (
        "✅ **DEKONT ONAYLANDI! ÖDEME ALINDI.** ✅\n\n"
        "Tebrikler! Özel davet linkleriniz aşağıdadır:\n\n"
    )

    for i, link in enumerate(VIP_LINKLERI, 1):
      links_text += f"🔗 [VIP Kanal {i} - Katılmak İçin Tıkla]({link})\n"

    links_text += "\n⚠️ **Bu linkler kişiye özeldir, paylaşılması yasaktır.**"

    try:
      await callback.bot.send_message(
          chat_id=target_user_id, 
          text=links_text, 
          parse_mode="Markdown",
          reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Ana Menüye Dön", callback_data="back_home")]]))
      
      if callback.message.caption:
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n✅ **DURUM: ONAYLANDI ve Linkler Gönderildi**",
            reply_markup=None,
        )
      elif callback.message.text:
        await callback.message.edit_text(
            text=callback.message.text + "\n\n✅ **DURUM: ONAYLANDI ve Linkler Gönderildi**",
            reply_markup=None,
        )
      await callback.answer("Onaylandı ve müşteriye iletildi.")
    except Exception as e:
      await callback.answer(f"Hata oluştu: {e}", show_alert=True)

  elif action == "reject":
    try:
      await callback.bot.send_message(
          chat_id=target_user_id,
          text="❌ **Ödemeniz Onaylanmadı.**\nDekont geçersiz veya tutar uyuşmuyor. Destek için: " + CANLI_DESTEK,
      )
      if callback.message.caption:
        await callback.message.edit_caption(
            caption=callback.message.caption + "\n\n❌ **DURUM: REDDEDİLDİ**",
            reply_markup=None,
        )
      elif callback.message.text:
        await callback.message.edit_text(
            text=callback.message.text + "\n\n❌ **DURUM: REDDEDİLDİ**",
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
