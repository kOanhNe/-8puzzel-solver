import pygame
import time
import heapq
from collections import deque
import sys
import random
import math

# ========================== Cấu hình Pygame ==========================
pygame.init()

WIDTH, HEIGHT = 1200, 800
TREE_WIDTH, TREE_HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Trình Giải 8-Puzzle")
tree_screen = None

GRID_SIZE = 3
TILE_SIZE = min(WIDTH, HEIGHT) // 10
MARGIN = 20
grid_y = HEIGHT // 4  # Thêm dòng này

# Font Times New Roman cho tất cả
TITLE_FONT = pygame.font.Font(pygame.font.match_font("timesnewroman") or None, 36)
SUBTITLE_FONT = pygame.font.Font(pygame.font.match_font("timesnewroman") or None, 14)
MENU_FONT = pygame.font.Font(pygame.font.match_font("timesnewroman") or None, 16)
MESSAGE_FONT = pygame.font.Font(pygame.font.match_font("timesnewroman") or None, 12)
TREE_FONT = pygame.font.Font(pygame.font.match_font("timesnewroman") or None, 14)
MINI_FONT = pygame.font.Font(pygame.font.match_font("timesnewroman") or None, 12)

# Bảng màu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CALM_BLUE = (100, 130, 180)
LIGHT_CALM = (130, 160, 200)
OCEAN_BLUE = (50, 110, 160)
LIGHT_OCEAN = (80, 140, 190)
FOREST_GREEN = (40, 130, 90)
LIGHT_FOREST = (70, 160, 120)
SUNSET_ORANGE = (180, 110, 60)
LIGHT_SUNSET = (200, 140, 90)
CORAL_RED = (180, 60, 60)
LIGHT_CORAL = (200, 90, 90)
SILVER = (160, 160, 160)
DARK_SILVER = (130, 130, 130)
SHADOW = (100, 100, 100, 100)
MESSAGE_COLOR = (30, 80, 130)
YELLOW = (255, 215, 0)

# FPS để kiểm soát tốc độ khung hình
FPS = 60

# ========================== Trạng thái bài toán ==========================
initial_state = [[2, 6, 5], ['_', 8, 7], [4, 3, 1]]
sorted_state = [row[:] for row in initial_state]
goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, '_']]

MOVES = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
ALGORITHMS = [
    "BFS", "DFS", "A*", "Greedy", "UCS", "IDA*", "ID",
    "Steepest Hill", "Simple Hill", "Stochastic Hill", "Simulated Annealing",
    "AO*", "Search with No Observation", "Backtracking", "Partially Observable",
    "Q-Learning" ]
