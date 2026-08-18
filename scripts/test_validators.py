from engines.writing.validators import validate_content

test_text = """Как квантовые компьютеры изменят криптографию?

Это действительно революционное достижение! Google представила квантовый чип Willow, который решает задачи за минуты, на которые обычному компьютеру потребовались бы миллионы лет.

В настоящее время данное достижение является прорывом в области квантовых вычислений. Соответственно, это безусловно изменит рынок.

Что думаете? Как это повлияет на безопасность?"""

result = validate_content(test_text, 'telegram')
print(f'Valid: {result["is_valid"]}')
print(f'Summary: {result["summary"]}')
print(f'Issues ({len(result["issues"])}):')
for issue in result['issues'][:5]:
    print(f'  [{issue.severity}] {issue.category}: {issue.message}')