from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
import math

APP_VERSION = "1.4"

# -----------------------------
# ТЕМА
# -----------------------------
BG = (0.055, 0.075, 0.11, 1)
PANEL = (0.09, 0.12, 0.17, 1)
PANEL_2 = (0.12, 0.15, 0.21, 1)
ACCENT = (0.18, 0.52, 0.96, 1)
ACCENT_DARK = (0.11, 0.36, 0.74, 1)
TEXT = (0.95, 0.97, 1, 1)
MUTED = (0.68, 0.74, 0.82, 1)
SUCCESS = (0.22, 0.72, 0.48, 1)
DANGER = (0.90, 0.31, 0.31, 1)

Window.clearcolor = BG

# Размер окна задаём только на компьютере для удобства тестирования.
# На Android Kivy должен использовать реальный размер экрана телефона.
if platform not in ("android", "ios"):
    Window.size = (430, 760)

STANDARD_MOTORS = [
    0.55, 0.75, 1.1, 1.5, 2.2, 3, 4, 5.5, 7.5, 11,
    15, 18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132,
    160, 200, 250, 315
]

STANDARD_RATIOS = [5, 7.5, 10, 12.5, 15, 20, 25, 30, 40, 50, 60, 80, 100]
SCREW_DIAMETERS_MM = [160, 200, 250, 300, 325, 400, 500, 600]

XLD_SHAFTS = {
    "XLD3": 35, "XLD4": 45, "XLD5": 55, "XLD6": 65,
    "XLD7": 75, "XLD8": 90, "XLD9": 100,
}

MATERIALS = {
    "Цемент": {"rho": 1200, "fill": 0.30, "vol_eta": 0.85, "friction": 4.0, "rpm_factor": 1.00},
    "Песок сухой": {"rho": 1500, "fill": 0.30, "vol_eta": 0.82, "friction": 3.5, "rpm_factor": 0.90},
    "Песок влажный": {"rho": 1700, "fill": 0.25, "vol_eta": 0.75, "friction": 5.0, "rpm_factor": 0.75},
    "Зола": {"rho": 700, "fill": 0.35, "vol_eta": 0.85, "friction": 3.0, "rpm_factor": 1.00},
    "Гипс порошок": {"rho": 900, "fill": 0.30, "vol_eta": 0.82, "friction": 4.0, "rpm_factor": 0.90},
    "Зерно": {"rho": 750, "fill": 0.40, "vol_eta": 0.90, "friction": 2.0, "rpm_factor": 1.10},
}


# -----------------------------
# РАСЧЁТНЫЕ ФУНКЦИИ
# -----------------------------
def f(text):
    return float(text.replace(",", ".").strip())


def pick_motor(required_kw):
    for p in STANDARD_MOTORS:
        if p >= required_kw:
            return p
    return None


def nearest_ratio(i_required):
    return min(STANDARD_RATIOS, key=lambda x: abs(x - i_required))


def pick_xld_by_torque(torque_nm):
    limits = [
        (450, "XLD3"), (800, "XLD4"), (1500, "XLD5"),
        (2600, "XLD6"), (4200, "XLD7"), (7000, "XLD8"),
        (10000, "XLD9"),
    ]
    for limit, model in limits:
        if torque_nm <= limit:
            return model
    return "выше XLD9"


def screw_capacity_tph(d_mm, shaft_mm, pitch_mm, rpm, rho, fill, vol_eta):
    d = d_mm / 1000
    ds = shaft_mm / 1000
    pitch = pitch_mm / 1000
    area = math.pi / 4 * (d**2 - ds**2)
    q_m3h = area * pitch * rpm * 60 * fill * vol_eta
    return q_m3h * rho / 1000