selected_algorithm = None
algorithm_selected = None
manual_mode = False
input_mode = False
input_state = [['' for _ in range(3)] for _ in range(3)]
input_pos = (0, 0)
paused = False
animating = False
animation_start = None
animation_start_pos = None
animation_end_pos = None
animation_tile = None
animation_duration = 0.5
tree_nodes = []
tree_edges = []
node_positions = {}
max_nodes_to_display = 50
tree_scale = 1.0
distance_cache = {}
button_pressed = None
animation_speed = 30
animation_frames = []
current_frame = 0
auto_play = False
path_steps = []
current_step = 0
show_solution = False
backtracking_mode = False
partially_observable_mode = False
belief_state = []
statistics = {
    "nodes_expanded": 0,
    "max_depth": 0,
    "solution_length": 0,
    "elapsed_time": 0
}
confirmation_message = None
confirmation_start_time = None
input_phase = "initial"  # "initial" để nhập trạng thái ban đầu, "goal" để nhập trạng thái mục tiêu, None khi không nhập
# ========================== Các hàm hỗ trợ ==========================
def resize_layout():
    global TILE_SIZE, WIDTH, HEIGHT
    WIDTH, HEIGHT = screen.get_size()
    TILE_SIZE = min(WIDTH // 4, HEIGHT // 5) // GRID_SIZE
    return create_buttons()

def state_to_tuple(state):
    return tuple(tuple(row) for row in state)

def state_to_list(state):
    return [x for row in state for x in row]

def list_to_state(lst):
    return [[lst[i * 3 + j] for j in range(3)] for i in range(3)]

def normalize_state(state):
    """Convert any 9 to '_' and ensure all numbers are integers."""
    new_state = [row[:] for row in state]
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if new_state[i][j] == 9:
                new_state[i][j] = '_'
            elif isinstance(new_state[i][j], str) and new_state[i][j].isdigit():
                new_state[i][j] = int(new_state[i][j])
    return new_state

def find_empty_tile(state):
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if state[i][j] in ['_', 9]:
                return i, j
    return None

def is_valid_move(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

def move(state, direction):
    state = normalize_state(state)
    empty_pos = find_empty_tile(state)
    if empty_pos is None:
        return None, None, None
    x, y = empty_pos
    dx, dy = MOVES[direction]
    nx, ny = x + dx, y + dy
    if is_valid_move(nx, ny):
        new_state = [row[:] for row in state]
        new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
        return new_state, (nx, ny), new_state[x][y]
    return None, None, None

def manhattan_distance(state, goal):
    state = normalize_state(state)
    state_tuple = state_to_tuple(state)
    if state_tuple in distance_cache:
        return distance_cache[state_tuple]
    distance = 0
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if state[i][j] != '_':
                value = state[i][j]
                if not isinstance(value, int):
                    value = int(value) if value.isdigit() else value
                for gi in range(GRID_SIZE):
                    for gj in range(GRID_SIZE):
                        if goal[gi][gj] == value:
                            distance += abs(i - gi) + abs(j - gj)
                            break
    distance_cache[state_tuple] = distance
    return distance

def get_inversions(state):
    state = normalize_state(state)
    flat = [x for row in state for x in row if x != '_']
    inversions = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] > flat[j]:
                inversions += 1
    return inversions

def is_solvable(start, goal):
    start = normalize_state(start)
    goal = normalize_state(goal)
    return get_inversions(start) % 2 == get_inversions(goal) % 2

def is_valid_state(state):
    state = normalize_state(state)
    flat = [x for row in state for x in row]
    numbers = [x for x in flat if x != '_']
    return (len(numbers) == 8 and 
            all(isinstance(x, int) for x in numbers) and 
            set(numbers) == set(range(1, 9)) and 
            '_' in flat)

def ease_in_out(t):
    return t * t * (3 - 2 * t)

def draw_shadow(surface, rect, offset=3):
    shadow_rect = pygame.Rect(rect.x + offset, rect.y + offset, rect.width, rect.height)
    pygame.draw.rect(surface, SHADOW, shadow_rect)

def draw_state(screen, state, x_offset, y_offset, title, animate_pos=None, scale=1.0):
    state = normalize_state(state)
    
    # Vẽ tiêu đề căn giữa với lưới
    title_text = SUBTITLE_FONT.render(title, True, BLACK)
    title_rect = title_text.get_rect(center=(x_offset + (GRID_SIZE * TILE_SIZE * scale) // 2, y_offset - 35))
    screen.blit(title_text, title_rect)
    
    # Tính toán kích thước thực tế của ô
    cell_size = int(TILE_SIZE * scale)
    
    # Vẽ lưới nền
    grid_rect = pygame.Rect(x_offset - 5, y_offset - 5, 
                          GRID_SIZE * cell_size + 10, 
                          GRID_SIZE * cell_size + 10)
    draw_shadow(screen, grid_rect)
    
    # Vẽ từng ô
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if animate_pos and (i, j) == animate_pos:
                continue
                
            value = state[i][j]
            x = x_offset + j * cell_size
            y = y_offset + i * cell_size
            rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)
            
            # Vẽ nền ô
            pygame.draw.rect(screen, SILVER if value == '_' else CALM_BLUE, rect)
            
            # Vẽ số
            if value != '_':
                font = MINI_FONT if scale < 1.0 else MENU_FONT
                text = font.render(str(value), True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
            
            pygame.draw.rect(screen, BLACK, rect, 2)
    
    # Vẽ ô đang animation  
    if animate_pos and animation_start is not None:
        i, j = animate_pos
        value = animation_tile
        t = (time.time() - animation_start) / animation_duration
        
        if t >= 1:
            return False
            
        t = ease_in_out(t)
        start_x, start_y = animation_start_pos 
        end_x, end_y = animation_end_pos
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t
        
        rect = pygame.Rect(x, y, cell_size - 2, cell_size - 2)
        pygame.draw.rect(screen, CALM_BLUE, rect)
        
        if value != '_':
            font = MINI_FONT if scale < 1.0 else MENU_FONT
            text = font.render(str(value), True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)
            
        pygame.draw.rect(screen, BLACK, rect, 2)
        
    return True

def draw_input_state(screen, state, x_offset, y_offset, title, active_pos):
    # Vẽ tiêu đề
    title_text = SUBTITLE_FONT.render(title, True, BLACK)
    title_rect = title_text.get_rect(center=(x_offset + (GRID_SIZE * TILE_SIZE) // 2, y_offset - 35))
    screen.blit(title_text, title_rect)
    
    # Vẽ lưới nền
    grid_rect = pygame.Rect(x_offset - 5, y_offset - 5,
                          GRID_SIZE * TILE_SIZE + 10,
                          GRID_SIZE * TILE_SIZE + 10)
    draw_shadow(screen, grid_rect)
    
    # Vẽ từng ô
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            rect = pygame.Rect(x_offset + j * TILE_SIZE,
                             y_offset + i * TILE_SIZE,
                             TILE_SIZE - 2,
                             TILE_SIZE - 2)
                             
            # Đổi màu ô đang active
            color = FOREST_GREEN if (i, j) == active_pos else CALM_BLUE
            pygame.draw.rect(screen, color, rect)
            
            # Vẽ số đã nhập
            value = state[i][j]
            if value != '':  # Sửa điều kiện kiểm tra giá trị
                text = MENU_FONT.render(str(value), True, BLACK)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
                
            pygame.draw.rect(screen, BLACK, rect, 2)

def draw_belief_state(screen, belief_state, x_offset, y_offset):
    if partially_observable_mode and belief_state:
        belief_str = "Belief State:\n"
        for i, state in enumerate(belief_state[:3]):
            belief_str += f"State {i+1}:\n"
            for row in state:
                belief_str += " ".join(str(x) for x in row) + "\n"
        belief_text = MESSAGE_FONT.render(belief_str, True, MESSAGE_COLOR)
        screen.blit(belief_text, (x_offset, y_offset))

def create_buttons():
    buttons = []
    button_width = 120
    button_height = 40

    start_x = (WIDTH - (button_width * 3 + 40)) // 2
    menu_y = HEIGHT - 300
    manual_rect = pygame.Rect(start_x, menu_y, button_width, button_height)
    buttons.append((manual_rect, "Chế Độ Thủ Công"))
    input_rect = pygame.Rect(start_x + button_width + 20, menu_y, button_width, button_height)
    buttons.append((input_rect, "Nhập Trạng Thái"))
    play_rect = pygame.Rect(start_x + 2 * (button_width + 20), menu_y, button_width, button_height)
    buttons.append((play_rect, "Play"))

    # Thêm nút Xác Nhận khi đang nhập trạng thái
    if input_mode:
        confirm_rect = pygame.Rect(start_x + button_width + 20, menu_y + button_height + 15, button_width, button_height)
        buttons.append((confirm_rect, "Xác Nhận"))

    algo_start_y = HEIGHT - 240
    algo_per_row = 4
    for idx, algo in enumerate(ALGORITHMS):
        row = idx // algo_per_row
        col = idx % algo_per_row
        algo_rect = pygame.Rect(
            (WIDTH - (button_width * algo_per_row + 20 * (algo_per_row - 1))) // 2 + col * (button_width + 20),
            algo_start_y + row * (button_height + 15),
            button_width,
            button_height
        )
        buttons.append((algo_rect, algo))

    reset_rect = pygame.Rect(WIDTH - 200, HEIGHT - 50, button_width, button_height)
    buttons.append((reset_rect, "Đặt Lại"))
    pause_rect = pygame.Rect(WIDTH - 400, HEIGHT - 50, button_width, button_height)
    buttons.append((pause_rect, "Tạm Dừng"))
    return buttons

def draw_menu(screen, initial, sorted_s, goal, message, buttons, input_mode=False, show_reset=False, mouse_pos=None):
    screen.fill(WHITE)
    
    title_text = TITLE_FONT.render("Trình Giải 8-Puzzle", True, BLACK)
    title_rect = title_text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(title_text, title_rect)
    
    # Sửa cách tính vị trí các lưới
    total_width = 3 * (GRID_SIZE * TILE_SIZE)  # Tổng độ rộng của 3 lưới
    spacing = TILE_SIZE * 2  # Khoảng cách giữa các lưới
    total_width_with_spacing = total_width + 2 * spacing  # Tổng độ rộng bao gồm khoảng cách
    start_x = (WIDTH - total_width_with_spacing) // 2  # Điểm bắt đầu để căn giữa
    
    if input_mode:
        if input_phase == "initial":
            draw_input_state(screen, input_state, start_x + GRID_SIZE * TILE_SIZE + spacing, grid_y, "Nhập Trạng Thái Ban Đầu", input_pos)
        elif input_phase == "goal":
            draw_input_state(screen, input_state, start_x + 2 * (GRID_SIZE * TILE_SIZE + spacing), grid_y, "Nhập Trạng Thái Mục Tiêu", input_pos)
    else:
        draw_state(screen, initial, start_x, grid_y, "Trạng Thái Ban Đầu")
        draw_state(screen, sorted_s, start_x + GRID_SIZE * TILE_SIZE + spacing, grid_y, "Trạng Thái Đang Sắp Xếp")
        draw_state(screen, goal, start_x + 2 * (GRID_SIZE * TILE_SIZE + spacing), grid_y, "Trạng Thái Mục Tiêu")
    
    algo_text = MESSAGE_FONT.render(message, True, MESSAGE_COLOR)
    algo_rect = algo_text.get_rect(center=(WIDTH // 2, grid_y - 70))
    screen.blit(algo_text, algo_rect)
    
    stats_text = MESSAGE_FONT.render(
        f"Thống kê: Nút đã mở: {statistics['nodes_expanded']} | Độ sâu tối đa: {statistics['max_depth']} | "
        f"Độ dài lời giải: {statistics['solution_length']} | Thời gian: {statistics['elapsed_time']:.2f}s",
        True, MESSAGE_COLOR
    )
    screen.blit(stats_text, (50, HEIGHT - 30))
    
    draw_belief_state(screen, belief_state, WIDTH - 300, HEIGHT - 320)
    
    if confirmation_message and (time.time() - confirmation_start_time) < 3:
        confirm_text = MESSAGE_FONT.render(confirmation_message, True, FOREST_GREEN)
        confirm_rect = confirm_text.get_rect(center=(WIDTH // 2, HEIGHT - 340))
        screen.blit(confirm_text, confirm_rect)
    
    for rect, label in buttons:
        if label == "Đặt Lại" and not show_reset:
            continue
        if label == "Chế Độ Thủ Công":
            base_color, light_color = FOREST_GREEN if manual_mode else OCEAN_BLUE, LIGHT_FOREST if manual_mode else LIGHT_OCEAN
        elif label == "Nhập Trạng Thái":
            base_color, light_color = SUNSET_ORANGE, LIGHT_SUNSET
        elif label == "Đặt Lại":
            base_color, light_color = CORAL_RED, LIGHT_CORAL
        elif label == "Tạm Dừng":
            base_color, light_color = CORAL_RED if paused else FOREST_GREEN, LIGHT_CORAL if paused else LIGHT_FOREST
        elif label == "Play":
            base_color, light_color = FOREST_GREEN if algorithm_selected else SILVER, LIGHT_FOREST if algorithm_selected else DARK_SILVER
        elif label == "Xác Nhận":
            base_color, light_color = FOREST_GREEN, LIGHT_FOREST
        else:
            base_color, light_color = OCEAN_BLUE, LIGHT_OCEAN
        
        if mouse_pos and rect.collidepoint(mouse_pos):
            base_color = light_color
            light_color = (min(255, base_color[0] + 20), min(255, base_color[1] + 20), min(255, base_color[2] + 20))
        
        draw_rect = rect
        if button_pressed == label:
            base_color = (max(0, base_color[0] - 20), max(0, base_color[1] - 20), max(0, base_color[2] - 20))
            light_color = base_color
            draw_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
        
        draw_shadow(screen, rect)
        pygame.draw.rect(screen, base_color, draw_rect)
        text = MENU_FONT.render(label, True, WHITE)
        text_rect = text.get_rect(center=draw_rect.center)
        screen.blit(text, text_rect)
        if mouse_pos and rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, LIGHT_OCEAN, draw_rect, 2)
    
    pygame.display.flip()
    return buttons[-2][0] if show_reset else None

def draw_tree(screen):
    screen.fill(WHITE)
    node_radius = 20 * tree_scale
    mini_grid_size = 30 * tree_scale
    
    back_rect = pygame.Rect(10, 10, 100, 40)
    pygame.draw.rect(screen, CORAL_RED, back_rect)
    back_text = MENU_FONT.render("Quay Lại", True, WHITE)
    back_text_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, back_text_rect)
    pygame.draw.rect(screen, BLACK, back_rect, 2)
    
    for edge in tree_edges:
        parent_id, child_id, move = edge
        if parent_id in node_positions and child_id in node_positions:
            start_pos = node_positions[parent_id]
            end_pos = node_positions[child_id]
            pygame.draw.line(screen, BLACK, start_pos, end_pos, 2)
            mid_pos = ((start_pos[0] + end_pos[0]) // 2, (start_pos[1] + end_pos[1]) // 2)
            text = TREE_FONT.render(move, True, BLACK)
            screen.blit(text, mid_pos)
    
    for node_id, pos in node_positions.items():
        color = YELLOW if node_id in [n[0] for n in tree_nodes if n[1].solved] else CALM_BLUE
        pygame.draw.circle(screen, color, pos, node_radius)
        pygame.draw.circle(screen, BLACK, pos, node_radius, 2)
        text = TREE_FONT.render(str(node_id), True, BLACK)
        text_rect = text.get_rect(center=(pos[0], pos[1] - node_radius - 10))
        screen.blit(text, text_rect)
        
        for _, node in tree_nodes:
            if node.node_id == node_id:
                draw_state(screen, node.state, pos[0] + node_radius + 5, pos[1] - mini_grid_size * 1.5, "", scale=0.3)
                break
    
    pygame.display.flip()
    return back_rect

def update_belief(belief, action_state):
    action_state = normalize_state(action_state)
    new_belief = []
    for state in belief:
        state = normalize_state(state)
        for move_name in MOVES:
            new_state, _, _ = move(state, move_name)
            if new_state and state_to_tuple(new_state) == state_to_tuple(action_state):
                new_belief.append(normalize_state(new_state))
    return new_belief if new_belief else belief

# ========================== Các thuật toán ==========================
def bfs(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    queue = deque([(start, [])])
    visited = {state_to_tuple(start)}
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    while queue and (partial_steps == float('inf') or len(queue[0][1]) < partial_steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(queue[0][1]) if queue else 0,
                "elapsed_time": time.time() - start_time
            })
            return queue[0][1] if queue else []
        state, path = queue.popleft()
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        if state == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        for move_name in MOVES:
            new_state, _, _ = move(state, move_name)
            if new_state and state_to_tuple(new_state) not in visited:
                visited.add(state_to_tuple(new_state))
                new_path = path + [move_name]
                queue.append((new_state, new_path))
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(queue[0][1]) if queue else 0,
        "elapsed_time": time.time() - start_time
    })
    return queue[0][1] if queue else []

def dfs(start, goal, max_depth_limit=float('inf'), partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    stack = [(start, [])]
    visited = {state_to_tuple(start)}
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    while stack and (partial_steps == float('inf') or len(stack[-1][1]) < partial_steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(stack[-1][1]) if stack else 0,
                "elapsed_time": time.time() - start_time
            })
            return stack[-1][1] if stack else []
        state, path = stack.pop()
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        if state == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        if len(path) < max_depth_limit:
            for move_name in MOVES:
                new_state, _, _ = move(state, move_name)
                if new_state and state_to_tuple(new_state) not in visited:
                    visited.add(state_to_tuple(new_state))
                    new_path = path + [move_name]
                    stack.append((new_state, new_path))
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(stack[-1][1]) if stack else 0,
        "elapsed_time": time.time() - start_time
    })
    return stack[-1][1] if stack else []

def ucs(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    # Thêm id để đảm bảo tính duy nhất khi so sánh
    node_id = 0
    pq = [(0, node_id, start, [])]  # (cost, node_id, state, path)
    visited = {state_to_tuple(start): 0}  # Lưu chi phí nhỏ nhất đến trạng thái
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    while pq and (partial_steps == float('inf') or len(pq[0][3]) < partial_steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(pq[0][3]) if pq else 0,
                "elapsed_time": time.time() - start_time
            })
            return pq[0][3] if pq else []
        cost, _, state, path = heapq.heappop(pq)
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        if state == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        state_tuple = state_to_tuple(state)
        if cost <= visited.get(state_tuple, float('inf')):
            for move_name in MOVES:
                new_state, _, _ = move(state, move_name)
                if new_state:
                    new_cost = cost + 1
                    new_state_tuple = state_to_tuple(new_state)
                    if new_state_tuple not in visited or new_cost < visited[new_state_tuple]:
                        visited[new_state_tuple] = new_cost
                        new_path = path + [move_name]
                        node_id += 1
                        heapq.heappush(pq, (new_cost, node_id, new_state, new_path))
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(pq[0][3]) if pq else 0,
        "elapsed_time": time.time() - start_time
    })
    return pq[0][3] if pq else []

def a_star(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    node_id = 0
    pq = [(manhattan_distance(start, goal), 0, node_id, start, [])]  # (f, g, node_id, state, path)
    visited = {state_to_tuple(start): 0}
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    while pq and (partial_steps == float('inf') or len(pq[0][4]) < partial_steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(pq[0][4]) if pq else 0,
                "elapsed_time": time.time() - start_time
            })
            return pq[0][4] if pq else []
        f, g, _, state, path = heapq.heappop(pq)
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        if state == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        state_tuple = state_to_tuple(state)
        if g <= visited.get(state_tuple, float('inf')):
            for move_name in MOVES:
                new_state, _, _ = move(state, move_name)
                if new_state:
                    new_g = g + 1
                    new_state_tuple = state_to_tuple(new_state)
                    if new_state_tuple not in visited or new_g < visited[new_state_tuple]:
                        visited[new_state_tuple] = new_g
                        h = manhattan_distance(new_state, goal)
                        new_path = path + [move_name]
                        node_id += 1
                        heapq.heappush(pq, (new_g + h, new_g, node_id, new_state, new_path))
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(pq[0][4]) if pq else 0,
        "elapsed_time": time.time() - start_time
    })
    return pq[0][4] if pq else []

