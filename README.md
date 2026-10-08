# Shock Radar

**Прогнозирование и обнаружение структурных изменений муниципальных потребительских расходов**

Shock Radar — исследовательский pipeline на данных СберИндекса: сначала строится прогноз ожидаемых расходов, затем отклонения от прогноза используются для обнаружения статистически необычных изменений. Сигналы объединяются в эпизоды, сопоставляются с категориями расходов и приоритизируются для внешней проверки.

> **Назначение:** поиск и ранжирование статистических аномалий, а не автоматическое установление причин экономических событий.

## Архитектура

```text
СберИндекс → подготовка и проверка муниципальных рядов
           → forecasting (Prophet / Chronos-Bolt / ETS / seasonal / ensembles)
           → forecast surprise
           → size-aware shock detector
           → месячные сигналы → shock episodes
           → категориальная атрибуция → приоритеты
           → external audit / News Alignment
```

## Основные результаты

### Прогнозирование

Единый исторический multi-horizon benchmark: **2 016 рядов × 4 forecast origins (июнь–сентябрь 2024) × 3 горизонта = 24 192 прогнозные ячейки на модель**.

| Модель | MAE |
|---|---:|
| **Reference ensemble (Chronos + ETS + Seasonal Growth)** | **761.916** |
| Chronos relative | 885.764 |
| ETS relative | 925.792 |
| Seasonal Growth | 995.026 |
| Prophet | 1428.002 |

Reference ensemble уменьшает MAE относительно Prophet на **46.64%** на одинаковых прогнозных ячейках. На Jun–Sep challenger benchmark residual correction показывает **758.339 MAE** против 761.916 у reference. На отдельной поздней проверке Oct–Nov online adaptive ensemble показывает **834.331 MAE** против 858.810 у Static 45/55 и 880.397 у Reference. Абсолютные MAE между Jun–Sep и Oct–Nov напрямую не сопоставляются.

### Обнаружение структурных изменений

Независимый synthetic TEST: **5 040 контролируемых событий**. Пороги классических методов выбирались по DEV до TEST.

| Метод | Event Recall | FAR / 100 фоновых ряд-месяцев | Month F1 |
|---|---:|---:|---:|
| Cross-sectional baseline | 56.23% | 3.224 | 20.56% |
| **Size-aware forecast-surprise** | **65.71%** | 3.448 | 35.57% |
| CUSUM | 50.75% | 3.224 | **55.35%** |
| Page–Hinkley | 44.76% | 3.447 | 32.96% |

Size-aware обнаруживает на **478 событий больше**, чем cross-sectional baseline: +9.48 п.п. Event Recall (bootstrap 95% CI: **[+7.92; +10.52] п.п.**). Он выбран по приоритетной event-level метрике; CUSUM лучше по помесячному F1. Synthetic TEST не является измерением precision на реальных экономических событиях.

### Применение к реальным данным

| Показатель | Значение |
|---|---:|
| Месячные сигналы | 975 |
| Муниципальные ряды с сигналами | 546 |
| Shock episodes | 826 |
| Эпизоды с безопасной категориальной атрибуцией | 776 |
| Эпизоды с сильным категориальным драйвером | 639 |

В заранее зафиксированном TOP-10 внешнего аудита: **3 strong match, 3 possible match, 2 external event without clear link, 2 no clear explanation**. Это не оценка реального precision детектора. Три strong match относятся к одной административной реформе.

### News Alignment

Реализованы структурированный реестр событий, привязка к `series_id × event_month`, количественный ретроспективный аудит TOP-10 и проверяемое правило фильтрации по `publication_date` относительно момента прогноза. Из десяти ретроспективных записей семь имеют датированную комбинацию муниципального ряда и месяца, но **ни одна запись не допущена к forecasting**: даты публикации не подтверждены. Прирост MAE от новостей не заявляется. Новости используются для независимой post-hoc интерпретации.

## Структура проекта

```text
shock-radar/
├── README.md
├── requirements.txt
├── configs/
│   └── final_config.yaml
├── notebooks/
│   ├── 00_data_final.ipynb
│   ├── 01_forecasting_baselines_final.ipynb
│   ├── 02_forecasting_static_final.ipynb
│   ├── 03_forecasting_final.ipynb
│   ├── 04_shock_detector_final.ipynb
│   ├── 05_real_shocks_and_attribution_final.ipynb
│   └── 06_results_final.ipynb
├── data/
│   ├── README.md
│   ├── raw/       # исходные данные, не публикуются в репозитории
│   └── interim/   # подготовленные артефакты и результаты
└── reports/        # конкурсный отчёт и презентация
```

## Данные

