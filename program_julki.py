from datetime import datetime

WIDTH = 1280
HEIGHT = 640


# definicje klas
class Game:
    def __init__(self, background_active, rooms_in_game):

        # ustawiamy najważniejsze elementy, niektóre na stałe
        self.background_active = background_active
        self.background_position = (0, 0)
        self.game_start = False
        self.game_finish = False
        self.actual_room = 5
        self.start_time = None
        self.all_keys_found = False
        self.show_hidden_door = False
        self.enter_last_door = False
        self.shift_ok = True
        self.game_time = None

        # grafiki na rozpoczęcie i zakończenie gry
        self.intro_canvas = Actor("intro1.png")
        self.intro_canvas.pos = (640, -160)
        self.game_over_canvas = Actor("finish.png")
        self.game_over_canvas.pos = (320, -160)

        # elementy związane z naszym bohaterem
        self.floor_level = 460
        self.hero = Actor("manright1.png")
        self.hero.pos = (WIDTH / 2, self.floor_level)
        # wyznaczenie rozmiarów gracza
        self.hero.height = 256
        self.hero.width = 140
        self.hero.frame = 1
        self.animation_step = 15

        # słownik z opisami pomieszczeń
        self.rooms = rooms_in_game

        # klucze
        self.pocket = Actor("pocket1.png")
        self.pocket.pos = (960, 95)
        self.keys_in_pocket = [key_00, key_01, key_02, key_03, key_04]

        #muzyka
        music.play("music-background.mp3")
        music.set_volume(0.1)
        self.music_play = True




    def draw_intro(self):
        def draw_text(text, x_offset, y_offset, fontsize=20):
            screen.draw.text(
                text,
                (self.intro_canvas.x + x_offset, self.intro_canvas.y + y_offset),
                fontname="ptsansnarrowbold.ttf",
                fontsize=fontsize,
                color=(187, 96, 191),
            )

        # wyświetlenie ekranu startowego gry
        self.intro_canvas.draw()
        animate(self.intro_canvas, pos=(640, 320), duration=0.3, tween="linear")

        draw_text("A game where you're lost", -450, -200, fontsize=32)

        # wprowadzenie: przedstawienie historii gry, zadania do wykonania, oraz klawisze aktywne w grze.
        story = (
            "It's a game where the main character is lost in an abandoned school. "
            "To get to the final control room they have to find all the keys. "
            "As we all suspect the kid does not want to stay lost... "
            "that's where you step in! "
            "You need to help them discover a secret door to freedom. "
            "We both hope you understant your task. "
            "Good luck! - the Creator"
            "\n\n"
            "click 'Q' to quit the game"
            "\n\n"
            "Click SPACE to start! "
        )

        screen.draw.text(
            story,
            (self.intro_canvas.x - 450, self.intro_canvas.y - 160),
            width=900,
            fontname="ptsansnarrowregular.ttf",
            fontsize=20,
            color=(0, 0, 0),
        )

    def draw_finish(self):
        # animujemy pojawienie się pucharu
        self.game_over_canvas.draw()
        animate(self.game_over_canvas, pos=(900, 320), duration=0.3, tween="linear")
        # pokazujemy teksty
        screen.draw.text(
            "You found the room!",
            (self.game_over_canvas.x - 140, self.game_over_canvas.y - 180),
            fontname="ptsansnarrowbold.ttf",
            fontsize=32,
            color=(187, 96, 191),
        )

        story = (
            f"Your time is: {self.game_time} \n\nClick 'Q' to exit!"
        )
        screen.draw.text(
            story,
            (self.game_over_canvas.x - 140, self.game_over_canvas.y - 120),
            fontname="ptsansnarrowregular.ttf",
            fontsize=20,
            color=(0, 0, 0),
        )
        if self.music_play:
            self.music_play = False
            music.stop()
            music.play_once("music-end-01.mp3")
            music.set_volume(0.7)

    def draw_pocket(self):
        self.pocket.draw()
        # ustawienie położenia / odległości między kluczami
        key_pos = [-200, -100, 0, 100, 200]

        temp = 0
        # dla każdego klucza w liście kluczy
        for key in self.keys_in_pocket:
            pos = (self.pocket.x + key_pos[temp] - 45, self.pocket.y - 30)
            temp += 1
            if key.in_pocket:
                # jeśli mamy klucz - wyświetlamy z pliku graficznego w konkretnej pozycji
                screen.blit(key.file_name, pos)
            else:
                # jeśli nie mamy klucza wyświetlamy znak zapytania
                screen.blit("question_mark.png", pos)

    def hero_move(self, direction):

        # pobieramy flagę mówiącą o tym, w którą stronę Maks może się przemieści
        move_flag = self.rooms[self.actual_room].can_move_lr

        if direction == "right":
            # jeżeli jest to możliwe przesuwamy postać
            if self.hero.x < WIDTH - self.hero.width:
                self.hero.x += self.animation_step
            else:
                if move_flag == 2 or move_flag == 3:
                    self.actual_room += 1
                    self.hero.x = 10

        if direction == "left":
            # jeżeli jest to możliwe przesuwamy postać
            if self.hero.x > self.hero.width:
                self.hero.x -= self.animation_step
            else:
                if move_flag == 1 or move_flag == 3:
                    self.actual_room -= 1
                    self.hero.x = WIDTH - self.hero.width

        # sprawdzamy tło dla nowego pomieszczenia
        new_background_image = self.rooms[self.actual_room].file_name
        self.background_active = new_background_image

        # ustawiamy odpowiedni obrazek animujący ruch
        self.hero.image = f"man{direction}{self.hero.frame}.png"
        # zwiększając numer obrazka następnym razem załadujemy inny,
        # co będzie pozornie wyglądało jak ruch
        self.hero.frame += 1
        # jest 8 obrazków, więc jeśli frame > 8
        if self.hero.frame > 8:
            # to wracamy do 1
            self.hero.frame = 1
        if self.hero.frame == 4 or self.hero.frame == 8:
            sounds.walk.play()

    def enter_door(self):
        # pobieramy element słownika
        room = self.rooms[self.actual_room]
        if len(room.doors):
            for door in room.doors:
                if (
                    self.hero.x > door.x_left_door
                    and self.hero.x < door.x_right_door
                    and door.open
                    and self.shift_ok
                ):
                    self.shift_ok = False
                    sounds.door.play()
                    # pobieramy nowy numer pomieszczenia i nazwę pliku tła
                    new_room = door.next_room_number
                    new_background_image = self.rooms[new_room].file_name
                    # ustawiamy odpowiednie właściwości
                    self.background_active = new_background_image
                    self.actual_room = new_room
                    # odblokowujemy po pół sekundy
                    clock.schedule_unique(self.shitf_do, 0.5)
                    # jeśli wchodzimy do auli, kończymy grę
                    if not self.enter_last_door and new_room == 13:
                        self.enter_last_door = True
                        self.game_time = datetime.now() - self.start_time
                    # przerywamy pętlę for i kończymy
                    break

    def shitf_do(self):
        self.shift_ok = True

    def draw_key(self):
        # dla każdego klucza w grze
        for key in self.keys_in_pocket:
            # jeżeli klucza nie ma w kieszeni odnalezionych i aktualny numer
            # pomieszczenia jest taki sam jak numer pomieszczenia dla klucza
            if not key.in_pocket and self.actual_room == key.room_number:
                # wyświetlamy klucz
                screen.blit(key.file_name, (key.place_on_floor, 534))

    def get_key(self):
        def check_all_keys(keys):
            for any_key in keys:
                if any_key.in_pocket is False:
                    return False
            else:
                # umożliwiamy przejście przez tajne drzwi
                # w instancji room_08 klasy Room, w liście drzwi, indeks 1
                self.rooms[8].doors[1].open = True
                return True

        # dla każdego klucza w grze
        for key in self.keys_in_pocket:
            # jeżeli klucza nie ma w kieszeni odnalezionych i aktualny numer
            # pomieszczenia jest taki sam jak numer pomieszczenia dla klucza
            # a nasz bohater jest blisko klucza
            if (
                not key.in_pocket
                and self.actual_room == key.room_number
                and (120 > self.hero.x - key.place_on_floor >= 0)
            ):
                # ustawiamy klucz jako znaleziony
                key.in_pocket = True
                # i sprawdzamy, czy znaleźliśmy już wszystkie klucze
                self.all_keys_found = check_all_keys(self.keys_in_pocket)

    def update_game(self):
        """ ta metoda będzie wywoływana z funkcji update() programu głównego """

        if not self.game_start and keyboard.space:
            self.game_start = True
            self.start_time = datetime.now()

        if keyboard.q:
            quit()

        if self.game_start:

            if keyboard.d:
                self.hero_move("right")
            if keyboard.a:
                self.hero_move("left")
            if keyboard.w:
                self.enter_door()
            if keyboard.s:
                self.get_key()
            if keyboard.k_0:
                music.set_volume(0)
            if keyboard.k_1:
                music.set_volume(0.1)
            if keyboard.k_2:
                music.set_volume(0.2)
            if keyboard.k_3:
                music.set_volume(0.7)
            if keyboard.k_4:
                music.set_volume(1.3)
            if keyboard.k_5:
                music.set_volume(1.9)


            if self.all_keys_found:
                self.show_hidden_door = True
            if self.actual_room == 13 and self.enter_last_door:
                self.game_finish = True
                self.game_start = False


    def draw_scene(self):
        """ ta metoda będzie wywoływana z funkcji draw() programu głównego """

        # rysujemy tło
        screen.blit(self.background_active, self.background_position)

        if self.game_start:
            # rysujemy torbę z kluczami
            self.draw_pocket()
            # rysujemy klucz, jeśli jest w tym pomieszczeniu
            self.draw_key()
            # rysujemy ukryte drzwi i ustawiamy możliwość przejścia
            if self.all_keys_found and self.actual_room == 8:
                screen.blit("thedoor.jpg", (206, 118))

            # rysujemy głównego bohatera bazując na jego danych
            self.hero.draw()

        elif self.game_finish:
            self.draw_finish()
        else:
            self.draw_intro()