def greedy(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    node_id = 0
    pq = [(manhattan_distance(start, goal), node_id, start, [])]  # (h, node_id, state, path)
    visited = {state_to_tuple(start)}
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    while pq and (partial_steps == float('inf') or len(pq[0][3]) < partial_steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(pq[0][3]) if pq else 0,
                "elapsed_time": time.time() - start_time
            })
            return pq[0][3] if pq else []
        h, _, state, path = heapq.heappop(pq)
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        if state == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        for move_name in MOVES:
            new_state, _, _ = move(state, move_name)
            if new_state and state_to_tuple(new_state) not in visited:
                visited.add(state_to_tuple(new_state))
                new_path = path + [move_name]
                node_id += 1
                heapq.heappush(pq, (manhattan_distance(new_state, goal), node_id, new_state, new_path))
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(pq[0][3]) if pq else 0,
        "elapsed_time": time.time() - start_time
    })
    return pq[0][3] if pq else []

def ida_star(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    def dfs(state, path, g, threshold, visited):
        f = g + manhattan_distance(state, goal)
        if f > threshold:
            return f
        if state == goal:
            return path
        min_cost = float('inf')
        for move_name in MOVES:
            new_state, _, _ = move(state, move_name)
            if new_state and state_to_tuple(new_state) not in visited:
                visited.add(state_to_tuple(new_state))
                result = dfs(new_state, path + [move_name], g + 1, threshold, visited)
                visited.remove(state_to_tuple(new_state))
                if isinstance(result, list):
                    return result
                min_cost = min(min_cost, result)
        return min_cost

    threshold = manhattan_distance(start, goal)
    visited = {state_to_tuple(start)}
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    while partial_steps == float('inf') or len(visited) < partial_steps:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": 0,
                "elapsed_time": time.time() - start_time
            })
            return []
        result = dfs(start, [], 0, threshold, visited)
        nodes_expanded += len(visited)
        max_depth = max(max_depth, len(visited))
        if isinstance(result, list):
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(result),
                "elapsed_time": time.time() - start_time
            })
            return result
        if result == float('inf'):
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": 0,
                "elapsed_time": time.time() - start_time
            })
            return []
        threshold = result
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": 0,
        "elapsed_time": time.time() - start_time
    })
    return []

def iterative_deepening(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    
    if not is_solvable(start, goal):
        statistics.update({
            "nodes_expanded": 0,
            "max_depth": 0,
            "solution_length": 0,
            "elapsed_time": 0
        })
        print("Trạng thái không thể giải được!")
        return []

    def dfs_limited(state, depth, limit, visited):
        if depth > limit:
            return None
            
        if state == goal:
            return []
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        if paused:
            return "PAUSED"
            
        for move_name in MOVES:
            new_state, _, _ = move(state, move_name)
            if new_state and state_to_tuple(new_state) not in visited:
                visited.add(state_to_tuple(new_state))
                result = dfs_limited(new_state, depth + 1, limit, visited)
                visited.remove(state_to_tuple(new_state))
                
                if result == "PAUSED":
                    return "PAUSED"
                    
                if result is not None:
                    return [move_name] + result
                    
        return None

    nodes_expanded = 0
    max_depth = 0 
    start_time = time.time()
    
    # Tăng giới hạn độ sâu tối đa lên 10000
    max_depth_limit = 10000
    current_moves = []

    print(f"Bắt đầu tìm kiếm với độ sâu tối đa {max_depth_limit}...")
    
    for depth in range(max_depth_limit + 1):
        # In thông báo mỗi 100 độ sâu
        if depth % 100 == 0:
            print(f"Đang tìm kiếm ở độ sâu {depth}...")
            
        visited = {state_to_tuple(start)}
        result = dfs_limited(start, 0, depth, visited)
        nodes_expanded += len(visited)
        max_depth = max(max_depth, depth)
        
        if result == "PAUSED":
            print("Tạm dừng tìm kiếm...")
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(current_moves),
                "elapsed_time": time.time() - start_time
            })
            return current_moves
            
        if result is not None:
            print(f"Đã tìm thấy lời giải ở độ sâu {depth}!")
            current_moves = result
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(current_moves),
                "elapsed_time": time.time() - start_time
            })
            return current_moves
            
        # Kiểm tra thời gian chạy
        elapsed_time = time.time() - start_time
        if elapsed_time > 60:  # Tăng giới hạn thời gian lên 60 giây
            print(f"Đã vượt quá thời gian khi tìm kiếm ở độ sâu {depth}")
            if len(current_moves) > 0:
                print("Trả về lời giải tốt nhất đã tìm được")
                return current_moves
            break

    # Nếu không tìm thấy lời giải
    print(f"Không tìm thấy lời giải trong giới hạn độ sâu {max_depth_limit}!")
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": 0,
        "elapsed_time": time.time() - start_time
    })
    return []  # Trả về rỗng để thông báo không tìm thấy lời giải

