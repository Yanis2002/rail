import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import base64
import io
from flask import Flask, render_template_string
from scipy.integrate import simpson

app = Flask(__name__)


def generate_smooth_noise(length, amplitude=1.0, frequency=0.1):
    """Генерирует гладкий шум как функцию синусоид с разными частотами"""
    x = np.arange(length)
    noise = np.zeros(length)

    # Комбинируем несколько синусоид с разными частотами
    for i in range(3, 8):
        phase = np.random.rand()
        freq = frequency * (i / 5)
        noise += (np.random.rand() * amplitude / i) * np.sin(2 * np.pi * freq * x + phase)

    return noise


def generate_ideal_rail_profile(length=500):
    """Генерирует профиль идеальной рельсы"""
    # Создаем базовый профиль рельсы как нулевую линию
    profile = np.zeros(length)
    return profile


def generate_defect_rail_profile(length=500, defect_amplitude=0.5, defect_frequency=0.05):
    """Генерирует профиль рельсы с дефектами как гладкую функцию"""
    # Начинаем с идеальной рельсы
    profile = generate_ideal_rail_profile(length)

    # Добавляем гладкие дефекты
    defects = generate_smooth_noise(length, defect_amplitude, defect_frequency)

    return profile + defects


def calculate_defect_integral(ideal_profile, defect_profile):
    """Рассчитывает интеграл разности между идеальным и дефектным профилями"""
    difference = np.abs(defect_profile - ideal_profile)
    x = np.arange(len(ideal_profile))

    # Используем метод Симпсона для интегрирования
    integral = simpson(difference, x)
    return integral, difference


def plot_rails(rail1_top, rail1_bottom, rail2_top, rail2_bottom, x):
    """Создает визуализацию двух параллельных рельсов"""
    fig = Figure(figsize=(12, 6))
    ax = fig.add_subplot(1, 1, 1)

    # Расстояние между рельсами
    rail_distance = 10

    # Первая рельса
    ax.plot(x, rail1_top, 'r-', linewidth=2, label='Рельса 1 (верх)')
    ax.plot(x, rail1_bottom, 'r-', linewidth=2, label='Рельса 1 (низ)')

    # Вторая рельса
    ax.plot(x, rail2_top + rail_distance, 'g-', linewidth=2, label='Рельса 2 (верх)')
    ax.plot(x, rail2_bottom + rail_distance, 'g-', linewidth=2, label='Рельса 2 (низ)')

    # Добавляем заливку между линиями для каждой рельсы
    ax.fill_between(x, rail1_top, rail1_bottom, color='r', alpha=0.3)
    ax.fill_between(x, rail2_top + rail_distance, rail2_bottom + rail_distance, color='g', alpha=0.3)

    ax.set_title('Профили железнодорожных рельсов')
    ax.set_xlabel('Расстояние (см)')
    ax.set_ylabel('Высота (мм)')
    ax.legend()
    ax.grid(True)

    return fig


