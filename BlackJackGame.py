
##              Blackjack game made by Zenny and OfficialVille
##              Card assets from: https://github.com/hayeah/playing-cards-assets
##              Free for use 

import random
import tkinter as tk
from tkinter import messagebox
import time
import os
from PIL import Image, ImageTk  # Importing from PIL (Pillow)

# Paths to the directories
cards_path = "Blackjack\\cards"
chips_path = "Blackjack\\chips"
save_file_path = "Blackjack\\save_data.txt"

# Global variables
bet = 0
balance = 0  # initialize this in the load_game_data function
player_hand = []
dealer_hand = []
show_dealer = False

# Card size
CARD_WIDTH = 222
CARD_HEIGHT = 323

# load bal from save 
def load_game_data():
    global balance  # Declare balance as global so we can modify it
    if os.path.exists(save_file_path):
        with open(save_file_path, 'r') as file:
            data = file.read().strip()
            if data.isdigit():
                balance = int(data)
    # If it is a invalid amount start with 1000
    if balance == 0:
        balance = 1000

# Function to save balance to file
def save_game_data():
    global balance  # Use global balance
    with open(save_file_path, 'w') as file:
        file.write(f"{balance}")

# Function to deal a card
def deal_card():
    cards = [f"{rank}_of_{suit}" for rank in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace'] for suit in ['clubs', 'diamonds', 'hearts', 'spades']]
    return random.choice(cards)

# Function to calculate a hand, including whether an Ace is present
def calculate_hand_value(hand):
    value = 0
    ace_count = 0
    for card in hand:
        rank = card.split("_")[0]  # Extract rank from '2_of_clubs'
        if rank in ['jack', 'queen', 'king']:
            value += 10
        elif rank == 'ace':
            value += 11
            ace_count += 1
        else:
            value += int(rank)
    
    # Adjust for aces
    while value > 21 and ace_count:
        value -= 10
        ace_count -= 1

    # If theres an ace, we return two possible values
    ace_in_hand = ace_count > 0 or 'ace' in [card.split("_")[0] for card in hand]
    return value, ace_in_hand

# Function to resize and display card images
def resize_card_image(card_path):
    image = Image.open(card_path)
    image = image.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)  # Resize the image to 222x323 pixels
    return ImageTk.PhotoImage(image)

# Update card display and animations
def update_display():
    global balance  
    player_value, player_has_ace = calculate_hand_value(player_hand)
    dealer_value, dealer_has_ace = calculate_hand_value(dealer_hand if show_dealer else dealer_hand[:1])
    
    # Update Player's hand on screen
    for i, card in enumerate(player_hand):
        card_img = resize_card_image(os.path.join(cards_path, f"{card}.png"))
        player_card_labels[i].config(image=card_img)
        player_card_labels[i].image = card_img  # Save reference to prevent garbage collection
    
    # Update Dealer's hand on screen
    for i, card in enumerate(dealer_hand if show_dealer else dealer_hand[:1]):
        card_img = resize_card_image(os.path.join(cards_path, f"{card}.png"))
        dealer_card_labels[i].config(image=card_img)
        dealer_card_labels[i].image = card_img
    
    # Update '?' for the dealer's hidden card
    if not show_dealer and len(dealer_hand) > 1:
        card_back_img = resize_card_image(os.path.join(cards_path, "back.png"))
        dealer_card_labels[1].config(image=card_back_img)
        dealer_card_labels[1].image = card_back_img

    # Update player's value on the screen, handling the ace
    if player_has_ace and player_value <= 21:
        player_value_label.config(text=f"Player: {player_value - 10} / {player_value}")
    else:
        player_value_label.config(text=f"Player: {player_value}")

    # Update dealer's value on the screen, handling the ace (if we are showing the full hand)
    if show_dealer:
        if dealer_has_ace and dealer_value <= 21:
            dealer_value_label.config(text=f"Dealer: {dealer_value - 10} / {dealer_value}")
        else:
            dealer_value_label.config(text=f"Dealer: {dealer_value}")
    else:
        dealer_value_label.config(text=f"Dealer: {dealer_value}")  # Only show one card value

    balance_label.config(text=f"Balance: ${balance}")
    
    # Check if player busts or has blackjack
    if player_value > 21:
        if not hasattr(update_display, 'bust_handled'):
            update_display.bust_handled = True
            messagebox.showinfo("Result", "Player busts! Dealer wins.")
            update_balance(-bet)
            reset_game()
    elif player_value == 21 and len(player_hand) == 2:
        messagebox.showinfo("Result", "Blackjack! Player wins!")
        update_balance(bet * 2.5)  # Pay out 2.5x for a blackjack
        reset_game()