def steepest_hill_climbing(start, goal, restarts=10, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    best_solution = []
    best_h = float('inf')
    
    def get_all_moves(state):
        moves = []
        for move_name in MOVES:
            new_state, _, _ = move(state, move_name) 
            if new_state:
                h = manhattan_distance(new_state, goal)
                moves.append((h, new_state, move_name))
        # Sắp xếp theo giá trị heuristic (phần tử đầu tiên của tuple)
        return sorted(moves, key=lambda x: x[0])
    
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    for _ in range(restarts):
        current = start
        current_path = []
        visited = {state_to_tuple(start)}
        steps_without_improvement = 0
        
        while len(current_path) < partial_steps and steps_without_improvement < 10:
            if current == goal:
                statistics.update({
                    "nodes_expanded": nodes_expanded,
                    "max_depth": max_depth,
                    "solution_length": len(current_path),
                    "elapsed_time": time.time() - start_time
                })
                return current_path
                
            nodes_expanded += 1
            max_depth = max(max_depth, len(current_path))
            
            moves = get_all_moves(current)
            found_better = False
            
            for h, next_state, move_name in moves:
                if state_to_tuple(next_state) not in visited and h < manhattan_distance(current, goal):
                    current = next_state
                    current_path.append(move_name)
                    visited.add(state_to_tuple(next_state))
                    found_better = True
                    steps_without_improvement = 0
                    break
                    
            if not found_better:
                steps_without_improvement += 1
                if steps_without_improvement >= 10:
                    # Try random valid move when stuck
                    valid_moves = [(s, m) for _, s, m in moves if state_to_tuple(s) not in visited]
                    if valid_moves:
                        next_state, move_name = random.choice(valid_moves)
                        current = next_state
                        current_path.append(move_name)
                        visited.add(state_to_tuple(current))
                        steps_without_improvement = 0
            
            if current == goal:
                if len(current_path) < len(best_solution) or not best_solution:
                    best_solution = current_path[:]
                break
                
        if len(current_path) < len(best_solution) or not best_solution:
            best_solution = current_path[:]
            best_h = manhattan_distance(current, goal)
    
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth, 
        "solution_length": len(best_solution),
        "elapsed_time": time.time() - start_time
    })
    return best_solution

def simple_hill_climbing(start, goal, restarts=10, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    best_solution = []
    best_h = float('inf')
    
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    for _ in range(restarts):
        current = start
        current_path = []
        visited = {state_to_tuple(start)}
        steps_without_improvement = 0
        
        while len(current_path) < partial_steps and steps_without_improvement < 10:
            if current == goal:
                statistics.update({
                    "nodes_expanded": nodes_expanded,
                    "max_depth": max_depth,
                    "solution_length": len(current_path),
                    "elapsed_time": time.time() - start_time
                })
                return current_path
            
            nodes_expanded += 1
            max_depth = max(max_depth, len(current_path))
            current_h = manhattan_distance(current, goal)
            best_neighbor = None
            best_move = None
            best_neighbor_h = float('inf')
            
            # Check all possible moves
            for move_name in MOVES:
                new_state, _, _ = move(current, move_name)
                if new_state and state_to_tuple(new_state) not in visited:
                    h = manhattan_distance(new_state, goal)
                    if h < best_neighbor_h:
                        best_neighbor = new_state
                        best_move = move_name
                        best_neighbor_h = h
            
            if best_neighbor and best_neighbor_h <= current_h:
                current = best_neighbor
                current_path.append(best_move)
                visited.add(state_to_tuple(current))
                steps_without_improvement = 0
            else:
                steps_without_improvement += 1
                if steps_without_improvement >= 10:
                    # Try random move when stuck
                    valid_moves = []
                    for move_name in MOVES:
                        new_state, _, _ = move(current, move_name)
                        if new_state and state_to_tuple(new_state) not in visited:
                            valid_moves.append((new_state, move_name))
                    
                    if valid_moves:
                        next_state, move_name = random.choice(valid_moves)
                        current = next_state
                        current_path.append(move_name)
                        visited.add(state_to_tuple(current))
                        steps_without_improvement = 0
            
            if current == goal:
                if len(current_path) < len(best_solution) or not best_solution:
                    best_solution = current_path[:]
                break
                
        if len(current_path) < len(best_solution) or not best_solution:
            best_solution = current_path[:]
            best_h = manhattan_distance(current, goal)
    
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(best_solution),
        "elapsed_time": time.time() - start_time
    })
    return best_solution

def stochastic_hill_climbing(start, goal, restarts=10, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    best_solution = []
    best_h = float('inf')
    
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    def calculate_probability(delta, temp):
        # Prevent overflow by capping the exponent
        try:
            if delta > 700:  # Large positive difference
                return 0.0
            elif delta < -700:  # Large negative difference
                return 1.0
            else:
                return math.exp(delta / temp)
        except OverflowError:
            return 0.0 if delta > 0 else 1.0
    
    for _ in range(restarts):
        current = start
        current_path = []
        visited = {state_to_tuple(start)}
        steps_without_improvement = 0
        temperature = 1.0
        
        while len(current_path) < partial_steps and steps_without_improvement < 10:
            if current == goal:
                statistics.update({
                    "nodes_expanded": nodes_expanded,
                    "max_depth": max_depth,
                    "solution_length": len(current_path),
                    "elapsed_time": time.time() - start_time
                })
                return current_path
            
            nodes_expanded += 1
            max_depth = max(max_depth, len(current_path))
            current_h = manhattan_distance(current, goal)
            
            # Get all valid neighbors
            neighbors = []
            for move_name in MOVES:
                new_state, _, _ = move(current, move_name)
                if new_state and state_to_tuple(new_state) not in visited:
                    h = manhattan_distance(new_state, goal)
                    # Calculate probability with bounds checking
                    prob = calculate_probability(current_h - h, temperature)
                    neighbors.append((new_state, move_name, h, prob))
            
            if not neighbors:
                steps_without_improvement += 1
                if steps_without_improvement >= 10:
                    break
                continue
            
            # Normalize probabilities if needed
            total_prob = sum(n[3] for n in neighbors)
            if total_prob == 0:
                # If all probabilities are 0, choose randomly
                next_state, move_name, h, _ = random.choice(neighbors)
            else:
                # Use normalized probabilities
                r = random.uniform(0, total_prob)
                cumsum = 0
                for state, move_name, h, prob in neighbors:
                    cumsum += prob
                    if cumsum >= r:
                        next_state, move_name, h = state, move_name, h
                        break
                else:
                    next_state, move_name, h, _ = neighbors[-1]
            
            current = next_state
            current_path.append(move_name)
            visited.add(state_to_tuple(current))
            
            if h < current_h:
                steps_without_improvement = 0
            else:
                steps_without_improvement += 1
            
            # Cool down more gradually
            temperature = max(0.1, temperature * 0.95)
            
            if current == goal:
                if len(current_path) < len(best_solution) or not best_solution:
                    best_solution = current_path[:]
                break
        
        if len(current_path) < len(best_solution) or not best_solution:
            best_solution = current_path[:]
            best_h = manhattan_distance(current, goal)
    
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(best_solution),
        "elapsed_time": time.time() - start_time
    })
    return best_solution

def simulated_annealing(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    def schedule(t):
        return 100 / (1 + 0.1 * t)

    current = start
    path = []
    t = 0
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    max_iterations = 10000  # Thêm giới hạn số lần lặp tối đa
    
    while len(path) < partial_steps and t < max_iterations:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        temperature = schedule(t)
        if current == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        neighbors = []
        for move_name in MOVES:
            new_state, _, _ = move(current, move_name)
            if new_state:
                neighbors.append((new_state, move_name))
        if not neighbors:
            break
        next_state, move_name = random.choice(neighbors)
        delta_e = manhattan_distance(current, goal) - manhattan_distance(next_state, goal)
        if delta_e > 0 or random.random() < math.exp(delta_e / temperature):
            path.append(move_name)
            current = next_state
        t += 1
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(path),
        "elapsed_time": time.time() - start_time
    })
    return path if path else []

