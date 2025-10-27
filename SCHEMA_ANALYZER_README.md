# OpenAPI Schema Duplicate Finder

Утилита для анализа OpenAPI/Swagger JSON файлов с целью выявления дубликатов и идентичных моделей (DTOs).

## Описание

Этот скрипт анализирует OpenAPI спецификации и находит:

- **Дубликатные схемы** - идентичные модели с разными именами
- **Паттерны ответов** - группирует схемы по типам (удаление, события, токены и т.д.)
- **Возможности консолидации** - предлагает рекомендации по объединению моделей
- **Статистику** - показывает степень дублирования в спецификации

## Установка

Скрипт требует только Python 3.6+ (встроенные библиотеки):

```bash
# Сделать исполняемым
chmod +x find_duplicate_schemas.py
```

## Использование

### Базовое использование

```bash
# Анализ всех дубликатов
python3 find_duplicate_schemas.py <path_to_openapi.json>

# Примеры
python3 find_duplicate_schemas.py api-2-2-2.json
python3 find_duplicate_schemas.py openapi.json
```

### С ограничением количества групп

```bash
# Показать только первые 10 групп дубликатов
python3 find_duplicate_schemas.py api-2-2-2.json 10
```

### Запуск из другой директории

```bash
cd /path/to/project
python3 find_duplicate_schemas.py api-2-2-2.json
```

## Пример вывода

```
📂 Reading file: api-2-2-2.json
📊 File size: 0.81 MB
✓ Schemas extracted successfully

==================================================================================================================================
📈 SUMMARY STATISTICS
==================================================================================================================================
Total schemas:        190
Unique definitions:   107
Duplicate groups:     28
Redundant schemas:    83
==================================================================================================================================
```

## Особенности

### ✓ Поддержка поврежденных JSON файлов

Скрипт может обрабатывать файлы с незавершенным JSON, извлекая только раздел `schemas`:

```python
# Если полный JSON не парсится, попытается извлечь только schemas
⚠ Full JSON parse failed, attempting schema extraction...
✓ Schemas extracted successfully (partial extraction)
```

### ✓ Детальный анализ

Для каждой группы дубликатов показывает:
- Список идентичных моделей
- Тип структуры (объект, ссылка и т.д.)
- Количество свойств
- Предпросмотр определения

### ✓ Паттерны и категоризация

Автоматически определяет типичные паттерны:
- **Delete Operations** - простые ответы удаления (`{isDeleted: boolean}`)
- **Event Based** - события (`{eventSent: boolean}`)
- **Bulk Operations** - массовые операции (`{affectedRows: number}`)
- **Token Responses** - авторизация (`{accessToken: string}`)
- **Empty Wrapper** - пустые обертки (`{response: {}}`)
- **List Responses** - списки объектов

### ✓ Рекомендации по приоритетам

```
🔴 HIGH PRIORITY (5+ duplicates) - объединить в первую очередь
🟡 MEDIUM PRIORITY (3-4 duplicates) - рассмотреть консолидацию  
🟢 LOW PRIORITY (2 duplicates) - низкий приоритет
```

## Примеры анализа

### Пример 1: Ответы пользователя (9 идентичных моделей)

```
[GROUP 1] 9 IDENTICAL MODELS
Models: CreateUserResponseDto, DisableUserResponseDto, EnableUserResponseDto, 
        GetUserByShortUuidResponseDto, GetUserByUsernameResponseDto, GetUserByUuidResponseDto, 
        ResetUserTrafficResponseDto, RevokeUserSubscriptionResponseDto, UpdateUserResponseDto

Рекомендация: Можно объединить в одну UserResponseDto
```

### Пример 2: Удаление объектов (8 идентичных моделей)

```
[GROUP 2] 8 IDENTICAL MODELS
Models: DeleteConfigProfileResponseDto, DeleteExternalSquadResponseDto, 
        DeleteHostResponseDto, DeleteInfraProviderByUuidResponseDto, etc.

Schema: { "properties": { "response": { "isDeleted": { "type": "boolean" } } } }

Рекомендация: Использовать generic DeleteResponseDto<T>
```

### Пример 3: Массовые операции (6 идентичных запросов)