# -----------------------------
# ВИДЖЕТЫ
# -----------------------------
class RoundedPanel(BoxLayout):
    def __init__(self, bg=PANEL, radius=18, **kwargs):
        super().__init__(**kwargs)
        self._bg = bg
        self._radius = radius
        with self.canvas.before:
            Color(*self._bg)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(radius)])
        self.bind(pos=self._update_rect, size=self._update_rect)

    def _update_rect(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size


class FlatButton(Button):
    def __init__(self, accent=True, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_down = ""
        self.background_color = ACCENT if accent else PANEL_2
        self.color = TEXT
        self.font_size = dp(16)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(54)


class HeaderLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = TEXT
        self.font_size = dp(21)
        self.bold = True
        self.size_hint_y = None
        self.height = dp(46)
        self.halign = "left"
        self.valign = "middle"
        self.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))


class SubLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = MUTED
        self.font_size = dp(13)
        self.halign = "left"
        self.valign = "middle"
        self.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))


class FieldRow(BoxLayout):
    def __init__(self, label, value="", **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(82),
            spacing=dp(5),
            **kwargs
        )

        lbl = Label(
            text=label,
            color=MUTED,
            size_hint_y=None,
            height=dp(25),
            font_size=dp(13),
            halign="left",
            valign="middle",
        )
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))
        self.add_widget(lbl)

        self.input = TextInput(
            text=value,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(17),
            padding=[dp(12), dp(12), dp(12), dp(8)],
            foreground_color=TEXT,
            background_normal="",
            background_active="",
            background_color=PANEL_2,
            cursor_color=TEXT,
        )
        self.add_widget(self.input)


class StyledSpinner(Spinner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ""
        self.background_color = PANEL_2
        self.color = TEXT
        self.font_size = dp(16)
        self.size_hint_y = None
        self.height = dp(52)


class ResultCard(RoundedPanel):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            bg=PANEL_2,
            padding=dp(14),
            spacing=dp(8),
            size_hint_y=None,
            **kwargs
        )
        self.bind(minimum_height=self.setter("height"))

        title = Label(
            text="РЕЗУЛЬТАТ",
            color=SUCCESS,
            font_size=dp(13),
            bold=True,
            size_hint_y=None,
            height=dp(28),
            halign="left",
            valign="middle",
        )
        title.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))
        self.add_widget(title)

        self.label = Label(
            text="Введите данные и нажмите «Рассчитать».",
            color=TEXT,
            size_hint_y=None,
            font_size=dp(15),
            halign="left",
            valign="top",
        )
        self.label.bind(
            width=lambda inst, width: setattr(inst, "text_size", (width, None)),
            texture_size=lambda inst, size: setattr(inst, "height", size[1] + dp(10))
        )
        self.add_widget(self.label)

    def set_text(self, text):
        self.label.text = text


class CalcPage(ScrollView):
    def __init__(self, title, subtitle="", **kwargs):
        super().__init__(do_scroll_x=False, bar_width=dp(5), **kwargs)

        self.body = GridLayout(
            cols=1,
            spacing=dp(12),
            padding=[dp(12), dp(10), dp(12), dp(20)],
            size_hint_y=None
        )
        self.body.bind(minimum_height=self.body.setter("height"))
        self.add_widget(self.body)

        self.body.add_widget(HeaderLabel(text=title))

        if subtitle:
            sub = SubLabel(text=subtitle, size_hint_y=None, height=dp(40))
            self.body.add_widget(sub)

    def add_field(self, label, value):
        row = FieldRow(label, value)
        self.body.add_widget(row)
        return row

    def add_spinner(self, label, text, values):
        wrap = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(82),
            spacing=dp(5)
        )
        lbl = Label(
            text=label,
            color=MUTED,
            size_hint_y=None,
            height=dp(25),
            font_size=dp(13),
            halign="left",
            valign="middle",
        )
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))
        wrap.add_widget(lbl)

        spinner = StyledSpinner(text=text, values=values)
        wrap.add_widget(spinner)
        self.body.add_widget(wrap)
        return spinner

    def add_calc_button(self, text, callback):
        btn = FlatButton(text=text)
        btn.bind(on_release=callback)
        self.body.add_widget(btn)
        return btn

    def add_result(self):
        result = ResultCard()
        self.body.add_widget(result)
        return result

    def error(self, message="Ошибка ввода. Проверьте числовые значения."):
        self.result.set_text("⚠ " + message)