def plot_defects_analysis(ideal_top, defect_top, ideal_bottom, defect_bottom, x, diff_top, diff_bottom, integral_top,
                          integral_bottom):
    """Создает визуализацию дефектов и их анализа с одинаковыми шкалами"""
    fig = Figure(figsize=(12, 10))

    # Найдем общие пределы для осей Y, чтобы графики были одинаково масштабированы
    all_values = np.concatenate([ideal_top, defect_top, ideal_bottom, defect_bottom])
    y_min = np.min(all_values) - 0.05
    y_max = np.max(all_values) + 0.05

    # Найдем общие пределы для графиков разности
    diff_values = np.concatenate([diff_top, diff_bottom])
    diff_max = np.max(diff_values) + 0.02
    diff_min = 0  # Для разности начинаем с нуля

    # Верхний профиль и его дефекты
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(x, ideal_top, 'b-', linewidth=1, label='Идеальный профиль')
    ax1.plot(x, defect_top, 'r-', linewidth=1, label='Дефектный профиль')
    ax1.set_title('Верхний профиль рельсы')
    ax1.set_ylim(y_min, y_max)  # Устанавливаем одинаковые пределы
    ax1.legend()
    ax1.grid(True)

    # Нижний профиль и его дефекты
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(x, ideal_bottom, 'b-', linewidth=1, label='Идеальный профиль')
    ax2.plot(x, defect_bottom, 'r-', linewidth=1, label='Дефектный профиль')
    ax2.set_title('Нижний профиль рельсы')
    ax2.set_ylim(y_min, y_max)  # Устанавливаем одинаковые пределы
    ax2.legend()
    ax2.grid(True)

    # Разность (дефекты) верхнего профиля
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.fill_between(x, np.zeros_like(x), diff_top, color='r', alpha=0.5)
    ax3.set_title(f'Дефекты верхнего профиля (Интеграл: {integral_top:.2f} мм²)')
    ax3.set_ylim(diff_min, diff_max)  # Устанавливаем одинаковые пределы
    ax3.grid(True)

    # Разность (дефекты) нижнего профиля
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.fill_between(x, np.zeros_like(x), diff_bottom, color='r', alpha=0.5)
    ax4.set_title(f'Дефекты нижнего профиля (Интеграл: {integral_bottom:.2f} мм²)')
    ax4.set_ylim(diff_min, diff_max)  # Устанавливаем одинаковые пределы
    ax4.grid(True)

    fig.tight_layout()
    return fig


def plot_to_html(fig):
    """Конвертирует matplotlib Figure в HTML-изображение"""
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"