```
[GROUP 5] 6 IDENTICAL MODELS
Models: BulkDeleteHostsRequestDto, BulkDeleteUsersRequestDto, 
        BulkDisableHostsRequestDto, BulkEnableHostsRequestDto, etc.

Schema: { "properties": { "uuids": { "items": { "format": "uuid", "type": "string" }, "type": "array" } } }

Рекомендация: Использовать BulkActionRequestDto с generics
```

## Интеграция с CI/CD

Добавить в ваш CI/CD pipeline для проверки дублирования:

```bash
# .github/workflows/lint.yml
- name: Check for duplicate schemas
  run: |
    python3 find_duplicate_schemas.py api-2-2-2.json > schema_analysis.txt
    
# Отправить отчет
- name: Upload schema analysis
  uses: actions/upload-artifact@v2
  with:
    name: schema-analysis
    path: schema_analysis.txt
```

## Рекомендации по консолидации

### 1. User Responses (9 дубликатов)

**Текущее:**
```json
CreateUserResponseDto, DisableUserResponseDto, EnableUserResponseDto, 
GetUserByUuidResponseDto, UpdateUserResponseDto, ...
```

**Предлагаемое:**
```go
type UserResponseDto struct {
    Response User `json:"response"`
}

type User struct {
    UUID string `json:"uuid"`
    // ... other fields
}
```

### 2. Delete Operations (8 дубликатов)

**Текущее:**
```json
DeleteUserResponseDto, DeleteHostResponseDto, DeleteNodeResponseDto, ...
```

**Предлагаемое:**
```go
type DeleteResponseDto struct {
    Response struct {
        IsDeleted bool `json:"isDeleted"`
    } `json:"response"`
}
```

### 3. Bulk Request Operations (6 дубликатов)

**Текущее:**
```json
BulkDeleteUsersRequestDto, BulkDeleteHostsRequestDto, 
BulkResetTrafficUsersRequestDto, ...
```

**Предлагаемое:**
```go
type BulkActionRequestDto struct {
    UUIDs []string `json:"uuids"`
}
```

### 4. Bulk Response Operations (6 дубликатов)

**Текущее:**
```json
BulkDeleteUsersResponseDto, BulkUpdateUsersResponseDto, 
BulkRevokeUsersSubscriptionResponseDto, ...
```

**Предлагаемое:**
```go
type BulkActionResponseDto struct {
    Response struct {
        AffectedRows int `json:"affectedRows"`
    } `json:"response"`
}
```

### 5. Auth Token Responses (5 дубликатов)

**Текущее:**
```json
LoginResponseDto, RegisterResponseDto, OAuth2CallbackResponseDto, 
TelegramCallbackResponseDto, VerifyPasskeyAuthenticationResponseDto
```

**Предлагаемое:**
```go
type TokenResponseDto struct {
    Response struct {
        AccessToken string `json:"accessToken"`
    } `json:"response"`
}
```

## Статистика по файлам проекта

### api-2-2-2.json
- **Total schemas:** 190
- **Unique definitions:** 107
- **Duplicate groups:** 28
- **Redundant schemas:** 83 (43.7% дублирования)

### api-2-2-0.json
- **Total schemas:** 195
- **Unique definitions:** 195
- **Duplicate groups:** 0
- **Redundant schemas:** 0

## Использование в коде

```python
#!/usr/bin/env python3
from find_duplicate_schemas import load_schemas, find_duplicates

# Загрузить схемы
schemas = load_schemas('api-2-2-2.json')

# Найти дубликаты
schema_groups, duplicates = find_duplicates(schemas)

# Обработать результаты
for names, schema_json in duplicates:
    print(f"Found {len(names)} identical models: {names}")
```

## Troubleshooting

### Ошибка: "Could not find 'schemas' section"

Проверьте:
- Файл это валидный OpenAPI JSON?
- Используется ли структура `components.schemas`?

### Ошибка: "File not found"

Проверьте:
- Правильный ли путь к файлу?
- Файл существует и доступен?

```bash
# Проверить
ls -la api-2-2-2.json
```

### Медленное выполнение

Для больших файлов (>50MB) может потребоваться время:

```bash
# Ограничить вывод
python3 find_duplicate_schemas.py api-2-2-2.json 5
```

## Лицензия

Этот скрипт является частью проекта Remnawave API.

## Автор

Создано для анализа OpenAPI спецификаций Remnawave API v2.2.2
