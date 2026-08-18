import pathlib
p = pathlib.Path('./backend/automation/runtime/workflow_runtime.py')
s = p.read_text(encoding='utf-8')
changes = []

# Ищем вызов _log_execution с параметром error и убираем его
old_log = '''            self._log_execution(execution_id, node_id, result.status.value, result.error)'''
new_log = '''            self._log_execution(execution_id, node_id, result.status.value)'''

if old_log in s:
    s = s.replace(old_log, new_log, 1)
    changes.append('removed error parameter from _log_execution call')

# Также в методе _log_execution убираем параметр error из создания ExecutionLogORM
old_orm = '''                log_entry = ExecutionLogORM(
                    execution_id=execution_id,
                    stage=stage,
                    status=status,
                    error=error,
                )'''
new_orm = '''                log_entry = ExecutionLogORM(
                    execution_id=execution_id,
                    stage=stage,
                    status=status,
                )'''

if old_orm in s:
    s = s.replace(old_orm, new_orm, 1)
    changes.append('removed error field from ExecutionLogORM creation')

if changes:
    p.write_text(s, encoding='utf-8')
    print(f'OK: применены фиксы:')
    for c in changes:
        print(f'   ✅ {c}')
else:
    print('ℹ️ Ничего не изменилось')