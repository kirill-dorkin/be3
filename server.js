const PORT = process.env.PORT || 3000;

Bun.serve({
  port: PORT,
  async fetch(req) {
    const url = new URL(req.url);

    // 1. Handle API endpoint for form submissions
    if (url.pathname === "/api/send-message" && req.method === "POST") {
      try {
        const contentType = req.headers.get("content-type") || "";
        let formData;
        
        if (contentType.includes("form-data") || contentType.includes("urlencoded")) {
          formData = await req.formData();
        } else {
          return new Response('<div class="alert alert-danger">Некорректный формат запроса.</div>', {
            headers: { "Content-Type": "text/html; charset=utf-8" }
          });
        }

        const name = (formData.get("name") || "").toString().trim();
        const tel = (formData.get("tel") || formData.get("phone") || "").toString().trim();
        const email = (formData.get("email") || "").toString().trim();
        const subject = formData.get("subject") || "Не указано";
        const date = formData.get("date");
        const time = formData.get("time");
        const message = formData.get("message") || "";
        const file = formData.get("file");

        // Backend Validation
        if (!name) {
          return new Response('<div class="alert alert-danger">Пожалуйста, укажите ваше имя.</div>', {
            headers: { "Content-Type": "text/html; charset=utf-8" }
          });
        }
        if (!/^[a-zA-Zа-яА-ЯёЁ\s\-']+$/.test(name)) {
          return new Response('<div class="alert alert-danger">Имя может содержать только буквы.</div>', {
            headers: { "Content-Type": "text/html; charset=utf-8" }
          });
        }
        if (!tel) {
          return new Response('<div class="alert alert-danger">Пожалуйста, укажите ваш номер телефона.</div>', {
            headers: { "Content-Type": "text/html; charset=utf-8" }
          });
        }

        // Format message for Telegram with HTML tags
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
          console.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment.");
          return new Response('<div class="alert alert-danger">Ошибка сервера: не настроены ключи Telegram.</div>', {
            headers: { "Content-Type": "text/html; charset=utf-8" }
          });
        }

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

        // Handle file upload if present and text message was successful
        if (response.ok && file && typeof file !== 'string' && file.size > 0) {
          const fileData = new FormData();
          fileData.append("chat_id", chatId);
          fileData.append("document", file);
          
          const fileTgUrl = `https://api.telegram.org/bot${botToken}/sendDocument`;
          const fileResponse = await fetch(fileTgUrl, {
            method: "POST",
            body: fileData
          });
          
          if (!fileResponse.ok) {
            console.error("Telegram API Error (File Upload):", await fileResponse.text());
          }
        }

        if (response.ok) {
          return new Response('<div class="alert alert-success">Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.</div>', {
            headers: { "Content-Type": "text/html; charset=utf-8" }
          });
        } else {
          const errText = await response.text();
          console.error("Telegram API Error:", errText);
          return new Response('<div class="alert alert-danger">Не удалось отправить заявку в Telegram.</div>', {
            headers: { "Content-Type": "text/html; charset=utf-8" }
          });
        }
      } catch (e) {
        console.error("Error processing form:", e);
        return new Response('<div class="alert alert-danger">Внутренняя ошибка сервера.</div>', {
          headers: { "Content-Type": "text/html; charset=utf-8" }
        });
      }
    }

    // 2. Serve static files from root directory
    let decodedPath = decodeURIComponent(url.pathname);
    let pathWithoutQuery = decodedPath.includes('?') ? decodedPath.split('?')[0] : decodedPath;

    let filepathWithQuery = "." + decodedPath;
    let filepathWithoutQuery = "." + pathWithoutQuery;

    try {
      // Try exact match first (handles files literally named with ? on disk)
      const fileWithQuery = Bun.file(filepathWithQuery);
      if (await fileWithQuery.exists()) {
        return new Response(fileWithQuery);
      }

      // Try without query string
      const fileWithoutQuery = Bun.file(filepathWithoutQuery);
      if (await fileWithoutQuery.exists()) {
        return new Response(fileWithoutQuery);
      }

      // Try index.html for directories
      if (pathWithoutQuery === "/" || pathWithoutQuery.endsWith("/")) {
        const fileIndex = Bun.file(filepathWithoutQuery + "index.html");
        if (await fileIndex.exists()) {
          return new Response(fileIndex);
        }
      }
    } catch (err) {
      // Ignore file check errors
    }

    // Serve custom 404.html page if file not found
    try {
      const file404 = Bun.file("./404.html");
      if (await file404.exists()) {
        return new Response(file404, { status: 404 });
      }
    } catch (err) {}

    return new Response("Page Not Found", { status: 404 });
  }
});

console.log(`\n🚀 Server running at http://localhost:${PORT}`);
console.log("Press Ctrl+C to stop the server.");
