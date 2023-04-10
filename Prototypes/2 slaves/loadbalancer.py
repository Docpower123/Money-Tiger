import pygame



server_list = [(21),(22)]


# Define map size and player coordinates
map_size = (400, 400)
player_pos = (200, 100)

# Define areas
area_size = (map_size[0] // 2, map_size[1] // 2)
area1 = pygame.Rect((0, 0), area_size)  # top-left area
area2 = pygame.Rect((area_size[0], 0), area_size)  # top-right area
area3 = pygame.Rect((0, area_size[1]), area_size)  # bottom-left area
area4 = pygame.Rect(area_size, area_size)  # bottom-right area

# Define buffer areas
buffer_size = 10
buffer1 = area1.inflate(buffer_size, buffer_size)
buffer2 = area2.inflate(buffer_size, buffer_size)
buffer3 = area3.inflate(buffer_size, buffer_size)
buffer4 = area4.inflate(buffer_size, buffer_size)

# Determine which areas the player's coordinates belong to
area1_flag = buffer1.collidepoint(player_pos)
area2_flag = buffer2.collidepoint(player_pos)
area3_flag = buffer3.collidepoint(player_pos)
area4_flag = buffer4.collidepoint(player_pos)

# Determine which areas the player is in
player_area = ""
if area1_flag:
    player_area += "1"
if area2_flag:
    player_area += "2"
if area3_flag:
    player_area += "3"
if area4_flag:
    player_area += "4"
if not player_area:
    player_area = "none"

# Define window
pygame.init()
window = pygame.display.set_mode(map_size)
pygame.display.set_caption("Map")

# Draw areas and buffers on window
pygame.draw.rect(window, (0, 255, 0), area1)
pygame.draw.rect(window, (0, 0, 255), area2)
pygame.draw.rect(window, (255, 255, 0), area3)
pygame.draw.rect(window, (255, 0, 0), area4)
pygame.draw.rect(window, (128, 128, 128), buffer1, 1)
pygame.draw.rect(window, (128, 128, 128), buffer2, 1)
pygame.draw.rect(window, (128, 128, 128), buffer3, 1)
pygame.draw.rect(window, (128, 128, 128), buffer4, 1)

# Draw player on window
pygame.draw.circle(window, (255, 255, 255), player_pos, 5)

# Display player area on window
font = pygame.font.SysFont("arial", 24)
text = font.render("Player is in Area(s) " + player_area, True, (255, 255, 255))
text_rect = text.get_rect(center=(map_size[0] // 2, map_size[1] - 20))
window.blit(text, text_rect)

# Update window
pygame.display.flip()
print(player_area)

if player_area == '1':
    print(server_list[0])

if player_area == '2':
    print(server_list[1])

if player_area == '3':
    print(server_list[2])

if player_area == '4':
    print(server_list[3])

if player_area == '12':
    print(server_list[0])
    print(server_list[1])

if player_area == '13':
    print(server_list[0])
    print(server_list[2])

if player_area == '34':
    print(server_list[2])
    print(server_list[3])
if player_area == '24':
    print(server_list[1])
    print(server_list[3])


# Wait for window to close
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
