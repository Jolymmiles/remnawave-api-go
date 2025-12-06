# API Processing Pipeline

Единый скрипт для автоматической обработки OpenAPI спецификаций и генерации Go клиента.

## Что делает

Pipeline выполняет 4 шага:

1. **Консолидация дубликатов** - находит и объединяет идентичные схемы
2. **Переименование** - заменяет verbose имена на common (UserResponse вместо CreateUserResponseDto)
3. **Генерация ogen** - создаёт Go клиент через `go generate`
4. **Генерация client_ext.go** - создаёт организованный wrapper с sub-clients

## Использование

```bash
python3 pipeline.py api-2-3-0.json
```

## Результаты

Pipeline создаёт:

- `api-2-2-2-consolidated.json` - консолидированная спецификация
- `api-2-2-2-final.json` - финальная спецификация с переименованными схемами
- `api/oas_client_gen.go` - сгенерированный ogen клиент
- `api/client_ext.go` - wrapper с организованными sub-clients

## Пример вывода

```
======================================================================
 PIPELINE COMPLETED SUCCESSFULLY
======================================================================

Results:
  • Schemas:     190 → 107 (-83, -43%)
  • Renamed:     28 schemas
  • Controllers: 25
  • Methods:     136

Generated files:
  • api-2-2-2-consolidated.json
  • api-2-2-2-final.json
  • api/oas_client_gen.go
  • api/client_ext.go
```

## Особенности

### Консолидация

Находит идентичные схемы по содержимому и объединяет их:
- DeleteUserResponseDto, DeleteNodeResponseDto → DeleteResponse
- CreateUserResponseDto, UpdateUserResponseDto → UserResponse
- LoginResponseDto, RegisterResponseDto → TokenResponse

### Переименование

Применяет общепринятые naming conventions:
- `CreateUserResponseDto` → `UserResponse`
- `BulkActionResponseDto` → `BulkActionResponse`
- `GetAllTagsResponseDto` → `TagsResponse`

### Client Extension

Генерирует организованный wrapper:

```go
client := remapi.NewClientExt(baseClient)

// Organised access to 139 operations
users, _ := client.Users().GetAllUsers(ctx)
tokens, _ := client.ApiTokens().FindAll(ctx)
nodes, _ := client.Nodes().GetAllNodes(ctx)
```

## Требования

- Python 3.7+
- Go 1.21+
- ogen установлен (для go generate)

## Настройка

Для изменения правил переименования отредактируйте функцию `create_rename_map()` в `pipeline.py`.

## Архитектура

```
api-2-2-2.json
    ↓
[Consolidate] → api-2-2-2-consolidated.json (190 → 107 schemas)
    ↓
[Rename] → api-2-2-2-final.json (common names)
    ↓
[Ogen] → api/oas_client_gen.go (base client)
    ↓
[ClientExt] → api/client_ext.go (organized wrapper)
```

## Интеграция с CI/CD

Добавьте в `.github/workflows/`:

```yaml
- name: Process API spec
  run: python3 pipeline.py api-2-2-2.json

- name: Commit generated code
  run: |
    git add api/
    git commit -m "chore: regenerate API client"
```

## License

MIT