Основной источник — **СберИндекс: «Потребительские безналичные расходы на уровне муниципальных образований»**. Используются также справочники **Росстата / ОКТМО (2023–2024)**. Исходные данные не включены в публичную сборку: для запуска этапа `00` их нужно получить у правообладателей и разместить по структуре, описанной в [data/README.md](data/README.md):

```text
data/raw/sberindex/consumption/
data/raw/rosstat/oktmo/
```

Для проверки зафиксированных результатов в `data/interim/` включены подготовленные артефакты. Отдельные этапы могут зависеть от заранее подготовленных промежуточных входов; наличие этих входов не следует смешивать с полной воспроизводимостью всего исследовательского поиска из исходных файлов.

## Установка

Рекомендуемое окружение: **Python 3.10**, Linux/WSL2. Для Chronos-Bolt может использоваться NVIDIA GPU; вариант PyTorch в исходном рабочем окружении — `2.9.1+cu128`.

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
# Для совместимой системы NVIDIA / CUDA 12.8 (если требуется GPU):
python -m pip install torch==2.9.1 --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r requirements.txt
python -m pip check
python -m ipykernel install --user --name shock-radar --display-name 'Python (Shock Radar)'
```

При использовании другой платформы установку PyTorch следует адаптировать по официальной инструкции. Версии в `requirements.txt` отражают проверенное исходное окружение; развёртывание с нуля на независимом компьютере требует отдельной проверки.

## Запуск и проверка

Откройте папку репозитория в VS Code с поддержкой Jupyter или запустите доступный Jupyter-интерфейс. Выберите kernel `Python (Shock Radar)`. **Рабочая директория — корень репозитория или каталог `notebooks/`**, если конкретный notebook допускает оба варианта.

Порядок этапов:

1. `00_data_final.ipynb` — подготовка и проверка панельных данных.
2. `01_forecasting_baselines_final.ipynb` — единый baseline/Prophet/Chronos benchmark.
3. `02_forecasting_static_final.ipynb` — статические модели и фиксированный ансамбль.
4. `03_forecasting_final.ipynb` — residual correction и online adaptive forward validation.
5. `04_shock_detector_final.ipynb` — synthetic TEST и сравнение четырёх детекторов.
6. `05_real_shocks_and_attribution_final.ipynb` — эпизоды, категории, внешний аудит и News Alignment.
7. `06_results_final.ipynb` — итоговая сводка без повторной оптимизации моделей.

**Быстрая проверка результатов:** откройте notebook `06` с сохранёнными входными артефактами `data/interim/`, выполните ячейки по порядку и проверьте сообщения `FINAL RESULTS NOTEBOOK: PASSED` и `FINAL RESULTS ARTIFACT INTEGRITY: PASSED`. Другие этапы могут быть вычислительно затратными; `01` включает Prophet и Chronos.

Ключевые итоговые артефакты:

- `data/interim/baseline_multihorizon_summary.csv`
- `data/interim/forecast_final_summary.csv`
- `data/interim/shock_detector_four_method_test_comparison.csv`
- `data/interim/shock_real_cases_summary.csv`
- `data/interim/shock_news_alignment_quantitative_top10.csv`
- `data/interim/final_results_summary.csv`
- `data/interim/final_results_manifest.json`

Настройки описаны в [`configs/final_config.yaml`](configs/final_config.yaml). Он фиксирует конфигурацию и служит для сверки параметров; не все notebook-параметры обязательно читаются непосредственно из YAML.


## Воспроизводимость и использование

Проект предоставляет финальные ноутбуки, конфигурацию, фиксированные результаты и протоколы проверки. Не все подготовительные исследовательские артефакты создаются в семи итоговых ноутбуках; для точного воспроизведения зафиксированных экспериментов используются предоставленные входные данные и результаты.

Полное независимое исполнение всего pipeline на чистой машине не заявляется как уже проведённое. Условия повторного распространения исходных и производных данных необходимо проверить перед публикацией.

## Материалы конкурсной работы

Для быстрого знакомства с проектом:

**Презентация**

[Shock Radar — PDF-презентация](reports/Shock_Radar_Presentation_Green_RU.pdf)

**Методологический отчёт**

[Методологический отчёт на русском языке](reports/Shock_Radar_Methodology_RU.docx)

**Основные эксперименты**

- [Сравнение прогнозирования с Prophet](notebooks/01_forecasting_baselines_final.ipynb)
- [Итоговое прогнозирование](notebooks/03_forecasting_final.ipynb)
- [Сравнение методов обнаружения изменений](notebooks/04_shock_detector_final.ipynb)
- [Реальные эпизоды и анализ внешних событий](notebooks/05_real_shocks_and_attribution_final.ipynb)
- [Финальная сводка результатов](notebooks/06_results_final.ipynb)

Ноутбуки содержат сохранённые результаты выполнения.
Для повторного запуска некоторых этапов необходимы
исходные данные и подготовленные входные артефакты.