# Deal cards with a delay to make it look more like a animation
def deal_card_with_animation(hand, is_player=True):
    hand.append(deal_card())  # Call the deal_card function here
    update_display()
    root.update()
    time.sleep(0.5)  # Simulate animation delay

# Clear the board (cards and values)
def clear_board():
    for label in player_card_labels + dealer_card_labels:
        label.config(image="")  # Clear the images
    player_value_label.config(text="Player: 0")
    dealer_value_label.config(text="Dealer: 0")

# Player hits (takes another card)
def hit():
    global balance  # Declare balance as global
    if bet > 0:
        deal_card_with_animation(player_hand)
        update_display()
        player_value, _ = calculate_hand_value(player_hand)
        if player_value == 21 and len(player_hand) == 2:
            messagebox.showinfo("Result", "Blackjack! Player wins!")
            update_balance(bet * 2.5)
            reset_game()
    else:
        messagebox.showwarning("Warning", "Please place a bet before hitting.")

# Player stands (ends their turn)
def stand():
    global show_dealer
    show_dealer = True
    dealer_turn()

# Dealer's turn logic
def dealer_turn():
    global balance  # Declare balance as global
    while calculate_hand_value(dealer_hand)[0] < 17:
        deal_card_with_animation(dealer_hand, is_player=False)
    
    dealer_value, _ = calculate_hand_value(dealer_hand)
    player_value, _ = calculate_hand_value(player_hand)
    update_display()

    if dealer_value > 21:
        messagebox.showinfo("Result", "Dealer busts! Player wins!")
        update_balance(bet * 2.5 if len(player_hand) == 2 and player_value == 21 else bet * 2)
    elif player_value > dealer_value:
        messagebox.showinfo("Result", "Player wins!")
        update_balance(bet * 2.5 if len(player_hand) == 2 and player_value == 21 else bet * 2)
    elif player_value < dealer_value:
        messagebox.showinfo("Result", "Dealer wins!")
    else:
        messagebox.showinfo("Result", "Push!")
        update_balance(bet)
    
    reset_game()

# Update balance and handle betting logic
def update_balance(amount):
    global balance  # Declare balance as global
    balance += amount
    save_game_data()  # Save after updating balance

    if balance <= 0:
        messagebox.showinfo("Game Over", "You are out of money!")
        root.quit()  # Exit the game if balance is zero or less

# Handle chip clicks to place bets
def place_bet(amount):
    global bet, balance  # Declare bet and balance as global
    if balance >= amount:
        bet += amount
        balance -= amount
        bet_label.config(text=f"Bet: ${bet}")
        balance_label.config(text=f"Balance: ${balance}")
    else:
        messagebox.showwarning("Insufficient Funds", "Not enough balance to place this bet.")
    save_game_data()  # Save balance after placing bet

def start_game():
    global player_hand, dealer_hand, show_dealer, bet  # Declare variables as global
    if bet > 0:
        player_hand = []
        dealer_hand = []
        show_dealer = False
        bet_label.config(text=f"Bet: ${bet}")
        clear_board()  # Clear the board before a new game
        deal_card_with_animation(player_hand)
        deal_card_with_animation(player_hand)
        deal_card_with_animation(dealer_hand, is_player=False)
        deal_card_with_animation(dealer_hand, is_player=False)
        start_button.config(state=tk.DISABLED)  # Disable start button after the game starts
        player_value, _ = calculate_hand_value(player_hand)
        if player_value == 21 and len(player_hand) == 2:
            messagebox.showinfo("Result", "Blackjack! Player wins!")
            update_balance(bet * 2.5)
            reset_game()
    else:
        messagebox.showwarning("No Bet", "Please place a bet before starting the game.")