# -----------------------------
# РАЗДЕЛЫ
# -----------------------------
class FanCalc(CalcPage):
    def __init__(self, **kwargs):
        super().__init__("Вентилятор", "Мощность вентилятора и подбор стандартного двигателя.", **kwargs)
        self.q = self.add_field("Расход воздуха, м³/ч", "30000")
        self.dp = self.add_field("Полное давление, Па", "3000")
        self.eta = self.add_field("Общий КПД", "0.70")
        self.reserve = self.add_field("Коэффициент запаса", "1.15")
        self.add_calc_button("РАССЧИТАТЬ", self.calculate)
        self.result = self.add_result()

    def calculate(self, *_):
        try:
            q, dp = f(self.q.input.text), f(self.dp.input.text)
            eta, reserve = f(self.eta.input.text), f(self.reserve.input.text)
            if q <= 0 or dp <= 0 or not (0 < eta <= 1) or reserve < 1:
                raise ValueError

            useful = (q / 3600) * dp / 1000
            shaft = useful / eta
            design = shaft * reserve
            motor = pick_motor(design)

            self.result.set_text(
                f"Полезная аэродинамическая мощность: {useful:.2f} кВт\n"
                f"Мощность на валу: {shaft:.2f} кВт\n"
                f"С учётом запаса: {design:.2f} кВт\n\n"
                f"Рекомендуемый двигатель: {motor if motor else '>315'} кВт"
            )
        except Exception:
            self.error()


class PumpCalc(CalcPage):
    def __init__(self, **kwargs):
        super().__init__("Насос", "Расчёт мощности по расходу и напору.", **kwargs)
        self.q = self.add_field("Расход, м³/ч", "139")
        self.h = self.add_field("Напор, м", "40")
        self.eta = self.add_field("КПД насоса", "0.70")
        self.rho = self.add_field("Плотность жидкости, кг/м³", "1000")
        self.reserve = self.add_field("Коэффициент запаса", "1.15")
        self.add_calc_button("РАССЧИТАТЬ", self.calculate)
        self.result = self.add_result()

    def calculate(self, *_):
        try:
            q, h = f(self.q.input.text), f(self.h.input.text)
            eta, rho = f(self.eta.input.text), f(self.rho.input.text)
            reserve = f(self.reserve.input.text)
            if q <= 0 or h <= 0 or rho <= 0 or not (0 < eta <= 1) or reserve < 1:
                raise ValueError

            hydraulic = rho * 9.81 * (q / 3600) * h / 1000
            shaft = hydraulic / eta
            design = shaft * reserve
            motor = pick_motor(design)

            self.result.set_text(
                f"Гидравлическая мощность: {hydraulic:.2f} кВт\n"
                f"Мощность на валу: {shaft:.2f} кВт\n"
                f"С учётом запаса: {design:.2f} кВт\n\n"
                f"Рекомендуемый двигатель: {motor if motor else '>315'} кВт"
            )
        except Exception:
            self.error()