def search_with_no_observation(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    current = start
    path = []
    visited = {state_to_tuple(start)}
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    while len(path) < partial_steps:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        if current == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        neighbors = []
        for move_name in MOVES:
            new_state, _, _ = move(current, move_name)
            if new_state and state_to_tuple(new_state) not in visited:
                neighbors.append((new_state, move_name, manhattan_distance(new_state, goal)))
        if not neighbors:
            neighbors = [(move(current, m)[0], m, float('inf')) for m in MOVES if move(current, m)[0]]
            if not neighbors:
                statistics.update({
                    "nodes_expanded": nodes_expanded,
                    "max_depth": max_depth,
                    "solution_length": len(path),
                    "elapsed_time": time.time() - start_time
                })
                return path
        next_state, move_name, _ = min(neighbors, key=lambda x: x[2])
        path.append(move_name)
        current = next_state
        visited.add(state_to_tuple(current))
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(path),
        "elapsed_time": time.time() - start_time
    })
    return path

def backtracking(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    start_time = time.time()
    nodes_expanded = 0
    max_depth = 0
    
    # Tạo trạng thái ban đầu rỗng
    empty_state = [['_' for _ in range(3)] for _ in range(3)]
    
    def backtrack(state, path, depth, used_numbers):
        nonlocal nodes_expanded, max_depth
        nodes_expanded += 1
        max_depth = max(max_depth, depth)
        
        if state == goal:
            return path
        
        if depth >= partial_steps or depth > 30:
            return None
        
        # Tìm ô trống tiếp theo
        empty_pos = find_empty_tile(state)
        if empty_pos is None:
            return None
        
        i, j = empty_pos
        # Thử điền từng số từ 1 đến 8
        for num in range(1, 9):
            if num not in used_numbers:
                new_state = [row[:] for row in state]
                new_state[i][j] = num
                new_used = used_numbers | {num}
                
                # Kiểm tra xem trạng thái mới có khả thi không
                if get_inversions(new_state) % 2 != get_inversions(goal) % 2:
                    continue  # Bỏ qua nếu không khả thi
                
                result = backtrack(new_state, path + [new_state], depth + 1, new_used)
                if result is not None:
                    return result
        
        return None
    
    # Bắt đầu từ trạng thái rỗng
    used_numbers = set()
    path = backtrack(empty_state, [empty_state], 0, used_numbers)
    
    if path:
        statistics.update({
            "nodes_expanded": nodes_expanded,
            "max_depth": max_depth,
            "solution_length": len(path) - 1,
            "elapsed_time": time.time() - start_time
        })
        return path
    
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": 0,
        "elapsed_time": time.time() - start_time
    })
    return []

def partially_observable(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    global belief_state
    start_time = time.time()
    nodes_expanded = 0
    max_depth = 0
    
    # Kiểm tra tính khả thi
    if not is_solvable(start, goal):
        statistics.update({
            "nodes_expanded": nodes_expanded,
            "max_depth": max_depth,
            "solution_length": 0,
            "elapsed_time": time.time() - start_time
        })
        return []
    
    # Khởi tạo belief state với trạng thái ban đầu
    belief_state = [normalize_state(start)]
    path = []
    current_state = start.copy()
    visited_states = {state_to_tuple(current_state)}
    max_moves = 50  # Giới hạn số bước tối đa
    
    def estimate_progress(state):
        """Ước tính tiến độ dựa trên nhiều yếu tố"""
        h_manhattan = manhattan_distance(state, goal)
        correct_tiles = count_correct_tiles(state, goal)
        inversions = get_inversions(state)
        # Công thức đánh giá tổng hợp
        return h_manhattan - (correct_tiles * 2) + (inversions * 0.5)
    
    def get_best_move(state, visited):
        """Chọn bước đi tốt nhất dựa trên đánh giá nhiều trạng thái"""
        moves = []
        current_score = estimate_progress(state)
        
        for move_name in MOVES:
            new_state, _, _ = move(state, move_name)
            if new_state and state_to_tuple(new_state) not in visited:
                new_score = estimate_progress(new_state)
                # Thêm yếu tố ngẫu nhiên nhỏ để tránh lặp
                randomness = random.uniform(0, 0.1)
                moves.append((new_score + randomness, new_state, move_name))
        
        return min(moves, key=lambda x: x[0]) if moves else None
    
    while len(path) < partial_steps and len(path) < max_moves:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return [start] + path if path else []
        
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        
        # Kiểm tra xem đã đạt mục tiêu chưa
        if current_state == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return [start] + path
        
        # Lấy bước đi tốt nhất
        best_move = get_best_move(current_state, visited_states)
        if not best_move:
            # Nếu không tìm thấy bước đi mới, thử quay lui
            if len(path) > 0:
                current_state = path[-1]
                path.pop()
                continue
            break
        
        _, next_state, move_name = best_move
        
        # Cập nhật belief state
        new_belief = []
        for belief in belief_state:
            possible_next = move(belief, move_name)[0]
            if possible_next:
                new_belief.append(possible_next)
        
        # Kiểm tra belief state không rỗng
        if new_belief:
            belief_state = new_belief[:10]  # Giới hạn kích thước belief state
            current_state = next_state
            path.append(next_state)
            visited_states.add(state_to_tuple(next_state))
        else:
            # Nếu belief state rỗng, thử một hướng khác
            continue
        
        # Kiểm tra tiến độ
        if manhattan_distance(current_state, goal) > manhattan_distance(start, goal) + len(path):
            # Nếu đi quá xa so với điểm bắt đầu, quay lui
            current_state = path[-2] if len(path) > 1 else start
            path.pop()
    
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(path),
        "elapsed_time": time.time() - start_time
    })
    return [start] + path if path else []

def ao_star_partial(start, goal, partial_steps=10):
    start = normalize_state(start)
    goal = normalize_state(goal)
    global tree_nodes, tree_edges, node_positions, tree_screen
    tree_nodes = []
    tree_edges = []
    node_positions = {}
    if tree_screen is None:
        tree_screen = pygame.display.set_mode((TREE_WIDTH, TREE_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Cây AND-OR")
    
    class Node:
        def __init__(self, state, parent=None, move=None, cost=0, node_id=0):
            self.state = state
            self.parent = parent
            self.move = move
            self.cost = cost
            self.h = manhattan_distance(state, goal)
            self.f = self.cost + self.h
            self.children = []
            self.solved = False
            self.node_id = node_id

    def expand_node(node):
        state = node.state
        moves = []
        for move_name in MOVES:
            new_state = move(state, move_name)[0]
            if new_state and state_to_tuple(new_state) not in visited:
                cost = node.cost + 1
                child_id = len(tree_nodes) + 1
                child = Node(new_state, node, move_name, cost, child_id)
                node.children.append(child)
                tree_nodes.append((child_id, child))
                tree_edges.append((node.node_id, child_id, move_name))
                if new_state == goal:
                    child.solved = True
                moves.append(move_name)
        return moves

    def update_f(node):
        if not node.children:
            return node.f, node.solved
        min_f = float('inf')
        solved = False
        for child in node.children:
            child_f, child_solved = update_f(child)
            if child_solved:
                node.solved = True
                min_f = min(min_f, child_f)
            elif child_f < min_f:
                min_f = child_f
        node.f = node.cost + min_f - node.cost
        return node.f, node.solved

    def assign_positions():
        node_positions.clear()
        if not tree_nodes:
            return
        levels = {}
        for node_id, node in tree_nodes:
            depth = node.cost
            if depth not in levels:
                levels[depth] = []
            levels[depth].append(node_id)
        
        max_width = max(len(nodes) for nodes in levels.values()) if levels else 1
        for depth, nodes in levels.items():
            y = 50 + depth * 120 * tree_scale
            for i, node_id in enumerate(nodes):
                x = (TREE_WIDTH // (len(nodes) + 1) * (i + 1)) if len(nodes) > 1 else TREE_WIDTH // 2
                node_positions[node_id] = (x, y)

    open_list = []
    visited = {state_to_tuple(start)}
    root = Node(start, node_id=0)
    tree_nodes.append((0, root))
    heapq.heappush(open_list, (root.f, id(root), root))
    partial_path = []
    nodes_expanded = 0
    max_depth = 0
    start_time = time.time()
    
    while open_list and len(partial_path) < partial_steps:
        assign_positions()
        back_rect = draw_tree(tree_screen)
        pygame.time.delay(50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if back_rect.collidepoint(x, y):
                    pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                    tree_screen = None
                    statistics.update({
                        "nodes_expanded": nodes_expanded,
                        "max_depth": max_depth,
                        "solution_length": len(partial_path),
                        "elapsed_time": time.time() - start_time
                    })
                    return partial_path
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(partial_path),
                "elapsed_time": time.time() - start_time
            })
            return partial_path
        
        _, _, node = heapq.heappop(open_list)
        nodes_expanded += 1
        max_depth = max(max_depth, node.cost)
        if node.solved or node.state == goal:
            path = []
            while node.parent:
                path.append(node.move)
                node = node.parent
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path[::-1]
        
        moves = expand_node(node)
        if moves and len(partial_path) < partial_steps:
            best_child = min(node.children, key=lambda c: c.f)
            partial_path.append(best_child.move)
        update_f(node)
        
        for child in node.children:
            child_tuple = state_to_tuple(child.state)
            if child_tuple not in visited:
                visited.add(child_tuple)
                if len(tree_nodes) <= max_nodes_to_display:
                    heapq.heappush(open_list, (child.f, id(child), child))
        
        heapq.heappush(open_list, (node.f, id(node), node))
    
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(partial_path),
        "elapsed_time": time.time() - start_time
    })
    return partial_path if partial_path else []

