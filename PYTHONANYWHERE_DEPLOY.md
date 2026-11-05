# Инструкция по деплою на PythonAnywhere + GitHub Pages

## 🎯 План развертывания

- **Backend API**: PythonAnywhere (бесплатно, без карты)
- **Frontend**: GitHub Pages (бесплатно)
- **База данных**: Neon PostgreSQL (уже готова)

---

## Часть 1: Backend на PythonAnywhere

### Шаг 1: Зарегистрируйтесь на PythonAnywhere

1. Откройте **[pythonanywhere.com](https://www.pythonanywhere.com)**
2. Нажмите **"Start running Python online in less than a minute!"**
3. Нажмите **"Create a Beginner account"** (бесплатный план)
4. Заполните форму:
   - Username: `puhi200620063` (или любой)
   - Email: ваш email
   - Password: придумайте пароль
5. Подтвердите email

---

### Шаг 2: Загрузите код на PythonAnywhere

После входа:

1. Перейдите в **"Consoles"** → **"Bash"**
2. В консоли выполните:

```bash
git clone https://github.com/puhi200620063-cmd/tutorly.git
cd tutorly/backend
```

---

### Шаг 3: Создайте Web App

1. Перейдите на вкладку **"Web"**
2. Нажмите **"Add a new web app"**
3. Выберите домен: `puhi200620063.pythonanywhere.com` (или ваш username)
4. Выберите **"Manual configuration"**
5. Python version: **Python 3.10**
6. Нажмите **"Next"**

---

### Шаг 4: Настройте WSGI файл

1. В разделе **"Code"** найдите ссылку на WSGI configuration file
2. Нажмите на неё (откроется редактор)
3. Удалите всё содержимое
4. Вставьте:

```python
import sys
import os

# Добавьте путь к вашему проекту
path = '/home/puhi200620063/tutorly/backend'
if path not in sys.path:
    sys.path.append(path)

# Установите переменные окружения
os.environ['DATABASE_URL'] = 'postgresql://neondb_owner:npg_hk3mA2VopdNM@ep-late-bonus-b9g7zwdm-pooler.c-7.eu-central-1.aws.neon.tech/neondb?channel_binding=require&sslmode=require'
os.environ['SECRET_KEY'] = 'pythonanywhere-secret-key-12345'
os.environ['CORS_ORIGINS'] = '*'

from app.main import app as application
```

5. Нажмите **"Save"** (вверху справа)

---

### Шаг 5: Установите зависимости

Вернитесь в **Bash консоль** и выполните:

```bash
cd ~/tutorly/backend
pip3.10 install --user -r requirements.txt
```

Это займёт 2-3 минуты.

---

### Шаг 6: Запустите Web App

1. Вернитесь на вкладку **"Web"**
2. Нажмите большую зелёную кнопку **"Reload puhi200620063.pythonanywhere.com"**
3. Подождите ~10 секунд
4. Проверьте: откройте `https://puhi200620063.pythonanywhere.com/health`
   - Должно показать: `{"status":"ok","product":"Tutorly","version":"2.0.0"}`

✅ **Backend готов!** URL: `https://puhi200620063.pythonanywhere.com`

---

## Часть 2: Frontend на GitHub Pages

Эту часть я выполню автоматически через команды.

---

## Часть 3: Проверка работы

После развертывания обеих частей:

1. Откройте URL frontend на GitHub Pages
2. Зарегистрируйтесь как репетитор
3. Создайте ученика, задание, занятие
4. Проверьте все функции

---

## ❓ Если что-то не работает

**Backend не запускается:**
- Проверьте логи: Web → Error log
- Убедитесь, что все зависимости установлены

**Frontend не подключается:**
- Проверьте VITE_API_URL в конфиге

**База данных не работает:**
- Проверьте DATABASE_URL в WSGI файле

---

**Готово!** Следуйте инструкции по PythonAnywhere, а я подготовлю frontend.