class ConveyorCalc(CalcPage):
    def __init__(self, **kwargs):
        super().__init__("Ленточный конвейер", "Предварительный подбор мощности привода.", **kwargs)
        self.capacity = self.add_field("Производительность, т/ч", "40")
        self.length = self.add_field("Длина, м", "18")
        self.angle = self.add_field("Угол наклона, °", "22")
        self.resistance = self.add_field("Коэффициент сопротивления", "0.04")
        self.reserve = self.add_field("Коэффициент запаса", "1.35")
        self.add_calc_button("РАССЧИТАТЬ", self.calculate)
        self.result = self.add_result()

    def calculate(self, *_):
        try:
            capacity = f(self.capacity.input.text)
            length = f(self.length.input.text)
            angle = f(self.angle.input.text)
            resistance = f(self.resistance.input.text)
            reserve = f(self.reserve.input.text)

            if capacity <= 0 or length <= 0 or not 0 <= angle < 90 or resistance < 0 or reserve < 1:
                raise ValueError

            mdot = capacity * 1000 / 3600
            vertical_h = length * math.sin(math.radians(angle))
            lift_kw = mdot * 9.81 * vertical_h / 1000
            resist_kw = mdot * 9.81 * resistance * length / 1000
            useful = lift_kw + resist_kw
            design = useful * reserve
            motor = pick_motor(design)

            self.result.set_text(
                f"Высота подъёма: {vertical_h:.2f} м\n"
                f"На подъём материала: {lift_kw:.2f} кВт\n"
                f"Сопротивления: {resist_kw:.2f} кВт\n"
                f"Расчётная мощность: {useful:.2f} кВт\n"
                f"С учётом запаса: {design:.2f} кВт\n\n"
                f"Предварительно двигатель: {motor if motor else '>315'} кВт\n\n"
                f"Примечание: окончательный выбор требует учёта массы ленты, роликоопор, "
                f"пуска под нагрузкой и свойств материала."
            )
        except Exception:
            self.error()


class DriveCalc(CalcPage):
    def __init__(self, **kwargs):
        super().__init__("Редуктор / привод", "Передаточное отношение, мощность и выходной момент.", **kwargs)
        self.n_motor = self.add_field("Обороты двигателя, об/мин", "1500")
        self.n_out = self.add_field("Требуемые выходные обороты, об/мин", "300")
        self.power = self.add_field("Мощность нагрузки, кВт", "11")
        self.eta = self.add_field("КПД передачи", "0.95")
        self.service = self.add_field("Коэффициент режима", "1.25")
        self.add_calc_button("РАССЧИТАТЬ", self.calculate)
        self.result = self.add_result()

    def calculate(self, *_):
        try:
            n_motor = f(self.n_motor.input.text)
            n_out = f(self.n_out.input.text)
            power = f(self.power.input.text)
            eta = f(self.eta.input.text)
            service = f(self.service.input.text)

            if n_motor <= 0 or n_out <= 0 or power <= 0 or not (0 < eta <= 1) or service < 1:
                raise ValueError

            ratio = n_motor / n_out
            p_design = power * service / eta
            torque = 9550 * p_design / n_out
            motor = pick_motor(p_design)

            self.result.set_text(
                f"Требуемое передаточное отношение: i = {ratio:.2f}\n"
                f"Расчётная мощность привода: {p_design:.2f} кВт\n"
                f"Крутящий момент на выходе: {torque:.0f} Н·м\n\n"
                f"Ближайший стандартный двигатель: {motor if motor else '>315'} кВт"
            )
        except Exception:
            self.error()


class PulleyCalc(CalcPage):
    def __init__(self, **kwargs):
        super().__init__("Шкивы / звёздочки", "Расчёт дополнительной ременной или цепной передачи.", **kwargs)
        self.d1 = self.add_field("Ведущий диаметр / число зубьев", "220")
        self.d2 = self.add_field("Ведомый диаметр / число зубьев", "300")
        self.n1 = self.add_field("Обороты ведущего вала, об/мин", "1500")
        self.add_calc_button("РАССЧИТАТЬ", self.calculate)
        self.result = self.add_result()

    def calculate(self, *_):
        try:
            d1, d2, n1 = f(self.d1.input.text), f(self.d2.input.text), f(self.n1.input.text)
            if d1 <= 0 or d2 <= 0 or n1 <= 0:
                raise ValueError

            i = d2 / d1
            n2 = n1 * d1 / d2

            self.result.set_text(
                f"Передаточное отношение: i = {i:.3f}\n"
                f"Обороты ведомого вала: {n2:.2f} об/мин"
            )
        except Exception:
            self.error()


