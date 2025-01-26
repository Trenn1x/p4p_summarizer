import pygame
import random
import json
from os import path
from datetime import datetime, timedelta

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Pop Language Learning")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

# Fonts
FONT_SIZE = 36
font = pygame.font.Font(None, FONT_SIZE)

# File paths
WORDS_FILE = path.join("data", "words.json")

# Load and save words
def load_words():
    """Load words from a JSON file. Initialize with default data if the file is empty or invalid."""
    default_words = [
        {"word": "Hola", "translation": "Hello", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "Adiós", "translation": "Goodbye", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "Gracias", "translation": "Thank you", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "Por favor", "translation": "Please", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "Sí", "translation": "Yes", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "No", "translation": "No", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "Buenos días", "translation": "Good morning", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "Buenas noches", "translation": "Good night", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "¿Cómo estás?", "translation": "How are you?", "confidence": 0, "last_shown": None, "interval": 1},
        {"word": "Estoy bien", "translation": "I am fine", "confidence": 0, "last_shown": None, "interval": 1}
    ]

    if not path.exists(WORDS_FILE):
        # Create the file with default data
        with open(WORDS_FILE, "w") as file:
            json.dump(default_words, file, indent=4)
        return default_words

    try:
        with open(WORDS_FILE, "r") as file:
            data = json.load(file)
            if not data:  # If the file is empty
                raise ValueError("File is empty")
            return data
    except (json.JSONDecodeError, ValueError):
        # If the file is invalid or empty, overwrite it with default data
        with open(WORDS_FILE, "w") as file:
            json.dump(default_words, file, indent=4)
        return default_words

# Save words
def save_words(words):
    """Save words to a JSON file."""
    with open(WORDS_FILE, "w") as file:
        json.dump(words, file, indent=4)

# Load initial words
words = load_words()

# Bubble class
class Bubble:
    def __init__(self, x, y, word, translation, confidence):
        self.x = x
        self.y = y
        self.word = word
        self.translation = translation
        self.popped = False
        self.confidence = confidence
        self.shown_in_session = False

        # Load images based on confidence level
        if confidence <= 2:
            # Low confidence: Use blue unpopped bubble
            self.image = pygame.image.load(path.join("images", "bubbles_blue_unpopped_whitebackground_regularsize.png"))
        elif confidence == 3:
            # Medium confidence: Use glowing unpopped bubble
            self.image = pygame.image.load(path.join("images", "bubbles_glowing_unpopped_whitebackground_regularsize.png"))
        else:
            # High confidence: Use blue unpopped bubble (or another variant)
            self.image = pygame.image.load(path.join("images", "bubbles_blue_unpopped_whitebackground_regularsize_2.png"))

        # Load popped image
        self.popped_image = pygame.image.load(path.join("images", "bubbles_blue_popped_whitebackground_regularsize.png"))

    def draw(self, screen):
        """Draw the bubble on the screen."""
        if self.popped:
            screen.blit(self.popped_image, (self.x, self.y))
            # Display the translation
            text = font.render(self.translation, True, BLACK)
            screen.blit(text, (self.x + 20, self.y + 50))
        else:
            screen.blit(self.image, (self.x, self.y))
            # Display the word
            text = font.render(self.word, True, BLACK)
            screen.blit(text, (self.x + 20, self.y + 50))

    def is_popped(self, mouse_pos):
        """Check if the bubble is popped."""
        bubble_rect = self.image.get_rect(topleft=(self.x, self.y))
        return bubble_rect.collidepoint(mouse_pos)

