from pixiboo import *
import time

try:
    import urandom as random
except ImportError:
    import random


WIDTH = 7
HEIGHT = 7
PLAYER_Y = HEIGHT - 1

APPLE_COLOR = (10, 20, 255)
PLAYER_COLOR = (160, 0, 250)
HEART_OUTLINE = PINK
HEART_FILL = (255, 170, 210)

def _randrange(n):
    try:
        return random.getrandbits(16) % n
    except Exception:
        return random.randrange(n)


def _randfloat():
    try:
        return random.getrandbits(16) / 65535
    except Exception:
        return random.random()


def draw_heart_outline():
    m.clear()
    for y, row in enumerate(HEART):
        for x, ch in enumerate(row):
            if ch != "1":
                continue
            is_edge = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx = x + dx
                ny = y + dy
                if nx < 0 or nx >= WIDTH or ny < 0 or ny >= HEIGHT:
                    is_edge = True
                    break
                if HEART[ny][nx] != "1":
                    is_edge = True
                    break
            m[y][x] = HEART_OUTLINE if is_edge else HEART_FILL
    m.show()


def play_startup():
    draw_heart_outline()
    e.off()
    b.play([(523, 80), (659, 80), (784, 120)])


def blink_left_eye():
    e.toggle_left()


def blink_right_eye():
    e.toggle_right()


def wait_for_center():
    # Track button states to debounce manually
    left_was_pressed = False
    right_was_pressed = False
    center_was_pressed = False
    
    while True:
        # Read current button states
        left_now = buttons.is_pressed("left")
        right_now = buttons.is_pressed("right")
        center_now = buttons.is_pressed("center")
        
        # Center button - exit when pressed
        if center_now and not center_was_pressed:
            # Wait for release
            while buttons.is_pressed("center"):
                time.sleep_ms(20)
            return
        center_was_pressed = center_now
        
        # Left button - toggle left eye
        if left_now and not left_was_pressed:
            e.toggle_left()
            time.sleep_ms(50)  # Small delay for tactile feedback
        left_was_pressed = left_now
        
        # Right button - toggle right eye
        if right_now and not right_was_pressed:
            e.toggle_right()
            time.sleep_ms(50)  # Small delay for tactile feedback
        right_was_pressed = right_now
        
        time.sleep_ms(30)


def render(player_x, apples):
    m.clear()
    for apple in apples:
        m[apple[1]][apple[0]] = APPLE_COLOR
    m[PLAYER_Y][player_x] = PLAYER_COLOR
    m.show()


def move_player(player_x):
    if buttons.left_pressed() and player_x > 0:
        b.play([(1600, 25)])
        return player_x - 1, True
    if buttons.right_pressed() and player_x < WIDTH - 1:
        b.play([(1600, 25)])
        return player_x + 1, True
    return player_x, False


def play_round(high_score):
    apples = []
    player_x = WIDTH // 2
    score = 0
    last_drop = time.ticks_ms()
    drop_interval = 600

    while True:
        player_x, moved = move_player(player_x)
        updated = moved

        now = time.ticks_ms()
        if time.ticks_diff(now, last_drop) >= drop_interval:
            last_drop = now

            if _randfloat() < 0.45:
                apples.append([_randrange(WIDTH), 0])

            next_apples = []
            for apple in apples:
                apple[1] += 1
                if apple[1] == PLAYER_Y and apple[0] == player_x:
                    b.play([(220, 200), (196, 220)])
                    return score, max(high_score, score)
                if apple[1] < HEIGHT:
                    next_apples.append(apple)
                else:
                    score += 1
                    b.play([(880, 40), (988, 40)])
            apples = next_apples

            drop_interval = max(150, 600 - score * 18)
            updated = True

        if updated:
            render(player_x, apples)
        time.sleep_ms(50)


def show_high_score(high_score):
    m.clear()
    m.display("HI", PINK, 450)
    m.display(str(high_score), PURPLE, 450)


def play_tetris_song():
    # Tetris theme (Korobeiniki)
    
    # Visual: show a rotating pattern while playing
    tetris_pattern = [
        [1, 1, 0, 0, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0],
        [0, 0, 0, 0, 1, 1, 0],
        [0, 0, 0, 0, 0, 1, 1],
        [0, 0, 0, 0, 0, 0, 1],
    ]
    
    # Rainbow colors to cycle through
    rainbow_colors = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, PINK]
    
    # Tetris melody (frequencies and durations in ms)
    melody = [
        # Main theme part 1
        (659, 400), (494, 200), (523, 200), (587, 400), (523, 200), (494, 200),
        (440, 400), (440, 200), (523, 200), (659, 400), (587, 200), (523, 200),
        (494, 600), (523, 200), (587, 400), (659, 400),
        (523, 400), (440, 400), (440, 400), (0, 200),
        # Part 2
        (587, 400), (698, 200), (880, 400), (784, 200), (698, 200),
        (659, 600), (523, 200), (659, 400), (587, 200), (523, 200),
        (494, 400), (494, 200), (523, 200), (587, 400), (659, 400),
        (523, 400), (440, 400), (440, 400), (0, 400),
    ]
    
    m.clear()
    m.show()
    
    # Get direct PWM control
    try:
        from machine import PWM, Pin
        from pixiboo.hardware import BUZZER_PIN
        pwm = PWM(Pin(BUZZER_PIN))
    except:
        # Fallback if PWM fails
        m.display("ERR", RED, 400)
        return
    
    # Play melody with visual effect
    for note_idx, (freq, duration) in enumerate(melody):
        # Update visual every 4 notes
        if note_idx % 4 == 0:
            m.clear()
            shift = (note_idx // 4) % 7
            color_idx = (note_idx // 4) % len(rainbow_colors)
            color = rainbow_colors[color_idx]
            
            for y in range(7):
                for x in range(7):
                    if tetris_pattern[y][(x + shift) % 7]:
                        m[y][x] = color
            m.show()
        
        # Play note
        if freq > 0:
            pwm.freq(freq)
            pwm.duty(512)
            time.sleep_ms(duration - 20)
            pwm.duty(0)
            time.sleep_ms(20)  # Small gap between notes
        else:
            pwm.duty(0)
            time.sleep_ms(duration)
    
    # Stop buzzer
    pwm.duty(0)
    
    # Clear display at end
    m.clear()
    m.show()
    time.sleep_ms(1000)


def main():
    set_brightness(0.7)
    high_score = 0
    mode = 0

    while True:
        if mode == 0:
            play_startup()
            wait_for_center()
            mode = 1
        elif mode == 1:
            score, high_score = play_round(high_score)
            show_high_score(high_score)
            wait_for_center()
            mode = 2
        else:
            play_tetris_song()
            mode = 0


main()