class Key:
    def __init__(self, file_name, in_pocket, room_number, place_on_floor):
        """ self oznacza *siebie samego* - czyli konkretny klucz """

        # te właściwości obiektu *self* przepisywane są z parametrów
        self.file_name = file_name
        self.in_pocket = in_pocket
        self.room_number = room_number
        self.place_on_floor = place_on_floor

    # na razie nie robimy nic
    pass


class Door:
    def __init__(self, room_number, door_position, next_room_number, open):
        """ self oznacza *siebie samego* - czyli konkretne drzwi """

        self.room_number = room_number
        # każde drzwi mają pewne wymiary (235 pixeli), więc obliczamy lewy i prawy koniec
        self.x_left_door = door_position - (230 / 2)
        self.x_right_door = door_position + (230 / 2)
        self.next_room_number = next_room_number
        self.open = open

    # na razie nie robimy nic
    pass


class Room:
    def __init__(self, room_number, room_name, can_move_lr, file_name, doors=[]):

        self.room_number = room_number
        self.room_name = room_name
        # czy z pomieszczenia prowadzą przejścia, w lewo i prawo
        # zmienne typu lewo/prawo/góra dół nie muszą występować wszystkie jednocześnie
        # można w tym celu nadać jakieś "flagi" (wartości) dla poszczególnych możliwości
        # np. 0 - brak wyjść, 1 tylko w lewo, 2, tylko w prawo, 3 w lewo i w prawo
        self.can_move_lr = can_move_lr
        # nazwa pliku z tłem pokoju
        self.file_name = file_name
        # lista drzwi znajdujących się w pokoju - domyślnie pusta lista []
        self.doors = doors

    # na razie nie robimy nic
    pass