# Create bubbles
def create_bubbles():
    bubbles = []
    bubble_spacing = 150  # Space between bubbles
    start_x = 100  # Starting X position
    start_y = 100  # Starting Y position

    # Filter words based on interval and last_shown
    now = datetime.now()
    eligible_words = [
        word for word in words
        if word["last_shown"] is None or
        (now - datetime.fromisoformat(word["last_shown"])) >= timedelta(days=word["interval"])
    ]

    if not eligible_words:
        # If no words are eligible, reset intervals for all words
        for word in words:
            word["interval"] = 1
            word["last_shown"] = None
        eligible_words = words  # Use all words

    # Adjust proportions based on confidence
    low_confidence_words = [word for word in eligible_words if word["confidence"] <= 3]
    high_confidence_words = [word for word in eligible_words if word["confidence"] >= 4]

    # Ensure at least 3 bubbles are shown
    total_bubbles = 12  # 3 rows x 4 columns

    # Calculate the number of low-confidence and high-confidence bubbles
    low_confidence_count = min(len(low_confidence_words), total_bubbles // 2)
    high_confidence_count = min(len(high_confidence_words), total_bubbles - low_confidence_count)

    # If there aren't enough words, adjust the counts
    if low_confidence_count + high_confidence_count < total_bubbles:
        # Add more words from the other category
        if len(low_confidence_words) > low_confidence_count:
            low_confidence_count = min(len(low_confidence_words), total_bubbles)
        elif len(high_confidence_words) > high_confidence_count:
            high_confidence_count = min(len(high_confidence_words), total_bubbles)

    # Randomly select words based on confidence
    selected_words = []
    if low_confidence_words and low_confidence_count > 0:
        selected_words.extend(random.sample(low_confidence_words, low_confidence_count))
    if high_confidence_words and high_confidence_count > 0:
        selected_words.extend(random.sample(high_confidence_words, high_confidence_count))

    # If there still aren't enough words, shuffle and repeat some words
    while len(selected_words) < total_bubbles:
        random.shuffle(eligible_words)
        selected_words.extend(eligible_words[:total_bubbles - len(selected_words)])

    # Shuffle the selected words to avoid contiguous duplicates
    random.shuffle(selected_words)

    # Ensure no contiguous duplicates
    for i in range(1, len(selected_words)):
        if selected_words[i]["word"] == selected_words[i - 1]["word"]:
            # Swap with a random word to break the sequence
            swap_index = random.randint(0, len(selected_words) - 1)
            selected_words[i], selected_words[swap_index] = selected_words[swap_index], selected_words[i]

    # Place bubbles on the grid
    for i in range(3):  # 3 rows
        for j in range(4):  # 4 columns
            if not selected_words:
                break
            word_data = selected_words.pop()
            bubble = Bubble(
                start_x + j * bubble_spacing,  # X position
                start_y + i * bubble_spacing,  # Y position
                word_data["word"],
                word_data["translation"],
                word_data["confidence"]  # Pass the confidence value
            )
            bubble.shown_in_session = True  # Mark as shown in the current session
            bubbles.append(bubble)
    return bubbles

def pop_quiz(pop_sound):  # Accept pop_sound as an argument
    clock = pygame.time.Clock()
    quiz_time = 60  # 60 seconds
    start_time = pygame.time.get_ticks()
    running = True

    # Create bubbles for all mastered words
    mastered_words = [word for word in words if word["confidence"] >= 4]
    bubbles = []
    for word_data in mastered_words:
        bubble = Bubble(
            random.randint(50, WIDTH - 100),  # Random X position
            random.randint(50, HEIGHT - 100),  # Random Y position
            word_data["word"],
            word_data["translation"],
            word_data["confidence"]
        )
        bubbles.append(bubble)

    while running:
        # Draw gradient background
        draw_gradient_background(screen)

        # Calculate remaining time
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        remaining_time = quiz_time - elapsed_time

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return  # Exit the pop quiz and return to the main game
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for bubble in bubbles:
                    if bubble.is_popped(mouse_pos) and not bubble.popped:
                        bubble.popped = True
                        if pop_sound:
                            pop_sound.play()  # Play pop sound

        # Draw bubbles
        for bubble in bubbles:
            bubble.draw(screen)

        # Draw timer
        timer_text = font.render(f"Time: {remaining_time}", True, BLACK)
        screen.blit(timer_text, (10, 10))

        # Check if time is up
        if remaining_time <= 0:
            text = font.render("Time's up! Great job!", True, GREEN)
            screen.blit(text, (WIDTH // 2 - 150, HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(3000)  # Wait 3 seconds before exiting
            running = False

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(30)

# Draw gradient background
def draw_gradient_background(screen):
    """Draw a gradient background."""
    for y in range(HEIGHT):
        color = (
            int(255 * (y / HEIGHT)),  # Red
            int(255 * (y / HEIGHT)),  # Green
            255  # Blue
        )
        pygame.draw.line(screen, color, (0, y), (WIDTH, y))

def main():
    global words
    clock = pygame.time.Clock()
    running = True
    current_bubble = None
    game_over = False  # Track if the game is over

    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load sounds
    try:
        pop_sound = pygame.mixer.Sound(path.join("sounds", "463392__vilkas_sound__vs-pop_8.mp3"))
    except FileNotFoundError:
        print("Error: Sound file not found. Please check the file path.")
        pop_sound = None  # Set to None to avoid crashes when playing the sound

    # Initialize bubbles
    bubbles = create_bubbles()

    while running:
        # Draw gradient background
        draw_gradient_background(screen)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if current_bubble is None and not game_over:  # Only allow clicking if no bubble is currently selected
                    mouse_pos = pygame.mouse.get_pos()
                    for bubble in bubbles:
                        if bubble.is_popped(mouse_pos) and not bubble.popped:
                            bubble.popped = True
                            if pop_sound:
                                pop_sound.play()  # Play pop sound
                            current_bubble = bubble
                            break  # Only allow one bubble to be clicked at a time
            if event.type == pygame.KEYDOWN:
                if current_bubble:
                    if event.key == pygame.K_1:
                        current_bubble.confidence = 1
                    elif event.key == pygame.K_2:
                        current_bubble.confidence = 2
                    elif event.key == pygame.K_3:
                        current_bubble.confidence = 3
                    elif event.key == pygame.K_4:
                        current_bubble.confidence = 4
                    elif event.key == pygame.K_5:
                        current_bubble.confidence = 5

                    # Update word confidence and interval
                    for word_data in words:
                        if word_data["word"] == current_bubble.word:
                            word_data["confidence"] = current_bubble.confidence
                            word_data["last_shown"] = datetime.now().isoformat()
                            if current_bubble.confidence <= 2:
                                word_data["interval"] = 1  # Show soon
                            elif current_bubble.confidence == 3:
                                word_data["interval"] = 3  # Show in 3 days
                            elif current_bubble.confidence == 4:
                                word_data["interval"] = 7  # Show in 1 week
                            elif current_bubble.confidence == 5:
                                word_data["interval"] = 30  # Show in 1 month
                            break

                    save_words(words)
                    current_bubble = None  # Reset current bubble after rating

                    # Check if all bubbles on the current board are popped
                    if all(bubble.popped for bubble in bubbles):
                        bubbles = create_bubbles()  # Refresh bubbles

        # Check if all words are mastered
        all_mastered = all(word["last_shown"] is not None and word["confidence"] >= 4 for word in words)

        # Draw bubbles
        for bubble in bubbles:
            bubble.draw(screen)

        # Draw confidence rating instructions
        if current_bubble:
            text = font.render(f"Rate your confidence for: {current_bubble.word}", True, BLACK)
            screen.blit(text, (10, HEIGHT - 100))
            text = font.render("1: Not confident", True, BLACK)
            screen.blit(text, (10, HEIGHT - 70))
            text = font.render("5: Very confident", True, BLACK)
            screen.blit(text, (10, HEIGHT - 40))

        # Display a message if all words are mastered
        if all_mastered and not game_over:
            game_over = True
            text = font.render("Congratulations! You've mastered all words!", True, GREEN)
            screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
            text = font.render("Press SPACE to start the Pop Quiz!", True, GREEN)
            screen.blit(text, (WIDTH // 2 - 200, HEIGHT // 2))
            pygame.display.flip()

            # Wait for SPACE key to start the Pop Quiz
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        waiting = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            pop_quiz(pop_sound)  # Pass pop_sound to the pop_quiz function
                            waiting = False

        # Update the display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()