def count_correct_tiles(state, goal):
    state = normalize_state(state)
    goal = normalize_state(goal)
    correct = 0
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if state[i][j] == goal[i][j] and state[i][j] != '_':
                correct += 1
    return correct

# Hàm Q-Learning được cải tiến
def q_learning(start, goal, partial_steps=10, episodes=50000):
    start = normalize_state(start)
    goal = normalize_state(goal)
    start_time = time.time()
    nodes_expanded = 0
    max_depth = 0
    path = []
    
    # Tham số Q-Learning được tối ưu
    alpha = 0.2  # Tốc độ học
    gamma = 0.95  # Hệ số chiết khấu
    epsilon_start = 0.5  # Khám phá ban đầu
    epsilon_end = 0.1  # Duy trì khám phá tối thiểu
    epsilon_decay = 0.9999  # Giảm rất chậm để duy trì khám phá
    q_table = {}  # Bảng Q: {state_tuple: {action: q_value}}
    visited_counts = {}  # Theo dõi số lần thăm mỗi trạng thái
    best_path = []  # Lưu đường đi tốt nhất nếu tìm thấy trong huấn luyện
    
    def get_q_value(state, action):
        state_tuple = state_to_tuple(state)
        if state_tuple not in q_table:
            q_table[state_tuple] = {a: 0.0 for a in MOVES}
        return q_table[state_tuple][action]
    
    def update_q_value(state, action, reward, next_state):
        state_tuple = state_to_tuple(state)
        next_state_tuple = state_to_tuple(next_state)
        if next_state_tuple not in q_table:
            q_table[next_state_tuple] = {a: 0.0 for a in MOVES}
        
        current_q = get_q_value(state, action)
        max_next_q = max(q_table[next_state_tuple].values())
        new_q = current_q + alpha * (reward + gamma * max_next_q - current_q)
        q_table[state_tuple][action] = new_q
    
    def choose_action(state, valid_moves, epsilon):
        if random.random() < epsilon:
            return random.choice(valid_moves)
        else:
            state_tuple = state_to_tuple(state)
            if state_tuple not in q_table:
                q_table[state_tuple] = {a: 0.0 for a in MOVES}
            valid_q_values = {a: q_table[state_tuple][a] for a in valid_moves}
            return max(valid_q_values, key=valid_q_values.get)
    
    # Kiểm tra tính khả thi
    if not is_solvable(start, goal):
        statistics.update({
            "nodes_expanded": nodes_expanded,
            "max_depth": max_depth,
            "solution_length": 0,
            "elapsed_time": time.time() - start_time
        })
        return []
    
    # Huấn luyện Q-Learning
    epsilon = epsilon_start
    for episode in range(episodes):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        
        current_state = [row[:] for row in start]
        episode_path = []
        episode_steps = 0
        max_steps = 1000  # Tăng giới hạn bước để khám phá xa hơn
        visited_counts.clear()  # Reset số lần thăm mỗi episode
        
        while episode_steps < max_steps:
            nodes_expanded += 1
            max_depth = max(max_depth, episode_steps)
            
            # Lấy các hành động hợp lệ
            valid_moves = [m for m in MOVES if move(current_state, m)[0] is not None]
            if not valid_moves:
                break
            
            # Chọn hành động với epsilon-greedy
            action = choose_action(current_state, valid_moves, epsilon)
            new_state, _, _ = move(current_state, action)
            if not new_state:
                reward = -50  # Phạt nặng hơn cho hành động không hợp lệ
            else:
                # Cập nhật số lần thăm trạng thái
                state_tuple = state_to_tuple(new_state)
                visited_counts[state_tuple] = visited_counts.get(state_tuple, 0) + 1
                
                # Phần thưởng cải tiến
                current_dist = manhattan_distance(current_state, goal)
                new_dist = manhattan_distance(new_state, goal)
                current_correct = count_correct_tiles(current_state, goal)
                new_correct = count_correct_tiles(new_state, goal)
                
                reward = -3  # Phạt mỗi bước (tăng phạt để khuyến khích đường ngắn)
                if new_dist < current_dist:
                    reward += 20  # Thưởng lớn hơn nếu gần mục tiêu
                elif new_dist > current_dist:
                    reward -= 20  # Phạt lớn hơn nếu xa mục tiêu
                if new_correct > current_correct:
                    reward += 10  # Thưởng nếu số ô đúng vị trí tăng
                elif new_correct < current_correct:
                    reward -= 10  # Phạt nếu số ô đúng vị trí giảm
                reward -= 10 * visited_counts[state_tuple]  # Phạt nặng hơn nếu quay lại trạng thái cũ
                if new_state == goal:
                    reward += 500  # Thưởng rất lớn khi đạt mục tiêu
                    episode_path.append(action)
                    best_path = episode_path  # Lưu đường đi
                    statistics.update({
                        "nodes_expanded": nodes_expanded,
                        "max_depth": max_depth,
                        "solution_length": len(best_path),
                        "elapsed_time": time.time() - start_time
                    })
                    return best_path  # Dừng sớm nếu tìm thấy mục tiêu
            
            # Cập nhật bảng Q
            update_q_value(current_state, action, reward, new_state if new_state else current_state)
            current_state = new_state if new_state else current_state
            episode_path.append(action)
            episode_steps += 1
            
            if new_state == goal:
                best_path = episode_path
                statistics.update({
                    "nodes_expanded": nodes_expanded,
                    "max_depth": max_depth,
                    "solution_length": len(best_path),
                    "elapsed_time": time.time() - start_time
                })
                return best_path
        
        # Giảm epsilon rất chậm để duy trì khám phá
        epsilon = max(epsilon_end, epsilon * epsilon_decay)
    
    # Giai đoạn khai thác: Tạo đường đi tối ưu từ trạng thái ban đầu
    current_state = [row[:] for row in start]
    path = []
    steps = 0
    max_steps = partial_steps if partial_steps != float('inf') else 200  # Tăng giới hạn bước
    visited = set()  # Tránh lặp trạng thái
    visited.add(state_to_tuple(current_state))
    best_dist = manhattan_distance(current_state, goal)
    best_correct = count_correct_tiles(current_state, goal)
    steps_without_improvement = 0  # Theo dõi số bước không tiến bộ
    
    
    # Giai đoạn khai thác: Tạo đường đi tối ưu từ trạng thái ban đầu
    current_state = [row[:] for row in start]
    path = []
    steps = 0
    max_steps = partial_steps if partial_steps != float('inf') else 200  # Tăng giới hạn bước
    visited = set()  # Tránh lặp trạng thái
    visited.add(state_to_tuple(current_state))
    best_dist = manhattan_distance(current_state, goal)
    best_correct = count_correct_tiles(current_state, goal)
    steps_without_improvement = 0  # Theo dõi số bước không tiến bộ
    
    while steps < max_steps:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if paused:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
        
        valid_moves = [m for m in MOVES if move(current_state, m)[0] is not None]
        if not valid_moves:
            break
        
        # Chọn hành động với khám phá ngẫu nhiên cao hơn để thoát local optima
        action = choose_action(current_state, valid_moves, epsilon=0.1)  # 10% cơ hội khám phá ngẫu nhiên
        new_state, _, _ = move(current_state, action)
        if not new_state or state_to_tuple(new_state) in visited:
            # Nếu quay lại trạng thái cũ, thử hành động khác chưa thăm
            remaining_moves = [m for m in valid_moves if m != action and move(current_state, m)[0] and state_to_tuple(move(current_state, m)[0]) not in visited]
            if remaining_moves:
                action = random.choice(remaining_moves)
                new_state, _, _ = move(current_state, action)
            else:
                break
        
        new_dist = manhattan_distance(new_state, goal)
        new_correct = count_correct_tiles(new_state, goal)
        # Kiểm tra tiến bộ dựa trên khoảng cách Manhattan và số ô đúng vị trí
        if new_dist < best_dist or new_correct > best_correct:
            best_dist = new_dist
            best_correct = new_correct
            steps_without_improvement = 0
        else:
            steps_without_improvement += 1
        
        # Dừng nếu không tiến bộ sau 5 bước (giảm ngưỡng để cho phép thử nghiệm nhiều hơn)
        if steps_without_improvement > 5:
            break
        
        path.append(action)
        current_state = new_state
        visited.add(state_to_tuple(current_state))
        steps += 1
        nodes_expanded += 1
        max_depth = max(max_depth, len(path))
        
        if current_state == goal:
            statistics.update({
                "nodes_expanded": nodes_expanded,
                "max_depth": max_depth,
                "solution_length": len(path),
                "elapsed_time": time.time() - start_time
            })
            return path
    
    statistics.update({
        "nodes_expanded": nodes_expanded,
        "max_depth": max_depth,
        "solution_length": len(path),
        "elapsed_time": time.time() - start_time
    })
    return path