# podstawowe zmienne
background_active = "c1.jpg"

# tworzymy klucze, a jako *self* będą przypisane nazwy zmiennych key_
key_00 = Key("key1.png", False, 11, 1050)
key_01 = Key("key2.png", False, 17, 80)
key_02 = Key("key3.png", False, 16, 670)
key_03 = Key("key4.png", False, 4, 950)
key_04 = Key("key5.png", False, 0, 370)

# tworzymy drzwi zgodnie z planem pomieszczeń
# domyślnie każde z drzwi będzie otwarte
door_00 = Door(0, 967, 5, True)
door_01 = Door(3, 962, 8, True)
door_02 = Door(5, 240, 15, True)
door_03 = Door(5, 967, 0, True)
door_04 = Door(6, 930, 11, True)
door_05 = Door(7, 735, 17, True)
door_06 = Door(8, 1000, 3, True)
door_07 = Door(8, 327, 13, False)
door_08 = Door(11, 925, 6, True)
door_09 = Door(13, 327, 8, True)
door_10 = Door(15, 240, 5, True)
door_11 = Door(17, 735, 7, True)

# tworzymy opisy pomieszczeń zgodnie z planem, najpierw tworzymy instancje klasy Room
room_00 = Room(0, "Przyroda 01", 2, "science1.jpg", [door_00])
room_01 = Room(1, "Przyroda 02", 1, "science2.jpg")
room_03 = Room(3, "Sala Gimnastyczna 01", 2, "pe1.jpg", [door_01])
room_04 = Room(4, "Sala Gimnastyczna 02", 1, "pe2.jpg")
room_05 = Room(5, "Korytarz 01 lewy", 2, "c1.jpg", [door_02, door_03])
room_06 = Room(6, "Korytarz 02", 3, "c2.jpg", [door_04])
room_07 = Room(7, "Korytarz 03", 3, "c3.jpg", [door_05])
room_08 = Room(8, "Korytarz 04 prawy", 1, "c4.jpg", [door_06, door_07])
room_11 = Room(11, "WC", 0, "wc1.jpg", [door_08])
room_13 = Room(13, "Aula", 0, "the_end.jpg", [door_09])  # Tego nie ma na mapie !
room_15 = Room(15, "Matematyka 01", 2, "math0.jpg", [door_10])
room_16 = Room(16, "Matematyka 02", 1, "math2.jpg")
room_17 = Room(17, "Informatyka 01", 2, "inf0.jpg", [door_11])
room_18 = Room(18, "Informatyka 02", 1, "inf2.jpg")

# następnie tworzymy słownik odpowiadający numeracją układowi pomieszczeń na mapie
rooms_in_game = {
    0: room_00,
    1: room_01,
    3: room_03,
    4: room_04,
    5: room_05,
    6: room_06,
    7: room_07,
    8: room_08,
    11: room_11,
    13: room_13,
    15: room_15,
    16: room_16,
    17: room_17,
    18: room_18,
}


# tworzymy zmienną gry
game = Game(background_active, rooms_in_game)


def update():
    game.update_game()


def draw():
    game.draw_scene()