const formidable = require('formidable');
const fs = require('fs');

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).send('Method Not Allowed');
  }

  const form = new formidable.IncomingForm({ multiples: false });

  form.parse(req, async (err, fields, files) => {
    if (err) {
      console.error('Error parsing form:', err);
      return res.status(500).send('<div class="alert alert-danger">Внутренняя ошибка обработки формы.</div>');
    }

    const getField = (val) => Array.isArray(val) ? val[0] : val;

    const name = (getField(fields.name) || "").toString().trim();
    const tel = (getField(fields.tel) || getField(fields.phone) || "").toString().trim();
    const email = (getField(fields.email) || "").toString().trim();
    const subject = getField(fields.subject) || "Не указано";
    const date = getField(fields.date);
    const time = getField(fields.time);
    const message = getField(fields.message) || "";
    
    const uploadedFile = Array.isArray(files.file) ? files.file[0] : files.file;

    // Validation
    if (!name) {
      return res.status(200).send('<div class="alert alert-danger">Пожалуйста, укажите ваше имя.</div>');
    }
    if (!/^[a-zA-Zа-яА-ЯёЁ\s\-']+$/.test(name)) {
      return res.status(200).send('<div class="alert alert-danger">Имя может содержать только буквы.</div>');
    }
    if (!tel) {
      return res.status(200).send('<div class="alert alert-danger">Пожалуйста, укажите ваш номер телефона.</div>');
    }

    let text = `<b>🔔 Новая заявка с сайта Best Electronics!</b>\n\n`;
    text += `<b>👤 Имя:</b> ${name}\n`;
    if (tel) text += `<b>📞 Телефон:</b> ${tel}\n`;
    if (email) text += `<b>✉️ Email:</b> ${email}\n`;
    if (subject && subject !== "Не указано") text += `<b>📋 Предмет:</b> ${subject}\n`;
    if (date) text += `<b>📅 Дата:</b> ${date}\n`;
    if (time) text += `<b>🕒 Время:</b> ${time}\n`;
    if (message) text += `<b>💬 Сообщение:</b>\n${message}\n`;

    const botToken = process.env.TELEGRAM_BOT_TOKEN;
    const chatId = process.env.TELEGRAM_CHAT_ID;

    if (!botToken || !chatId) {
      console.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID");
      return res.status(200).send('<div class="alert alert-danger">Ошибка сервера: не настроены ключи Telegram.</div>');
    }

    try {
      const tgUrl = `https://api.telegram.org/bot${botToken}/sendMessage`;
      const response = await fetch(tgUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text: text,
          parse_mode: "HTML"
        })
      });

      if (response.ok && uploadedFile && uploadedFile.size > 0) {
        const fileBuffer = fs.readFileSync(uploadedFile.filepath);
        const fileBlob = new Blob([fileBuffer]);
        
        const tgFormData = new FormData();
        tgFormData.append("chat_id", chatId);
        tgFormData.append("document", fileBlob, uploadedFile.originalFilename);

        const fileTgUrl = `https://api.telegram.org/bot${botToken}/sendDocument`;
        const fileResponse = await fetch(fileTgUrl, {
          method: "POST",
          body: tgFormData
        });

        if (!fileResponse.ok) {
          console.error("Telegram File Error:", await fileResponse.text());
        }
      }

      if (response.ok) {
        return res.status(200).send('<div class="alert alert-success">Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.</div>');
      } else {
        console.error("Telegram API Error:", await response.text());
        return res.status(200).send('<div class="alert alert-danger">Не удалось отправить заявку в Telegram.</div>');
      }
    } catch (e) {
      console.error("Network Error:", e);
      return res.status(200).send('<div class="alert alert-danger">Внутренняя ошибка сервера.</div>');
    }
  });
};

module.exports.config = {
  api: {
    bodyParser: false,
  },
};
