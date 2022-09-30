#! /bin/env python3

import sys
import string

from itertools import product, combinations_with_replacement
from random import shuffle

N_LETTERS_MIN, N_LETTERS_MAX = 10, 20
N_HOLES_MIN, N_HOLES_MAX = 4, 20
CORRECT_POS_IDX, CORRECT_COL_IDX = 0, 1

class FastBrain:
	def __init__(self, n_letters, n_holes, max_attempts):
		self.letters = string.ascii_lowercase[:N_LETTERS_MIN]
		self.n_holes = N_HOLES_MIN
		self.max_attempts = max_attempts
		self.n_attempts = 0
		self.initial_combos = self.possible_combos = [ _ for _ in product(self.letters, repeat=self.n_holes)]
		shuffle(self.possible_combos)
		self.possible_responses = self.generate_possible_responses()
		self.used_illogical_solution = False

	def loop(self):
		while ((self.n_attempts < self.max_attempts) and self.possible_combos):
			self.proposition = self.minimax(self.possible_combos)
			print(*self.proposition, sep='')
			self.n_attempts += 1
			self.response = self.prompt_user()
			if (self.response[CORRECT_POS_IDX] == self.n_holes):
				return
			self.possible_combos = self.remove_impossible_combos(self.proposition, self.response, self.possible_combos)

	def generate_possible_responses(self):
		res = []
		for pos_or_col in range(self.n_holes + 1):
			for pos in range(pos_or_col + 1):
				res.append((pos, pos_or_col - pos))
		return res

	def minimax(self, combos):
		shuffle(combos)
		if len(combos) == 1:
			return combos[0]
		if self.n_attempts == 0:
			for combo in combos:
				if len(set(combo)) == 2 and combo.count(combo[0]) == 2:
					return combo
		if self.n_attempts == 1 and self.response == (0, 0):
			for combo in combos:
				if len(set(combo)) == 3:
					return combo
		if len(combos) <= 1000:
			pool = self.initial_combos
		else:
			pool = combos[:min(len(combos), 2048)]
		res, mini = combos[0], self.get_max(pool[0], combos)
		for combo in pool[1:]:
			tmp = self.get_max(combo, combos)
			if tmp < mini or (tmp == mini and combo in combos):
				res, mini = combo, tmp
		return res

	def get_max(self, candidate, combos):
		maxi = 0
		for response in self.possible_responses:
			tmp = self.count_compatible_combos(candidate, response, combos)
			maxi = max(maxi, tmp)
		return maxi

	def count_compatible_combos(self, candidate, response, combos):
		return sum(self.is_possible_combo(candidate, response, combo) for combo in combos)

	def prompt_user(self):
		good_pos = int(input("Good position: "))
		bad_pos = int(input("Bad position: "))
		return good_pos, bad_pos

	def remove_impossible_combos(self, proposition, response, combos):
		res = []
		for combo in combos:
			if self.is_possible_combo(proposition, response, combo):
				res.append(combo)
		return res

	def is_possible_combo(self, proposition, response, combo):
		mask1 = mask2 = [a == b for a,b in zip(proposition, combo)]
		if sum(mask1) != response[0]:
			return False
		misplaced = 0
		for i, letter1 in enumerate(proposition):
			if mask1[i]:
				continue
			for j, letter2 in enumerate(combo):
				if letter1 == letter2 and (letter2 != proposition[j] or mask1[j]) and not mask2[j]:
					mask2[j] = 1
					misplaced += 1
					break
		return misplaced == response[1]

def valid_args(av) -> bool:
	if len(av) != 4:
		return False
	try:
		n_letters, n_holes, max_attempts = [int(a) for a in av[1:]]
	except:
		return False
	if (n_letters not in [N_LETTERS_MIN, N_LETTERS_MAX]) \
		or (n_holes not in [N_HOLES_MIN, N_HOLES_MAX]) \
		or (max_attempts < 1):
		return False
	return True

def main(av):
	if not valid_args(av):
		print("Usage: player.py n_letters(10 or 20) n_positions(4 or 20) max_attempts")
	args = [int(a) for a in av[1:]]
	match args[1:3]:
		case (N_LETTERS_MIN, N_HOLES_MIN):
			player = FastBrain(*args)
		case _:
			print("Unknown game type")
			exit(1)
	player.loop()

if __name__ == "__main__":
	main(sys.argv)