class XLDCalc(CalcPage):
    def __init__(self, **kwargs):
        super().__init__("Редукторы XLD", "Справочный расчёт по модели, мощности и оборотам.", **kwargs)
        self.model = self.add_spinner("Модель редуктора", "XLD5", list(XLD_SHAFTS.keys()))
        self.power = self.add_field("Мощность двигателя, кВт", "11")
        self.n_out = self.add_field("Выходные обороты, об/мин", "300")
        self.add_calc_button("ПОКАЗАТЬ", self.calculate)
        self.result = self.add_result()

    def calculate(self, *_):
        try:
            power = f(self.power.input.text)
            n_out = f(self.n_out.input.text)
            if power <= 0 or n_out <= 0:
                raise ValueError

            shaft = XLD_SHAFTS[self.model.text]
            torque = 9550 * power / n_out

            self.result.set_text(
                f"Модель: {self.model.text}\n"
                f"Ориентировочный выходной вал: Ø{shaft} мм\n"
                f"Крутящий момент: {torque:.0f} Н·м\n\n"
                f"Важно: размеры и допустимые моменты XLD отличаются у производителей. "
                f"Перед изготовлением муфты или звёздочки проверьте паспорт редуктора."
            )
        except Exception:
            self.error()


class ScrewCalc(CalcPage):
    def __init__(self, **kwargs):
        super().__init__(
            "Шнек AUTO",
            "Введите производительность и длину — программа подберёт основные параметры.",
            **kwargs
        )

        self.material = self.add_spinner("Материал", "Цемент", list(MATERIALS.keys()))
        self.target = self.add_field("Требуемая производительность, т/ч", "5")
        self.length = self.add_field("Длина шнека, м", "12")
        self.angle = self.add_field("Угол наклона, °", "20")
        self.motor_rpm = self.add_field("Обороты двигателя, об/мин", "1500")
        self.reserve = self.add_field("Коэффициент запаса мощности", "1.40")
        self.add_calc_button("АВТОМАТИЧЕСКИ ПОДОБРАТЬ", self.calculate)
        self.result = self.add_result()

    def calculate(self, *_):
        try:
            target = f(self.target.input.text)
            length = f(self.length.input.text)
            angle = f(self.angle.input.text)
            motor_rpm = f(self.motor_rpm.input.text)
            reserve = f(self.reserve.input.text)

            if target <= 0 or length <= 0 or motor_rpm <= 0 or not 0 <= angle <= 45 or reserve < 1:
                raise ValueError

            mat = MATERIALS[self.material.text]
            rho = mat["rho"]
            fill = mat["fill"]
            vol_eta = mat["vol_eta"]
            friction = mat["friction"]
            rpm_factor = mat["rpm_factor"]

            incline_factor = max(0.55, 1 - 0.012 * angle)
            effective_eta = vol_eta * incline_factor

            selected = None
            for d_mm in SCREW_DIAMETERS_MM:
                shaft_mm = max(48, round(d_mm * 0.27))
                pitch_mm = round(d_mm * 0.80)
                rpm_max = min(300, (260 * (200 / d_mm) ** 0.45) * rpm_factor)

                cap_at_max = screw_capacity_tph(
                    d_mm, shaft_mm, pitch_mm, rpm_max,
                    rho, fill, effective_eta
                )

                if cap_at_max >= target:
                    needed_rpm = max(25, rpm_max * target / cap_at_max)
                    rpm = math.ceil(needed_rpm / 5) * 5
                    selected = (d_mm, shaft_mm, pitch_mm, rpm, rpm_max)
                    break

            if selected is None:
                self.result.set_text(
                    "Для заданной производительности нужен шнек больше Ø600 мм "
                    "или несколько параллельных шнеков."
                )
                return

            d_mm, shaft_mm, pitch_mm, rpm, rpm_max = selected

            mdot = target * 1000 / 3600
            horizontal_length = length * math.cos(math.radians(angle))
            vertical_h = length * math.sin(math.radians(angle))

            friction_kw = mdot * 9.81 * horizontal_length * friction / 1000
            lift_kw = mdot * 9.81 * vertical_h / 1000
            idle_kw = 0.18 * length * (d_mm / 325) ** 1.5

            shaft_power = friction_kw + lift_kw + idle_kw
            design_power = shaft_power * reserve / 0.92
            motor = pick_motor(design_power)

            ratio_req = motor_rpm / rpm
            ratio_std = nearest_ratio(ratio_req)
            rpm_real = motor_rpm / ratio_std

            motor_for_torque = motor if motor else design_power
            torque = 9550 * motor_for_torque * 0.92 / rpm_real
            xld_model = pick_xld_by_torque(torque)

            actual_capacity = screw_capacity_tph(
                d_mm, shaft_mm, pitch_mm, rpm_real,
                rho, fill, effective_eta
            )

            self.result.set_text(
                f"ПОДБОР ШНЕКА\n\n"
                f"Материал: {self.material.text}\n"
                f"Заданная производительность: {target:.1f} т/ч\n"
                f"Длина: {length:.1f} м   •   Угол: {angle:.1f}°\n\n"
                f"ОСНОВНЫЕ ПАРАМЕТРЫ\n"
                f"Диаметр шнека: Ø{d_mm} мм\n"
                f"Вал / труба: Ø{shaft_mm} мм\n"
                f"Рекомендуемый шаг: {pitch_mm} мм\n"
                f"Расчётные обороты: ≈ {rpm:.0f} об/мин\n"
                f"Ориентировочная верхняя скорость: {rpm_max:.0f} об/мин\n\n"
                f"МОЩНОСТЬ\n"
                f"Перемещение материала: {friction_kw:.2f} кВт\n"
                f"Подъём материала: {lift_kw:.2f} кВт\n"
                f"Холостой ход / потери: {idle_kw:.2f} кВт\n"
                f"Расчётная мощность на валу: {shaft_power:.2f} кВт\n"
                f"С запасом: {design_power:.2f} кВт\n"
                f"Рекомендуемый двигатель: {motor if motor else '>315'} кВт\n\n"
                f"МОТОР-РЕДУКТОР\n"
                f"Требуемое i: {ratio_req:.2f}\n"
                f"Ближайшее стандартное i: {ratio_std:g}\n"
                f"Фактические обороты: {rpm_real:.1f} об/мин\n"
                f"Ожидаемая производительность: {actual_capacity:.1f} т/ч\n"
                f"Крутящий момент: ≈ {torque:.0f} Н·м\n"
                f"Предварительный XLD: {xld_model}\n\n"
                f"Проверка длинного шнека должна дополнительно учитывать кручение, "
                f"прогиб, подвесные опоры и пуск под загрузкой."
            )
        except Exception:
            self.error()


