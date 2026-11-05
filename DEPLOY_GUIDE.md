# 🚀 Инструкция по деплою Tutorly

## Что нужно сделать (5 минут)

### Шаг 1: Создать базу данных (2 минуты)

1. Перейдите на [neon.tech](https://neon.tech)
2. Нажмите **Sign Up** → войдите через GitHub
3. Нажмите **Create Project**
4. Название: `tutorly` (или любое)
5. После создания найдите **Connection String** → выберите **Pooled connection**
6. **СКОПИРУЙТЕ** строку (начинается с `postgresql://...`)
   - Пример: `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require`
7. **СОХРАНИТЕ** её — понадобится на шаге 3

### Шаг 2: Подготовить GitHub (1 минута)

**Если репозиторий УЖЕ на GitHub — пропустите этот шаг.**

Если нет:
1. Создайте репозиторий на [github.com/new](https://github.com/new)
2. Название: `tutorly` (публичный или приватный)
3. В папке проекта выполните:
```bash
cd "C:\Users\PUHI\Desktop\Яшина 2\tut\Tutorly"
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/ВАШ_USERNAME/tutorly.git
git push -u origin main
```

### Шаг 3: Деплой на Render (2 минуты)

1. Перейдите на [render.com](https://render.com)
2. Нажмите **Sign Up** → войдите через GitHub
3. На главной странице нажмите **New +** → выберите **Blueprint**
4. Нажмите **Connect** рядом с репозиторием `tutorly`
5. Render найдёт файл `render.yaml` и покажет 2 сервиса
6. Нажмите **Add env variable** для сервиса **tutorly-api**:
   - Ключ: `DATABASE_URL`
   - Значение: **ВСТАВЬТЕ** строку из Neon (шаг 1)
7. Нажмите **Add env variable** для сервиса **tutorly-web**:
   - Ключ: `VITE_API_URL`
   - Значение: `https://tutorly-api.onrender.com` (если Render назначит другой URL, вернитесь и исправьте)
8. Нажмите **Apply** внизу страницы
9. Дождитесь деплоя (3-5 минут)

### Шаг 4: Открыть сайт

1. После завершения деплоя перейдите в **tutorly-web**
2. Скопируйте URL (типа `https://tutorly-web.onrender.com`)
3. **ОТКРОЙТЕ В БРАУЗЕРЕ** — ваш сайт работает! 🎉

---

## Важно

- **Бесплатный план Render** засыпает после 15 минут неактивности. Первый запуск после сна занимает ~30 сек
- **Neon Free** имеет лимит 0.5 ГБ данных и 100 часов вычислений в месяц
- Если нужно изменить `VITE_API_URL` после деплоя:
  1. Зайдите в Render Dashboard → **tutorly-web** → **Environment**
  2. Измените `VITE_API_URL`
  3. Нажмите **Manual Deploy** → **Deploy latest commit**

---

## Если что-то пошло не так

### Backend не запускается
- Проверьте, что `DATABASE_URL` в Render совпадает со строкой из Neon
- Убедитесь, что строка начинается с `postgresql://` (не `postgres://`)

### Frontend не подключается к API
- Проверьте, что `VITE_API_URL` указывает на правильный URL API
- URL должен быть `https://tutorly-api.onrender.com` (без `/` в конце)
- Если API имеет другой URL, обновите переменную и пересоберите frontend

### База данных не работает
- Neon Free засыпает после периода неактивности
- Первое обращение разбудит базу (займёт несколько секунд)

---

## Что дальше?

После успешного деплоя:
1. Зарегистрируйте аккаунт репетитора на сайте
2. Добавьте учеников, задания, занятия
3. Проверьте все функции
4. При необходимости подключите свой домен (см. документацию Render)

**Готово!** Ваш сайт в интернете 🌐
