#!/bin/bash

echo "🚀 Настройка Git репозитория для Nexa Messenger"
echo "=================================================="

# Проверяем, есть ли уже Git репозиторий
if [ -d ".git" ]; then
    echo "✅ Git репозиторий уже инициализирован"
else
    echo "📁 Инициализация Git репозитория..."
    git init
    echo "✅ Git репозиторий создан"
fi

# Добавляем все файлы
echo "📝 Добавление файлов в Git..."
git add .

# Проверяем статус
echo "📊 Статус Git репозитория:"
git status

echo ""
echo "🔧 Следующие шаги:"
echo "1. Сделайте первый коммит:"
echo "   git commit -m 'Initial commit: Nexa Messenger'"
echo ""
echo "2. Добавьте удаленный репозиторий (замените на ваш):"
echo "   git remote add origin https://github.com/yourusername/nexa-messenger.git"
echo ""
echo "3. Отправьте на GitHub:"
echo "   git push -u origin main"
echo ""
echo "4. Перейдите на render.com и создайте новый веб-сервис"
echo "5. Подключите ваш GitHub репозиторий"
echo ""
echo "📖 Подробные инструкции в файле RENDER_DEPLOYMENT_README.md"
echo ""
echo "🎯 Удачи с деплоем на Render!"