class SpeedCalc(CalcPage):
    def __init__(self, **kwargs):
        super().__init__("Окружная скорость", "Для барабанов, шкивов, валов и рабочих органов.", **kwargs)
        self.d = self.add_field("Диаметр, м", "0.325")
        self.rpm = self.add_field("Обороты, об/мин", "60")
        self.add_calc_button("РАССЧИТАТЬ", self.calculate)
        self.result = self.add_result()

    def calculate(self, *_):
        try:
            d, rpm = f(self.d.input.text), f(self.rpm.input.text)
            if d <= 0 or rpm <= 0:
                raise ValueError

            v = math.pi * d * rpm / 60
            self.result.set_text(
                f"Окружная скорость: {v:.3f} м/с\n"
                f"Линейная скорость: {v*60:.2f} м/мин"
            )
        except Exception:
            self.error()


class AboutPage(CalcPage):
    def __init__(self, **kwargs):
        super().__init__("О программе", "", **kwargs)
        self.result = self.add_result()
        self.result.label.text = (
            "Инженерный калькулятор\n"
            f"Версия {APP_VERSION}\n\n"
            "Автор: Faxriddinov Azizbek\n"
            "Email: farhodkb@gmail.com\n"
            "Телефон: +998957774418\n\n"
            "Программа предназначена для предварительных инженерных расчётов "
            "вентиляторов, насосов, конвейеров, приводов, редукторов и шнеков.\n\n"
            "Результаты являются предварительными инженерными оценками. "
            "Перед изготовлением оборудования необходимо выполнить проверочные "
            "расчёты и свериться с паспортами выбранных компонентов."
        )