def print_state(state):
    for row in state:
        print(" ".join(str(cell) for cell in row))
    print("-" * 10)

def run_algorithm(initial_state, sorted_state, buttons, algorithm):
    global selected_algorithm, animating, animation_start, animation_start_pos, animation_end_pos, animation_tile, tree_nodes, tree_edges, node_positions, tree_screen, paused, statistics, show_solution
    
    algorithm_map = {
        "BFS": bfs, "DFS": dfs, "A*": a_star, "Greedy": greedy,
        "UCS": ucs, "IDA*": ida_star, "ID": iterative_deepening,
        "Steepest Hill": steepest_hill_climbing, "Simple Hill": simple_hill_climbing,
        "Stochastic Hill": stochastic_hill_climbing, "Simulated Annealing": simulated_annealing,
        "AO*": ao_star_partial, "Search with No Observation": search_with_no_observation,
        "Backtracking": backtracking, "Partially Observable": partially_observable,
        "Q-Learning": q_learning 
    }

    selected_algorithm = algorithm
    statistics = {"nodes_expanded": 0, "max_depth": 0, "solution_length": 0, "elapsed_time": 0}
    if selected_algorithm not in algorithm_map:
        return initial_state, sorted_state, True

    show_solution = True
    draw_menu(screen, initial_state, sorted_state, goal_state, f"Đang chạy {selected_algorithm}...", buttons, show_reset=True)
    pygame.display.flip()

    if selected_algorithm == "AO*":
        tree_nodes = []
        tree_edges = []
        node_positions = {}
        if tree_screen is None:
            tree_screen = pygame.display.set_mode((TREE_WIDTH, TREE_HEIGHT), pygame.RESIZABLE)
            pygame.display.set_caption("Cây AND-OR")
        tree_screen.fill(WHITE)
        pygame.display.flip()
    else:
        if tree_screen is not None:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            tree_screen = None
    
    solvable = is_solvable(initial_state, goal_state)
    solution = algorithm_map[selected_algorithm](sorted_state, goal_state, partial_steps=10 if not solvable else float('inf'))

    if solution is None or (not solvable and len(solution) <= 10):
        message = f"{selected_algorithm}: Không tìm thấy lời giải sau 10 bước!" if solvable else "Trạng thái không thể giải được!"
        draw_menu(screen, initial_state, sorted_state, goal_state, message, buttons, show_reset=True)
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    reset_rect = buttons[-2][0]
                    pause_rect = buttons[-1][0]
                    if reset_rect.collidepoint(x, y):
                        show_solution = False
                        selected_algorithm = None
                        algorithm_selected = None
                        paused = False
                        return initial_state, [row[:] for row in initial_state], True
                    if pause_rect.collidepoint(x, y):
                        paused = not paused
            draw_menu(screen, initial_state, sorted_state, goal_state, message, buttons, show_reset=True)
            if selected_algorithm == "AO*" and tree_screen:
                draw_tree(tree_screen)
            pygame.display.flip()
            clock.tick(FPS)
        return initial_state, sorted_state, True

    print("Trạng thái ban đầu:")
    print_state(sorted_state)

    total_width = 3 * (GRID_SIZE * TILE_SIZE)
    spacing = TILE_SIZE * 2
    total_width_with_spacing = total_width + 2 * spacing
    start_x = (WIDTH - total_width_with_spacing) // 2
    grid_x = start_x + GRID_SIZE * TILE_SIZE + spacing
    grid_y = HEIGHT // 4
    
    if solution and isinstance(solution[0], list):
        path_states = solution
    else:
        path_states = [sorted_state]
        current_state = sorted_state
        for move_name in solution:
            new_state, _, _ = move(current_state, move_name)
            if new_state:
                path_states.append(new_state)
                current_state = new_state

    clock = pygame.time.Clock()
    for step, state in enumerate(path_states[1:]):
        animating = True
        animation_start = time.time()
        empty_x, empty_y = find_empty_tile(sorted_state)
        new_empty_x, new_empty_y = find_empty_tile(state)
        
        animation_start_pos = (grid_x + new_empty_y * TILE_SIZE, grid_y + new_empty_x * TILE_SIZE)
        animation_end_pos = (grid_x + empty_y * TILE_SIZE, grid_y + empty_x * TILE_SIZE)
        animation_tile = state[empty_x][empty_y]
        
        while animating:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    pause_rect = buttons[-1][0]
                    reset_rect = buttons[-2][0]
                    if pause_rect.collidepoint(x, y):
                        paused = not paused
                        break
                    if reset_rect.collidepoint(x, y):
                        show_solution = False
                        selected_algorithm = None
                        algorithm_selected = None
                        paused = False
                        return initial_state, [row[:] for row in initial_state], True
            
            if paused:
                running = True
                while running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            x, y = event.pos
                            pause_rect = buttons[-1][0]
                            reset_rect = buttons[-2][0]
                            if pause_rect.collidepoint(x, y):
                                paused = not paused
                                running = False
                            if reset_rect.collidepoint(x, y):
                                show_solution = False
                                selected_algorithm = None
                                algorithm_selected = None
                                paused = False
                                return initial_state, [row[:] for row in initial_state], True
                    screen.fill(WHITE)
                    draw_menu(screen, initial_state, sorted_state, goal_state, f"{selected_algorithm} - Bước {step + 1}/{len(path_states)-1} (Tạm Dừng)", buttons, show_reset=True)
                    if selected_algorithm == "AO*" and tree_screen:
                        draw_tree(tree_screen)
                    pygame.display.flip()
                    clock.tick(FPS)
                continue
            
            screen.fill(WHITE)
            draw_menu(screen, initial_state, sorted_state, goal_state, f"{selected_algorithm} - Bước {step + 1}/{len(path_states)-1}", buttons, show_reset=True)
            if selected_algorithm == "AO*" and tree_screen:
                draw_tree(tree_screen)
            
            animating = draw_state(screen, sorted_state, grid_x, grid_y, "Trạng Thái Đang Sắp Xếp", (empty_x, empty_y))
            
            if not animating:
                sorted_state = state
            
            pygame.display.flip()
            clock.tick(FPS)
        
        print(f"Bước {step + 1}")
        print_state(sorted_state)

    screen.fill(WHITE)
    draw_menu(screen, initial_state, sorted_state, goal_state, f"Hoàn thành! {selected_algorithm}", buttons, show_reset=True)
    if selected_algorithm == "AO*" and tree_screen:
        draw_tree(tree_screen)
    pygame.display.flip()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                reset_rect = buttons[-2][0]
                pause_rect = buttons[-1][0]
                if reset_rect.collidepoint(x, y):
                    show_solution = False
                    selected_algorithm = None
                    algorithm_selected = None
                    paused = False
                    return initial_state, [row[:] for row in initial_state], True
                if pause_rect.collidepoint(x, y):
                    paused = not paused
            screen.fill(WHITE)
            draw_menu(screen, initial_state, sorted_state, goal_state, f"Hoàn thành! {selected_algorithm}", buttons, show_reset=True)
            if selected_algorithm == "AO*" and tree_screen:
                draw_tree(tree_screen)
            pygame.display.flip()
            clock.tick(FPS)
    
    return initial_state, sorted_state, True

