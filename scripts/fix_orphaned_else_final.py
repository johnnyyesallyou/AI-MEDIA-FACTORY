import pathlib, re
p = pathlib.Path('./backend/automation/runner.py')
s = p.read_text(encoding='utf-8')

print("=== Анализ проблемы ===")
lines = s.split('\n')

# Находим проблемные строки
for i, line in enumerate(lines):
    if 'jobs = []  # Runtime уже выполнил jobs' in line:
        print(f"   Строка {i+1}: {line}")
    if i >= 144 and i <= 150:
        print(f"   {i+1}: {line}")

# Стратегия: удаляем блок от "jobs = []  # Runtime уже выполнил jobs"
# до конца else-блока (включая hardcoded jobs список),
# а вместо этого делаем правильный else с fallback
pattern = re.compile(
    r'(        jobs = \[\]  # Runtime уже выполнил jobs\s*\n)'
    r'(\s*else:\s*\n'
    r'\s*# Старый hardcoded список jobs.*?\n'
    r'\s*logger\.info\("No workflow_id provided.*?"\)\s*\n'
    r'\s*jobs = \[\s*\n.*?'
    r'\s*PublishJob\(\)\s*\n'
    r'\s*\),\s*\n'
    r'\s*\]\s*\n)',
    re.DOTALL
)

new_block = r'''\1        else:
            # Старый hardcoded список jobs (для обратной совместимости)
            logger.info("No workflow_id provided, using hardcoded job list")
            jobs = [
                ("research", ResearchJob()),
                ("decision", DecisionJob()),
                ("writing", WritingJob()),
                ("evaluation", EvaluatorJob()),
                ("revision", RevisionJob()),
                ("re_evaluation", ReEvaluationJob()),
                ("publish", PublishJob()),
            ]
'''

s_new, count = pattern.subn(new_block, s, count=1)

if count > 0:
    p.write_text(s_new, encoding='utf-8')
    print(f"\n✅ Применён {count} фикс: orphaned else исправлен")
else:
    print("\n⚠️ Regex не сработал, пробуем line-by-line фикс")
    
    # Fallback: line-by-line
    new_lines = []
    skip_until_for_loop = False
    for i, line in enumerate(lines):
        if 'jobs = []  # Runtime уже выполнил jobs' in line:
            new_lines.append(line)
            # Проверяем следующую строку - если это else, пропускаем весь else блок
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].strip().startswith('else:'):
                print(f"   Удаляем orphaned else на строке {j+1}")
                skip_until_for_loop = True
                continue
        
        if skip_until_for_loop:
            # Пропускаем до строки "for name, job in jobs:"
            if 'for name, job in jobs:' in line:
                skip_until_for_loop = False
                # Вставляем правильный else блок ПЕРЕД for
                indent = '        '
                new_lines.append(f'{indent}else:')
                new_lines.append(f'{indent}    # Старый hardcoded список jobs (для обратной совместимости)')
                new_lines.append(f'{indent}    logger.info("No workflow_id provided, using hardcoded job list")')
                new_lines.append(f'{indent}    jobs = [')
                new_lines.append(f'{indent}        ("research", ResearchJob()),')
                new_lines.append(f'{indent}        ("decision", DecisionJob()),')
                new_lines.append(f'{indent}        ("writing", WritingJob()),')
                new_lines.append(f'{indent}        ("evaluation", EvaluatorJob()),')
                new_lines.append(f'{indent}        ("revision", RevisionJob()),')
                new_lines.append(f'{indent}        ("re_evaluation", ReEvaluationJob()),')
                new_lines.append(f'{indent}        ("publish", PublishJob()),')
                new_lines.append(f'{indent}    ]')
                new_lines.append(line)  # добавляем for loop
            continue
        
        new_lines.append(line)
    
    p.write_text('\n'.join(new_lines), encoding='utf-8')
    print("✅ Применён line-by-line фикс")

# Проверка синтаксиса
import py_compile
try:
    py_compile.compile(str(p), doraise=True)
    print('✅ Синтаксис валиден!')
except py_compile.PyCompileError as e:
    print(f'❌ Синтаксическая ошибка: {e}')