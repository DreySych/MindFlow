//Если не нравятся комментарии - удалите (относится к Андрею, Макару)


//Проверка на существование контента
document.addEventListener('DOMContentLoaded', function() {
    // Получаем айди поля ввода и списка друзей
    const searchInput = document.getElementById('friendSearchInput');
    const friendsList = document.getElementById('friendsList');

    // Проверяем что элементы существуют на странице (чисто страховка от поломки js)
    if (searchInput && friendsList) {
        // Смотрим на ввод текста в поле поиска
        searchInput.addEventListener('input', function() {
            // Убираем пробелы и делаем буквы мелкими (А->а) у поиска
            const searchTerm = this.value.toLowerCase().trim();

            // Получаем список всех друзей
            const friendItems = friendsList.querySelectorAll('.friend-item');

            // Перебираем каждого друга
            friendItems.forEach(function(item) {
                // Находим ник друга внутри списка
                const nickElement = item.querySelector('.friend-nick');

                if (nickElement) {
                    // делаем буквы мелкими (А->а) у ника
                    const nick = nickElement.textContent.toLowerCase();

                    // Содержание ника в поисковой строке (не тупо ==)
                    if (nick.includes(searchTerm)) {
                        item.style.display = 'flex';
                    } else {
                        item.style.display = 'none';
                    }
                }
            });
        });
    }
});