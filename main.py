import time
import string
import random
import bruhcolor
from bruhanimate.bruhffer import Buffer
from bruhanimate.bruhscreen import Screen
from bruhanimate.bruheffects import StarEffect


class GradientNoise:
    def __init__(self, x, y, length, char_halt=1, color_halt=1, gradient_length=1):
        self.x = x
        self.y = y
        self.__gradient_length = gradient_length
        # colors to use for gradient
        self.__gradient = [c for c in [232,232,232,232,233,233,233,233,234,234,234,234,235,235,235,235,236,236,236,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255] for _ in range(self.__gradient_length)]
        # delay to changing the chars in the noise
        self.__char_halt = char_halt
        self.__char_frame_number = 0
        # delay to change the gradient shift
        self.__color_halt = color_halt
        self.__color_frame_number = 0
        self.length = length
        self.done_generating = False
        
        self.string_chars = [" " for _ in range(self.length)]
        self.string_colors = [self.__gradient[i % len(self.__gradient)] for i in range(self.length)]
        self.colored_chars = [bruhcolor.bruhcolored(c, color=color) for c, color in zip(self.string_chars, self.string_colors)]

    # change the gradient
    def update_gradient(self, gradient):
        self.__gradient = [c for c in gradient for _ in range(self.__gradient_length)]
        return self

    def generate(self, frame_number: int):
        if self.done_generating: return
        # is it time to change the noise chars?
        if frame_number % self.__char_halt == 0:
            self.__char_frame_number += 1
            for i, c in enumerate(self.string_chars):
                # frame == 0 basically
                if not c:
                    self.string_chars[i] = random.choice(
                        string.ascii_letters + "1234567890!@#$%^&*()_+-=<>,.:\";'{}[]?/"
                    )
                # randomly decide to update this char to a new one
                elif random.random() < 0.6:
                    self.string_chars[i] = random.choice(
                        string.ascii_letters + "1234567890!@#$%^&*()_+-=<>,.:\";'{}[]?/"
                    )
        # is it time to change the gradient position?
        if frame_number % self.__color_halt == 0:
            self.__color_frame_number += 1
            self.string_colors = [
                self.__gradient[(i - self.__color_frame_number) % len(self.__gradient)]
                for i in range(self.length)
            ]

        # update the color characters exposed to the main program
        self.colored_chars = [
            bruhcolor.bruhcolored(c, color=color)
            for c, color in zip(self.string_chars, self.string_colors)
        ]

    def mark_done(self):
        self.done_generating = True
        

class Bubble:
    def __init__(self, bubbles=5):
        self.bubbles = bubbles
        self.bubble_chars = ["." for _ in range(self.bubbles)]
        self.pos = 0
        self.inc_val = 1

    def update(self):
        # for each update call, push the bubble back
        # and forth
        self.bubble_chars[self.pos] = "•"
        self.bubble_chars[self.pos - self.inc_val] = "."
        if self.pos >= self.bubbles - 1:
            self.inc_val = -1
        elif self.pos <= 0:
            self.inc_val = 1
        self.pos += self.inc_val


class GenerateBubble:
    """
    Creates the "Generating" text and the bubble that
    moves back and forth
    """
    def __init__(self, x, y, bubbles=4, halt=1):
        self.x = x
        self.y = y
        self.__halt = halt
        self.__main_text = list("Generating")
        self.__bubble_generator = Bubble(bubbles)
        self.chars = self.__main_text + self.__bubble_generator.bubble_chars
        self.done_generating = False

    def generate(self, frame_number: int):
        if frame_number % self.__halt == 0:
            if not self.done_generating:
                self.__bubble_generator.update()
            self.chars = self.__main_text + self.__bubble_generator.bubble_chars
            
    def mark_done(self, frame_number: int, message: str = "Done"):
        self.done_generating = True
        self.__bubble_generator.bubble_chars = list(" " + message)
        self.__main_text = []
        self.generate(frame_number)


class Cradle:
    """
    Class to handle sending bubble from beggining
    to end only.
    """
    def __init__(self, cradle_length=5):
        self.cradle_length = cradle_length
        self.cradle_chars = ["." for _ in range(self.cradle_length)]
        self.ball = "•"
        self.ball_pos = -1

    def update(self):
        self.cradle_chars[0] = self.ball
        self.ball_pos = 0

    def push_ball(self) -> bool:
        self.cradle_chars[self.ball_pos] = "."
        if self.ball_pos == self.cradle_length - 1:
            self.ball_pos = -1
            return True
        else:
            self.ball_pos = (self.ball_pos + 1) % self.cradle_length
            self.cradle_chars[self.ball_pos] = self.ball
            return False


class GenerateCradle:
    """
    Class to handle the "Generating" text and updating
    the cradle ball to get sent to the end.
    """
    def __init__(self, x, y, cradle_length=4, halt=1):
        self.x = x
        self.y = y
        self.__halt = halt
        self.__main_text = list("Generating")
        self.__gradle_generator = Cradle(cradle_length)
        self.chars = self.__main_text + self.__gradle_generator.cradle_chars
        self.free = True
        self.done_generating = False

    def generate(self, frame_number: int):
        if self.free:
            self.__gradle_generator.update()
            self.free = False
        else:
            if frame_number % self.__halt == 0:
                self.free = self.__gradle_generator.push_ball()

        self.chars = self.__main_text + self.__gradle_generator.cradle_chars

    def mark_done(self, frame: int, message: str = "Done"):
        self.done_generating = True
        self.__gradle_generator.cradle_chars = list(message)
        self.__main_text = []
        self.generate(frame)


