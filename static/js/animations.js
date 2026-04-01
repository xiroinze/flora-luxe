// ================== THEME SWITCHER ==================
(function() {
  // Создаем переключатель тем
  const switcher = document.createElement('div');
  switcher.className = 'theme-switcher';
  switcher.innerHTML = `
    <button class="theme-btn rose" data-theme="rose" title="Ethereal Rose"></button>
    <button class="theme-btn emerald" data-theme="emerald" title="Emerald Royale"></button>
  `;
  document.body.appendChild(switcher);
  
  // Получаем сохраненную тему или используем rose по умолчанию
  const savedTheme = localStorage.getItem('flora_luxe_theme') || 'rose';
  
  // Применяем тему
  function applyTheme(theme) {
    // Удаляем существующие классы тем
    document.body.classList.remove('theme-rose', 'theme-emerald');
    // Добавляем новую тему
    document.body.classList.add(`theme-${theme}`);
    
    // Обновляем активную кнопку
    document.querySelectorAll('.theme-btn').forEach(btn => {
      if (btn.dataset.theme === theme) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
    
    // Сохраняем тему
    localStorage.setItem('flora_luxe_theme', theme);
  }
  
  // Добавляем обработчики для кнопок
  document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const theme = btn.dataset.theme;
      applyTheme(theme);
      
      // Небольшая анимация для плавного перехода
      document.body.style.transition = 'background 0.4s ease';
      setTimeout(() => {
        document.body.style.transition = '';
      }, 400);
    });
  });
  
  // Применяем сохраненную тему
  applyTheme(savedTheme);
})();