def main():
    global initial_state, sorted_state, goal_state, selected_algorithm, algorithm_selected, manual_mode, animating, animation_start, animation_start_pos, animation_end_pos, animation_tile, input_mode, input_state, input_pos, input_phase, tree_scale, distance_cache, tree_screen, button_pressed, paused, confirmation_message, confirmation_start_time, backtracking_mode, partially_observable_mode, belief_state, statistics, show_solution
    buttons = create_buttons()
    clock = pygame.time.Clock()
    mouse_pos = None
    error_message = None
    error_start_time = None
    
    while True:
        message = "Chọn thuật toán" if not manual_mode else "Chế độ thủ công"
        if input_mode:
            if input_phase == "initial":
                message = "Nhập trạng thái ban đầu (1-9, 9 cho ô trống)"
            elif input_phase == "goal":
                message = "Nhập trạng thái mục tiêu (1-9, 9 cho ô trống)"
        if error_message and (time.time() - error_start_time) < 5:
            message = error_message
        # Xóa sạch màn hình trước khi vẽ
        screen.fill(WHITE)
        reset_rect = draw_menu(screen, initial_state, sorted_state, goal_state, message, buttons, input_mode, show_solution, mouse_pos)
        if selected_algorithm == "AO*" and tree_screen:
            draw_tree(tree_screen)
        pygame.display.flip()  # Gọi một lần sau khi vẽ xong menu và cây (nếu có)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                buttons = resize_layout()
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
            if event.type == pygame.MOUSEBUTTONDOWN and not animating:
                x, y = event.pos
                for rect, label in buttons:
                    if rect.collidepoint(x, y):
                        button_pressed = label
                        if label == "Chế Độ Thủ Công":
                            manual_mode = not manual_mode
                            input_mode = False
                            input_phase = "initial"
                            algorithm_selected = None
                            selected_algorithm = None
                            backtracking_mode = False
                            partially_observable_mode = False
                            show_solution = False
                        elif label == "Nhập Trạng Thái":
                            input_mode = not input_mode
                            manual_mode = False
                            algorithm_selected = None
                            selected_algorithm = None
                            input_state = [['' for _ in range(3)] for _ in range(3)]
                            input_pos = (0, 0)
                            input_phase = "initial"
                            show_solution = False
                        elif label == "Xác Nhận" and input_mode:
                            if is_valid_state(input_state):
                                if input_phase == "initial":
                                    initial_state = normalize_state([row[:] for row in input_state])
                                    sorted_state = normalize_state([row[:] for row in input_state])
                                    input_state = [['' for _ in range(3)] for _ in range(3)]
                                    input_pos = (0, 0)
                                    input_phase = "goal"
                                    confirmation_message = "Trạng thái ban đầu đã xác nhận! Nhập trạng thái mục tiêu."
                                    confirmation_start_time = time.time()
                                elif input_phase == "goal":
                                    goal_state = normalize_state([row[:] for row in input_state])
                                    input_mode = False
                                    input_phase = "initial"
                                    confirmation_message = "Trạng thái mục tiêu đã xác nhận!"
                                    confirmation_start_time = time.time()
                            else:
                                error_message = "Trạng thái không hợp lệ! Đảm bảo có 1-8 và một ô trống (9)."
                                error_start_time = time.time()
                        elif label == "Đặt Lại":
                            initial_state = [[2, 6, 5], ['_', 8, 7], [4, 3, 1]]
                            sorted_state = [row[:] for row in initial_state]
                            goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, '_']]
                            selected_algorithm = None
                            algorithm_selected = None
                            manual_mode = False
                            input_mode = False
                            input_phase = "initial"
                            tree_nodes = []
                            tree_edges = []
                            node_positions = {}
                            distance_cache.clear()
                            animation_frames = []
                            current_frame = 0
                            auto_play = False
                            path_steps = []
                            show_solution = False
                            backtracking_mode = False
                            partially_observable_mode = False
                            belief_state = []
                            paused = False
                            statistics = {"nodes_expanded": 0, "max_depth": 0, "solution_length": 0, "elapsed_time": 0}
                            if tree_screen is not None:
                                pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                                tree_screen = None
                        elif label == "Play":
                            if algorithm_selected:
                                initial_state, sorted_state, _ = run_algorithm(initial_state, sorted_state, buttons, algorithm_selected)
                            else:
                                error_message = "Vui lòng chọn thuật toán trước!"
                                error_start_time = time.time()
                        elif label == "Tạm Dừng":
                            paused = not paused
                        elif label in ALGORITHMS:
                            algorithm_selected = label
                            backtracking_mode = (label == "Backtracking")
                            partially_observable_mode = (label == "Partially Observable")
                            message = f"Đã chọn thuật toán: {label}. Nhấn Play để chạy."
                        button_pressed = None
            elif event.type == pygame.MOUSEBUTTONUP:
                button_pressed = None
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_PLUS, pygame.K_EQUALS] and selected_algorithm == "AO*":
                tree_scale += 0.1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS and selected_algorithm == "AO*":
                tree_scale = max(0.5, tree_scale - 0.1)
            if event.type == pygame.KEYDOWN and manual_mode and not animating:
                move_dir = None
                if event.key == pygame.K_UP:
                    move_dir = "UP"
                elif event.key == pygame.K_DOWN:
                    move_dir = "DOWN"
                elif event.key == pygame.K_LEFT:
                    move_dir = "LEFT"
                elif event.key == pygame.K_RIGHT:
                    move_dir = "RIGHT"
                if move_dir:
                    grid_x = (WIDTH - (3 * GRID_SIZE * TILE_SIZE + 2 * 4.5 * TILE_SIZE)) // 2 + 4.5 * TILE_SIZE
                    grid_y = HEIGHT // 4
                    new_state, new_pos, tile_value = move(sorted_state, move_dir)
                    if new_state:
                        animating = True
                        animation_start = time.time()
                        empty_x, empty_y = find_empty_tile(sorted_state)
                        new_x, new_y = new_pos
                        animation_start_pos = (grid_x + new_y * TILE_SIZE, grid_y + new_x * TILE_SIZE)
                        animation_end_pos = (grid_x + empty_y * TILE_SIZE, grid_y + empty_x * TILE_SIZE)
                        animation_tile = tile_value
                        sorted_state = new_state
            if event.type == pygame.KEYDOWN and input_mode:
                i, j = input_pos
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    num = event.key - pygame.K_0
                    flat_input = [x for row in input_state for x in row if x != '']
                    # Kiểm tra trùng lặp số, ngoại trừ số 9 (ô trống)
                    if num == 9:
                        # Chỉ cho phép một ô trống (số 9)
                        if 9 not in flat_input:
                            input_state[i][j] = num
                            if j < 2:
                                input_pos = (i, j + 1)
                            elif i < 2:
                                input_pos = (i + 1, 0)
                            else:
                                input_pos = (0, 0)
                        else:
                            error_message = "Chỉ được phép có một ô trống (số 9)!"
                            error_start_time = time.time()
                    else:
                        # Kiểm tra trùng lặp cho các số 1-8
                        if str(num) not in flat_input or input_state[i][j] == str(num):
                            input_state[i][j] = num
                            if j < 2:
                                input_pos = (i, j + 1)
                            elif i < 2:
                                input_pos = (i + 1, 0)
                            else:
                                input_pos = (0, 0)
                        else:
                            error_message = f"Số {num} đã tồn tại! Vui lòng nhập số khác."
                            error_start_time = time.time()
                elif event.key == pygame.K_BACKSPACE:
                    input_state[i][j] = ''
                    if j > 0:
                        input_pos = (i, j - 1)
                    elif i > 0:
                        input_pos = (i - 1, 2)
                    else:
                        input_pos = (0, 0)
                elif event.key == pygame.K_RETURN:
                    if is_valid_state(input_state):
                        if input_phase == "initial":
                            initial_state = normalize_state([row[:] for row in input_state])
                            sorted_state = normalize_state([row[:] for row in input_state])
                            input_state = [['' for _ in range(3)] for _ in range(3)]
                            input_pos = (0, 0)
                            input_phase = "goal"
                            confirmation_message = "Trạng thái ban đầu đã xác nhận! Nhập trạng thái mục tiêu."
                            confirmation_start_time = time.time()
                        elif input_phase == "goal":
                            goal_state = normalize_state([row[:] for row in input_state])
                            input_mode = False
                            input_phase = "initial"
                            confirmation_message = "Trạng thái mục tiêu đã xác nhận!"
                            confirmation_start_time = time.time()
                    else:
                        error_message = "Trạng thái không hợp lệ! Đảm bảo có 1-8 và một ô trống (9)."
                        error_start_time = time.time()
                elif event.key == pygame.K_LEFT and j > 0:
                    input_pos = (i, j - 1)
                elif event.key == pygame.K_RIGHT and j < 2:
                    input_pos = (i, j + 1)
                elif event.key == pygame.K_UP and i > 0:
                    input_pos = (i - 1, j)
                elif event.key == pygame.K_DOWN and i < 2:
                    input_pos = (i + 1, j)
                elif event.key == pygame.K_ESCAPE:
                    input_mode = False
                    input_phase = "initial"
                    input_state = [['' for _ in range(3)] for _ in range(3)]
                    input_pos = (0, 0)
        
        if animating and not paused:
            grid_x = (WIDTH - (3 * GRID_SIZE * TILE_SIZE + 2 * 4.5 * TILE_SIZE)) // 2 + 4.5 * TILE_SIZE
            grid_y = HEIGHT // 4
            empty_pos = find_empty_tile(sorted_state)
            # Xóa sạch màn hình trước khi vẽ
            screen.fill(WHITE)
            draw_menu(screen, initial_state, sorted_state, goal_state, "Đang di chuyển...", buttons, show_reset=show_solution)
            if selected_algorithm == "AO*" and tree_screen:
                draw_tree(tree_screen)
            animating = draw_state(screen, sorted_state, grid_x, grid_y, "Trạng Thái Đang Sắp Xếp", empty_pos)
            pygame.display.flip()
            clock.tick(FPS)
        
        clock.tick(FPS)

if __name__ == "__main__":
    main()