# Reset the game for a new round
def reset_game():
    global bet  # Declare bet as global
    bet = 0
    bet_label.config(text=f"Bet: ${bet}")
    start_button.config(state=tk.NORMAL)  # Enable start button for the next round
    clear_board()  # Clear the board after the game ends
    update_display()
    # Reset bust flag
    if hasattr(update_display, 'bust_handled'):
        del update_display.bust_handled

# Create the main window
root = tk.Tk()
root.title("Blackjack")
root.configure(bg="green")

# Load the balance from the file
load_game_data()

# Make the window resizeable and center elements
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(4, weight=1)
root.grid_rowconfigure(5, weight=1)
root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)

# Create frames to hold card labels for player and dealer
player_card_frames = [tk.Frame(root, width=CARD_WIDTH, height=CARD_HEIGHT, bg="white") for _ in range(5)]
dealer_card_frames = [tk.Frame(root, width=CARD_WIDTH, height=CARD_HEIGHT, bg="white") for _ in range(5)]

# Create card labels for player and dealer
player_card_labels = [tk.Label(player_card_frames[i], bg="white") for i in range(5)]  # Initially white with no image
dealer_card_labels = [tk.Label(dealer_card_frames[i], bg="white") for i in range(5)]  # Initially white with no image

# Arrange frames and card labels in the grid
for i in range(5):
    player_card_frames[i].grid(row=3, column=i, padx=5, pady=5)
    player_card_labels[i].pack(fill=tk.BOTH, expand=True)  # Put the label inside the frame

    dealer_card_frames[i].grid(row=1, column=i, padx=5, pady=5)
    dealer_card_labels[i].pack(fill=tk.BOTH, expand=True)  # Put the label inside the frame

# Create balance and betting display
balance_label = tk.Label(root, text=f"Balance: ${balance}", font=("Helvetica", 14), bg="green", fg="black")
balance_label.grid(row=4, column=0, columnspan=2, pady=10, sticky="nsew")

bet_label = tk.Label(root, text=f"Bet: ${bet}", font=("Helvetica", 14), bg="green", fg="black")
bet_label.grid(row=4, column=2, columnspan=2, pady=10, sticky="nsew")

player_value_label = tk.Label(root, text="Player: 0", font=("Helvetica", 14), bg="green", fg="black")
player_value_label.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

dealer_value_label = tk.Label(root, text="Dealer: 0", font=("Helvetica", 14), bg="green", fg="black")
dealer_value_label.grid(row=0, column=0, columnspan=3, pady=10, sticky="nsew")

# Create chip buttons with smaller size
chip_size = (25, 25)  # Adjust chip size as needed
chip_20_img = ImageTk.PhotoImage(Image.open(os.path.join(chips_path, "20.png")).resize((75, 75), Image.LANCZOS))
chip_50_img = ImageTk.PhotoImage(Image.open(os.path.join(chips_path, "50.png")).resize((75, 75), Image.LANCZOS))
chip_100_img = ImageTk.PhotoImage(Image.open(os.path.join(chips_path, "100.png")).resize((75, 75), Image.LANCZOS))

chip_buttons = {
    20: tk.Button(root, image=chip_20_img, command=lambda: place_bet(20), bg="green"),
    50: tk.Button(root, image=chip_50_img, command=lambda: place_bet(50), bg="green"),
    100: tk.Button(root, image=chip_100_img, command=lambda: place_bet(100), bg="green")
}

chip_buttons[20].grid(row=5, column=0, padx=10, pady=10)
chip_buttons[50].grid(row=5, column=1, padx=10, pady=10)
chip_buttons[100].grid(row=5, column=2, padx=10, pady=10)

# Create buttons for "Hit", "Stand", and "Start"
hit_button = tk.Button(root, text="Hit", command=hit, font=("Helvetica", 14), bg="green")
hit_button.grid(row=6, column=0, pady=10, sticky="nsew")

stand_button = tk.Button(root, text="Stand", command=stand, font=("Helvetica", 14), bg="green")
stand_button.grid(row=6, column=1, pady=10, sticky="nsew")

start_button = tk.Button(root, text="Start", command=start_game, font=("Helvetica", 14), bg="green")
start_button.grid(row=6, column=2, pady=10, sticky="nsew")

# Start the GUI event loop
root.mainloop()
