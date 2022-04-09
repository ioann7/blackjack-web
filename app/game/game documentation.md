# Документация по запросам на модуль game #

## new (POST) ##

Создать новую игру

#### Пример ответа ####

```json lines
{
  "game_id": 3,
  "state": "started",
  "success": true,
}
{
  "success": false,
  "error": "game_already_started",
  "message": "Game already started"
}
```

#### Возможные ошибки ####

`game_already_started` - Игра уже началась.

## info (GET) ##

Получить информацию об игре. Если игра была закончена добавляются поля:
`deck_of_cards`
`dealer_cards`
`closed_cards_of_dealer`

#### Параметры запроса ####

[last_game: bool] - если true, возвращает последнюю игру, вне зависимости активна ли она.

#### Пример ответа ####

```json lines
{
  "created": "2022-04-08 05:50:54.749635",
  "id": 3,
  "open_card_of_dealer": {
    "game_id": 3,
    "id": 127,
    "name": "7",
    "owner": "dealer",
    "suit": "club",
    "weight": 7
  },
  "player_cards": [
    {
      "game_id": 3,
      "id": 117,
      "name": "5",
      "owner": "player",
      "suit": "diamond",
      "weight": 5
    },
    {
      "game_id": 3,
      "id": 149,
      "name": "K",
      "owner": "player",
      "suit": "diamond",
      "weight": 10
    }
  ],
  "result": "in_progress",
  "state": "started"
}

{
  "success": false,
  "error": "game_not_found",
  "message": "Game not found. Try start new game"
}
```

#### Возможные ошибки ####

`game_not_found` - Не удалось найти игру.

## take_card (GET) ##

Взять ещё одну карту.

#### Пример ответа ####

```json lines
{
  "game_info": "", // game info если игра завершится то, будет более подробное описание
  "success": true
}

{
  "success": false,
  "error": "game_not_found",
  "message": "Game not found. Try start new game"
}
```

#### Возможные ошибки ####
`game_not_found` - Не удалось найти игру.

`game_already_finished` - Текущая игра завершилась.

## stand (GET) ##

Перестать брать карты, и дать ход дилеру.

#### Пример ответа ####

```json lines
{
  "game_info": "", // game info если игра завершится то, будет более подробное описание
  "success": true
}

{
  "success": false,
  "error": "game_not_found",
  "message": "Game not found. Try start new game"
}
```

#### Возможные ошибки ####
`game_not_found` - Не удалось найти игру.

`game_already_finished` - Текущая игра завершилась.