class Loading:
    def __init__(self, animate_part: GradientNoise, message_part: GenerateBubble | GenerateCradle):
        self.animate_part = animate_part
        self.message_part = message_part
    
    def update(self, frame: int):
        self.animate_part.generate(frame)
        if self.message_part and not self.message_part.done_generating:
            self.message_part.generate(frame)
    
    def mark_done(self, frame: int, message: str = "Done"):
        self.animate_part.mark_done()
        if self.message_part: self.message_part.mark_done(frame, message)
        

class StringStreamer:
    def __init__(self, x: int, y: int, text: str, start_frame: int, halt: int = 1):
        self.x = x
        self.y = y
        self.text = text
        self.__start_frame = start_frame
        self.__halt = halt
        self.__chars = list(self.text)
        self.elapsed = []
        self.complete = False
    
    def generate(self, frame: int):
        if self.complete or frame < self.__start_frame: return
        if frame % self.__halt == 0:
            self.elapsed.append(self.__chars[len(self.elapsed)])
            if len(self.elapsed) == len(self.__chars):
                self.complete = True


def main(screen: Screen) -> None:
    # loading = Loading(
    #     GradientNoise(x=0, y=1, length=30, char_halt=1, color_halt=20, gradient_length=5).update_gradient(
    #         [21, 57, 93, 129, 165, 201, 165, 129, 93, 57]
    #     ),
    #     GenerateBubble(x=31, y=1, bubbles=5, halt=20)
    # )
    
    count = 20
    
    loaders = [Loading(
        GradientNoise(x=0, y=i, length=30, char_halt=1, color_halt=1, gradient_length=5).update_gradient(
           [21, 57, 93, 129, 165, 201, 165, 129, 93, 57]
        ),
        None
    ) for i in range(count)]
    
    strings = [random.choice(["Hello", "Hello world", "Hello world from", "Hello world from main.py!"]) for _ in range(count)]

    streamers = [StringStreamer(
        x=31,
        y=i,
        text=strings[i],
        start_frame=0 if i == 0 else len(strings[i - 1]) * 2 + 1,
        halt=2
    ) for i in range(count)]
    
    
    back_buffer = Buffer(height=screen.height, width=screen.width)
    front_buffer = Buffer(height=screen.height, width=screen.width)

    current_frame = 0

    run = True

    try:
        while run:
            
            if streamers[-1].complete:
                run = False
                continue

            for idx in range(count):
                
                if streamers[idx].complete:
                    loaders[idx].mark_done(current_frame, "Message generated!")
                
                if idx != 0 and loaders[idx - 1].animate_part.done_generating:
                    loaders[idx].update(current_frame)
                elif idx == 0:
                    loaders[idx].update(current_frame)
                
                if idx != 0 and loaders[idx - 1].animate_part.done_generating:
                    streamers[idx].generate(current_frame)
                elif idx == 0:
                    streamers[idx].generate(current_frame)
            

                if idx != 0:
                    if loaders[idx -1].animate_part.done_generating:
                        for i, c in enumerate(loaders[idx].animate_part.colored_chars):
                            back_buffer.put_char(
                                loaders[idx].animate_part.x + i,
                                loaders[idx].animate_part.y, c.colored
                            )
                
                    if loaders[idx].message_part: 
                        for i, c in enumerate(loaders[idx].message_part.chars):
                            back_buffer.put_char(
                                loaders[idx].message_part.x + i,
                                loaders[idx].message_part.y,
                                c
                            )
                else:
                    for i, c in enumerate(loaders[idx].animate_part.colored_chars):
                        back_buffer.put_char(
                            loaders[idx].animate_part.x + i,
                            loaders[idx].animate_part.y, c.colored
                        )
                    if loaders[idx].message_part: 
                        for i, c in enumerate(loaders[idx].message_part.chars):
                            back_buffer.put_char(
                                loaders[idx].message_part.x + i,
                                loaders[idx].message_part.y,
                                c
                            )
        
                for i, c in enumerate(streamers[idx].elapsed):
                    back_buffer.put_char(
                        streamers[idx].x + i,
                        streamers[idx].y,
                        c
                    )

                if idx != 0:
                    if loaders[idx - 1].animate_part.done_generating:
                        for i, c in enumerate(streamers[idx].elapsed):
                            back_buffer.put_char(
                                streamers[idx].x + i,
                                streamers[idx].y,
                                c
                            )
                else:
                    for i, c in enumerate(streamers[idx].elapsed):
                            back_buffer.put_char(
                                streamers[idx].x + i,
                                streamers[idx].y,
                                c
                            )
                    
                for y, x, val in front_buffer.get_buffer_changes(back_buffer):
                    screen.print_at(val, x, y, 1)
                
            front_buffer.sync_with(back_buffer)
            time.sleep(0.01)
            current_frame += 1
        input()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    Screen.show(main)
