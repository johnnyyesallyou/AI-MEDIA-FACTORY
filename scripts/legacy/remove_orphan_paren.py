import pathlib, py_compile

f = pathlib.Path('./core/models/content_orm.py')
lines = f.read_text(encoding='utf-8').split('\n')

# Ищем одинокую ')' — строка где только ')' с отступом, 
# и предыдущая непустая строка уже заканчивается на ')'
# Это означает что скобка "сирота"
new_lines = []
for i, line in enumerate(lines):
    stripped = line.strip()
    
    # Если строка — только закрывающая скобка с отступом
    if stripped == ')' and i > 0:
        # Ищем предыдущую непустую строку
        prev_idx = len(new_lines) - 1
        while prev_idx >= 0 and not new_lines[prev_idx].strip():
            prev_idx -= 1
        
        if prev_idx >= 0:
            prev_line = new_lines[prev_idx]
            prev_stripped = prev_line.strip()
            
            # Если предыдущая непустая строка заканчивается на ')'
            # и НЕ является определением Column (т.е. это закрытие многострочного блока)
            # То текущая ')' — сирота
            if prev_stripped == ')' and 'Column(' not in lines[i-3] if i >= 3 else True:
                # Проверяем что это реально "лишняя" скобка — она между двумя блоками
                # (предыдущая строка - это конец draft_text, а дальше идут новые поля)
                # Смотрим следующую непустую строку
                next_idx = i + 1
                while next_idx < len(lines) and not lines[next_idx].strip():
                    next_idx += 1
                
                if next_idx < len(lines):
                    next_line = lines[next_idx].strip()
                    # Если дальше идёт asset_id или image_url — это точно сирота
                    if next_line.startswith('asset_id =') or next_line.startswith('image_url =') or next_line.startswith('image_prompt ='):
                        print(f'  ❌ Удаляю сиротскую скобку на строке {i+1}: "{line}"')
                        continue
    
    new_lines.append(line)

f.write_text('\n'.join(new_lines), encoding='utf-8')
print(f'\\n✅ Файл переписан ({len(new_lines)} строк)')

# Показываем финальный результат
print('\\n=== Финальный результат (строки 50-65) ===')
for i, line in enumerate(new_lines[49:65], start=50):
    print(f'{i}: {line}')

try:
    py_compile.compile(str(f), doraise=True)
    print('\\n✅✅✅ content_orm.py валиден! ✅✅✅')
except py_compile.PyCompileError as e:
    print(f'\\n❌ Ошибка: {e}')