@app.route('/')
def index():
    # Параметры рельсов
    length = 500  # длина в см
    rail_height = 3  # высота рельсы в мм
    x = np.arange(length)

    # Генерируем профили идеальных рельсов
    ideal_top1 = generate_ideal_rail_profile(length)
    ideal_bottom1 = ideal_top1 - rail_height

    ideal_top2 = generate_ideal_rail_profile(length)
    ideal_bottom2 = ideal_top2 - rail_height

    # Генерируем профили рельсов с дефектами
    defect_top1 = generate_defect_rail_profile(length, defect_amplitude=0.3, defect_frequency=0.02)
    defect_bottom1 = defect_top1 - rail_height + generate_defect_rail_profile(length, defect_amplitude=0.2,
                                                                              defect_frequency=0.03)

    defect_top2 = generate_defect_rail_profile(length, defect_amplitude=0.4, defect_frequency=0.015)
    defect_bottom2 = defect_top2 - rail_height + generate_defect_rail_profile(length, defect_amplitude=0.25,
                                                                              defect_frequency=0.025)

    # Рассчитываем интегралы дефектов
    integral_top1, diff_top1 = calculate_defect_integral(ideal_top1, defect_top1)
    integral_bottom1, diff_bottom1 = calculate_defect_integral(ideal_bottom1, defect_bottom1)

    integral_top2, diff_top2 = calculate_defect_integral(ideal_top2, defect_top2)
    integral_bottom2, diff_bottom2 = calculate_defect_integral(ideal_bottom2, defect_bottom2)

    # Создаем общую визуализацию рельсов
    fig_rails = plot_rails(defect_top1, defect_bottom1, defect_top2, defect_bottom2, x)

    # Создаем анализ дефектов для обеих рельсов
    fig_defects1 = plot_defects_analysis(
        ideal_top1, defect_top1, ideal_bottom1, defect_bottom1,
        x, diff_top1, diff_bottom1, integral_top1, integral_bottom1
    )

    fig_defects2 = plot_defects_analysis(
        ideal_top2, defect_top2, ideal_bottom2, defect_bottom2,
        x, diff_top2, diff_bottom2, integral_top2, integral_bottom2
    )

    # Конвертируем графики в HTML
    rails_html = plot_to_html(fig_rails)
    defects1_html = plot_to_html(fig_defects1)
    defects2_html = plot_to_html(fig_defects2)

    # Суммируем интегралы для итоговой оценки
    total_integral1 = integral_top1 + integral_bottom1
    total_integral2 = integral_top2 + integral_bottom2

    # Оценка состояния рельсов
    def evaluate_condition(integral):
        if integral < 20:
            return "Отличное", "green"
        elif integral < 50:
            return "Хорошее", "blue"
        elif integral < 100:
            return "Требует внимания", "orange"
        else:
            return "Требует замены", "red"

    condition1, color1 = evaluate_condition(total_integral1)
    condition2, color2 = evaluate_condition(total_integral2)

    # Создаем HTML-шаблон
    html_template = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Анализ дефектов железнодорожных рельсов</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }
                h1, h2, h3 {
                    color: #333;
                }
                .container {
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                .assessment {
                    font-size: 18px;
                    font-weight: bold;
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                    display: inline-block;
                }
                .stats {
                    display: flex;
                    justify-content: space-between;
                    flex-wrap: wrap;
                }
                .stat-box {
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                    flex: 1;
                    min-width: 200px;
                    margin-right: 10px;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    display: block;
                    margin: 0 auto;
                }
            </style>
        </head>
        <body>
            <h1>Система анализа дефектов железнодорожных рельсов</h1>

            <div class="container">
                <h2>Общий вид рельсов</h2>
                <p>Визуализация двух параллельных рельсов. Красным показан первый рельс, зеленым - второй.</p>
                {{ rails_html|safe }}
            </div>

            <div class="container">
                <h2>Анализ первого рельса</h2>

                <div class="stats">
                    <div class="stat-box">
                        <h3>Интеграл дефектов верхнего профиля</h3>
                        <p>{{ integral_top1|round(2) }} мм²</p>
                    </div>
                    <div class="stat-box">
                        <h3>Интеграл дефектов нижнего профиля</h3>
                        <p>{{ integral_bottom1|round(2) }} мм²</p>
                    </div>
                    <div class="stat-box">
                        <h3>Общий интеграл дефектов</h3>
                        <p>{{ total_integral1|round(2) }} мм²</p>
                    </div>
                </div>

                <h3>Оценка состояния:</h3>
                <div class="assessment" style="background-color: {{ color1 }}; color: white;">
                    {{ condition1 }}
                </div>

                {{ defects1_html|safe }}
            </div>

            <div class="container">
                <h2>Анализ второго рельса</h2>

                <div class="stats">
                    <div class="stat-box">
                        <h3>Интеграл дефектов верхнего профиля</h3>
                        <p>{{ integral_top2|round(2) }} мм²</p>
                    </div>
                    <div class="stat-box">
                        <h3>Интеграл дефектов нижнего профиля</h3>
                        <p>{{ integral_bottom2|round(2) }} мм²</p>
                    </div>
                    <div class="stat-box">
                        <h3>Общий интеграл дефектов</h3>
                        <p>{{ total_integral2|round(2) }} мм²</p>
                    </div>
                </div>

                <h3>Оценка состояния:</h3>
                <div class="assessment" style="background-color: {{ color2 }}; color: white;">
                    {{ condition2 }}
                </div>

                {{ defects2_html|safe }}
            </div>
        </body>
    </html>
    """

    return render_template_string(html_template,
                                  rails_html=rails_html,
                                  defects1_html=defects1_html,
                                  defects2_html=defects2_html,
                                  integral_top1=integral_top1,
                                  integral_bottom1=integral_bottom1,
                                  total_integral1=total_integral1,
                                  integral_top2=integral_top2,
                                  integral_bottom2=integral_bottom2,
                                  total_integral2=total_integral2,
                                  condition1=condition1,
                                  color1=color1,
                                  condition2=condition2,
                                  color2=color2)


if __name__ == '__main__':
    app.run(debug=True)