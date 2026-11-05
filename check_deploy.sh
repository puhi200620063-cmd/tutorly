#!/bin/bash
# Автоматический скрипт проверки готовности к деплою

echo "🔍 Проверка проекта Tutorly перед деплоем..."
echo ""

# Проверка структуры проекта
echo "✓ Проверка файлов..."
files=("backend/Dockerfile" "frontend/Dockerfile" "render.yaml" "backend/requirements.txt" "frontend/package.json" "backend/app/main.py")
missing=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ ОТСУТСТВУЕТ: $file"
        missing=$((missing + 1))
    fi
done

echo ""

if [ $missing -eq 0 ]; then
    echo "✅ Все файлы на месте!"
else
    echo "❌ Отсутствует $missing файлов"
    exit 1
fi

echo ""
echo "📋 Следующие шаги:"
echo ""
echo "1. Создайте базу данных на https://neon.tech"
echo "   → Скопируйте Connection String (Pooled)"
echo ""
echo "2. Загрузите код на GitHub (если ещё не загружен):"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git remote add origin https://github.com/USERNAME/tutorly.git"
echo "   git push -u origin main"
echo ""
echo "3. Деплой на Render: https://render.com"
echo "   → New → Blueprint → Подключите репозиторий tutorly"
echo "   → Добавьте переменные:"
echo "     tutorly-api: DATABASE_URL = [строка из Neon]"
echo "     tutorly-web: VITE_API_URL = https://tutorly-api.onrender.com"
echo "   → Apply"
echo ""
echo "4. Дождитесь деплоя (3-5 минут) и откройте сайт!"
echo ""
echo "📖 Подробная инструкция: DEPLOY_GUIDE.md"
echo ""
echo "✨ Готово к деплою!"
