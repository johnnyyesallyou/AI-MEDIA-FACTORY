import pathlib, py_compile, glob

# Ищем все Python файлы
py_files = glob.glob('./backend/**/*.py', recursive=True)

fixed_count = 0
for file_path in py_files:
    f = pathlib.Path(file_path)
    s = f.read_text(encoding='utf-8')
    
    if 'RevisionJob' in s or 'ReEvaluationJob' in s:
        print(f'\\n📄 {file_path}:')
        lines = s.split('\n')
        new_lines = []
        for line in lines:
            if 'RevisionJob' in line or 'ReEvaluationJob' in line:
                print(f'  Удаляю: {line.strip()}')
                continue
            new_lines.append(line)
        
        f.write_text('\n'.join(new_lines), encoding='utf-8')
        fixed_count += 1
        
        try:
            py_compile.compile(str(f), doraise=True)
            print(f'  ✅ Валиден')
        except py_compile.PyCompileError as e:
            print(f'  ❌ Ошибка: {e}')

print(f'\\n✅ Исправлено {fixed_count} файлов')