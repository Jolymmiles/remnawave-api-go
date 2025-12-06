# Улучшения консолидации схем

## Обзор

`smart_consolidate.py` - улучшенная система консолидации OpenAPI схем с:
- Многоуровневым анализом дубликатов
- Интеллектуальным выбором канонических имен
- Анализом по атрибутному составу

## Уровни анализа дубликатов

### 1. Exact (точное совпадение)
Идентичный JSON контент. **Безопасно консолидировать.**

### 2. Structural (структурное совпадение)
Одинаковая структура с учетом constraints (minLength, pattern, etc.).
Отличаются только метаданные (description, example). **Безопасно консолидировать.**

### 3. Structural Loose (без constraints)
Одинаковая структура, но могут отличаться валидационные правила.
**Консолидация возможна, но потеряется валидация.**

### 4. Attribute (по атрибутам)
Одинаковый набор полей (имя + тип), но может отличаться структура.
**Только для анализа, не для консолидации.**

## Использование

```python
from smart_consolidate import SmartConsolidator

with open('api.json') as f:
    spec = json.load(f)

consolidator = SmartConsolidator(spec)

# Полный анализ
report = consolidator.analyze_duplicates()
print(f"Exact: {report['exact']['count']} groups")
print(f"Structural: {report['structural']['count']} groups")
print(f"Near-duplicates: {report['near_duplicates']['count']} groups")

# Консолидация
rename_map, stats = consolidator.consolidate()
new_spec = consolidator.apply_consolidation(rename_map)
```

## Автоматические имена

| Паттерн исходных имен | Каноническое имя |
|----------------------|------------------|
| Delete*Response | DeleteResponse |
| BulkAll*, Restart*, Add/RemoveUsersTo* | EventResponse |
| Bulk*UsersResponse | BulkActionResponse |
| Login, Register, OAuth2* | TokenResponse |
| Create/Update/Get*User* | UserResponse |
| GetAll*Response | *ListResponse |

## Пример вывода

```
=== COMPREHENSIVE DUPLICATE ANALYSIS ===
Total schemas: 203

Level                    Groups  Schemas
-----------------------------------------
Exact                       33     127
Structural                  34     130
Structural (loose)          36     134
Attribute                    8     161

Near-duplicates              2       7
Constraint-only              2       4
```

## Интеграция в pipeline

Заменить `consolidate_schemas()` и `create_rename_map()` на:

```python
from smart_consolidate import SmartConsolidator

def consolidate_schemas_smart(input_file, output_file):
    with open(input_file) as f:
        spec = json.load(f)
    
    consolidator = SmartConsolidator(spec)
    rename_map, stats = consolidator.consolidate()
    new_spec = consolidator.apply_consolidation(rename_map)
    
    with open(output_file, 'w') as f:
        json.dump(new_spec, f, indent=2)
    
    return stats
```
