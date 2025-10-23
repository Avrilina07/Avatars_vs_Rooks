import sys
import pygame


class PantallaDificultad:
    """Pantalla simple con 4 botones: Fácil, Medio, Difícil, Salir.
    Solo el botón 'Salir' cierra el programa.
    """

    def __init__(self, width=640, height=480):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Seleccionar dificultad')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        # Define botones: rects and labels
        btn_w, btn_h = 200, 60
        gap = 20
        total_h = 4 * btn_h + 3 * gap
        start_y = (self.height - total_h) // 2
        center_x = (self.width - btn_w) // 2

        labels = ['Fácil', 'Medio', 'Difícil', 'Salir']
        self.buttons = []
        for i, lab in enumerate(labels):
            rect = pygame.Rect(center_x, start_y + i * (btn_h + gap), btn_w, btn_h)
            self.buttons.append((rect, lab))

    def draw(self):
        self.screen.fill((30, 30, 30))
        for rect, label in self.buttons:
            pygame.draw.rect(self.screen, (200, 200, 200), rect, border_radius=8)
            # label
            txt = self.font.render(label, True, (10, 10, 10))
            txt_rect = txt.get_rect(center=rect.center)
            self.screen.blit(txt, txt_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    for rect, label in self.buttons:
                        if rect.collidepoint(pos):
                            if label == 'Salir':
                                pygame.quit()
                                sys.exit(0)
                            else:
                                # For now other buttons do nothing; could be expanded
                                print(f'Botón pulsado: {label}')

            self.draw()
            self.clock.tick(30)


def main():
    pantalla = PantallaDificultad()
    pantalla.run()


if __name__ == '__main__':
    main()