# -----------------------------
# ЭКРАНЫ
# -----------------------------
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(12))

        head = RoundedPanel(
            orientation="vertical",
            bg=PANEL,
            padding=dp(16),
            spacing=dp(4),
            size_hint_y=None,
            height=dp(108)
        )

        title = Label(
            text="ИНЖЕНЕРНЫЙ КАЛЬКУЛЯТОР",
            color=TEXT,
            bold=True,
            font_size=dp(23),
            halign="left",
            valign="middle"
        )
        title.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))
        head.add_widget(title)

        subtitle = Label(
            text="Быстрые расчёты оборудования",
            color=MUTED,
            font_size=dp(14),
            halign="left",
            valign="middle"
        )
        subtitle.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))
        head.add_widget(subtitle)

        root.add_widget(head)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(5))

        menu = GridLayout(
            cols=1,
            spacing=dp(9),
            padding=[0, dp(4), 0, dp(10)],
            size_hint_y=None
        )
        menu.bind(minimum_height=menu.setter("height"))

        sections = [
            ("Вентилятор", "fan"),
            ("Насос", "pump"),
            ("Ленточный конвейер", "conveyor"),
            ("Редуктор / привод", "drive"),
            ("Шкивы / звёздочки", "pulley"),
            ("Редукторы XLD", "xld"),
            ("Шнек AUTO", "screw"),
            ("Окружная скорость", "speed"),
            ("О программе", "about"),
        ]

        for text, screen_name in sections:
            btn = FlatButton(text=text, accent=(screen_name == "screw"))
            btn.bind(on_release=lambda btn, name=screen_name: self.open_screen(name))
            menu.add_widget(btn)

        scroll.add_widget(menu)
        root.add_widget(scroll)

        footer = Label(
            text=f"Версия {APP_VERSION}",
            color=MUTED,
            size_hint_y=None,
            height=dp(28),
            font_size=dp(12)
        )
        root.add_widget(footer)

        self.add_widget(root)

    def open_screen(self, name):
        self.manager.current = name


class CalcScreen(Screen):
    def __init__(self, page, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))

        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(8))

        back = FlatButton(text="‹  Меню", accent=False)
        back.size_hint_x = 0.32
        back.bind(on_release=lambda *_: self.go_home())
        top.add_widget(back)

        current = Label(
            text=page.body.children[-1].text if page.body.children else "",
            color=TEXT,
            bold=True,
            font_size=dp(16),
            halign="right",
            valign="middle"
        )
        current.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], val[1])))
        top.add_widget(current)

        root.add_widget(top)
        root.add_widget(page)

        self.add_widget(root)

    def go_home(self):
        self.manager.current = "home"


class EngineeringApp(App):
    def build(self):
        self.title = "Инженерный калькулятор"

        sm = ScreenManager()

        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(CalcScreen(FanCalc(), name="fan"))
        sm.add_widget(CalcScreen(PumpCalc(), name="pump"))
        sm.add_widget(CalcScreen(ConveyorCalc(), name="conveyor"))
        sm.add_widget(CalcScreen(DriveCalc(), name="drive"))
        sm.add_widget(CalcScreen(PulleyCalc(), name="pulley"))
        sm.add_widget(CalcScreen(XLDCalc(), name="xld"))
        sm.add_widget(CalcScreen(ScrewCalc(), name="screw"))
        sm.add_widget(CalcScreen(SpeedCalc(), name="speed"))
        sm.add_widget(CalcScreen(AboutPage(), name="about"))

        return sm


if __name__ == "__main__":
    EngineeringApp().run()
