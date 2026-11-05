# 🚂 Инструкция по деплою Tutorly на Railway

## ✅ Что уже готово:
- Railway CLI установлен
- Авторизация завершена (puhi200620063@gmail.com)
- Проект создан: `Tutorly`
- Код на GitHub: https://github.com/puhi200620063-cmd/tutorly

## 🌐 Деплой через веб-интерфейс Railway

CLI столкнулся с временной ошибкой "Failed to snapshot repository". Продолжим через браузер:

### Шаг 1: Откройте Railway Dashboard

Перейдите на: **[railway.app/dashboard](https://railway.app/dashboard)**

Вы увидите проект **"Tutorly"** в списке.

---

### Шаг 2: Настройте GitHub Deploy

1. Откройте проект **Tutorly**
2. Кликните на сервис **"Tutorly"**
3. Перейдите в **Settings** → **Source**
4. Нажмите **"Connect Repo"**
5. Выберите репозиторий **puhi200620063-cmd/tutorly**
6. В поле **Root Directory** введите: `backend`
7. Нажмите **"Save"**

---

### Шаг 3: Добавьте переменные окружения

В том же сервисе:

1. Перейдите на вкладку **"Variables"**
2. Нажмите **"New Variable"** и добавьте:

```
DATABASE_URL=postgresql://neondb_owner:npg_hk3mA2VopdNM@ep-late-bonus-b9g7zwdm-pooler.c-7.eu-central-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require

SECRET_KEY=railway-production-secret-key-12345

CORS_ORIGINS=*

PORT=8000
```

3. Нажмите **"Add"** для каждой переменной

---

### Шаг 4: Разверните сервис

1. Railway автоматически начнёт деплой после сохранения переменных
2. Или нажмите **"Deploy"** вручную
3. Дождитесь завершения (3-5 минут)

---

### Шаг 5: Создайте публичный URL

1. В настройках сервиса найдите **Settings** → **Networking**
2. Нажмите **"Generate Domain"**
3. Railway создаст URL типа: `tutorly-production.up.railway.app`
4. **Скопируйте этот URL** — он понадобится для frontend

---

### Шаг 6: Разверните Frontend на Vercel

Frontend нужно развернуть отдельно:

1. Зайдите на **[vercel.com](https://vercel.com)** → Login через GitHub
2. Нажмите **"Add New..."** → **"Project"**
3. Выберите репозиторий **tutorly**
4. В настройках:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Добавьте переменную окружения:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://tutorly-production.up.railway.app` (ваш Railway URL)
6. Нажмите **"Deploy"**

---

### Шаг 7: Откройте ваш сайт

После завершения деплоя на Vercel:

1. Vercel покажет URL типа: `tutorly.vercel.app`
2. **Откройте этот URL** — ваш сайт работает! 🎉

---

## 🎯 Итоговая архитектура

- **Backend (API)**: Railway — `tutorly-production.up.railway.app`
- **Frontend**: Vercel — `tutorly.vercel.app`
- **База данных**: Neon PostgreSQL (Frankfurt)

---

## ❓ Если возникнут проблемы

**Backend не запускается:**
- Проверьте логи в Railway Dashboard → Deployments → View Logs
- Убедитесь, что Root Directory = `backend`

**Frontend не подключается к API:**
- Проверьте VITE_API_URL в Vercel
- Убедитесь, что Railway сгенерировал публичный домен

**База данных не работает:**
- Проверьте DATABASE_URL (должен начинаться с `postgresql://`)
- Neon Free tier может засыпать — первое обращение разбудит

---

Дайте знать, когда дойдёте до Railway Dashboard!
