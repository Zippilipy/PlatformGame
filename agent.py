import torch
import random
import pygame, sys
from level import Level
from collections import deque
from player import Player
from model import Linear_QNet, QTrainer
from helper import plot
from settings import start_map, level_map, screen_width, screen_height


MAX_MEMORY = 100000
BATCH_SIZE = 1000
LR = 0.001


class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(209, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, level):
        state = level.get_state(level.player.sprite.rect.x, level.realxpos, level.player.sprite.rect.y, level.continue_level)
        return state

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) < BATCH_SIZE:
            mini_sample = random.choices(self.memory, k=BATCH_SIZE)
        else:
            mini_sample = self.memory


        new_memory = []

        memory_count = 1
        for memory in self.memory:
            if memory_count > len(self.memory) - 10:
                new_memory.append(memory)
            memory_count += 1

        mini_sample = new_memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)

        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves
        self.epsilon = 1-self.n_games/10
        final_move = 0
        if random.random() < self.epsilon:
            final_move = random.randint(0, 2)
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            final_move = torch.argmax(prediction).item()
        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    pygame.init()
    clock = pygame.time.Clock()
    agent = Agent()
    screen = pygame.display.set_mode((screen_width, screen_height))
    level = Level(start_map, level_map, screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill('black')
        level.run()

        pygame.display.update()
        clock.tick(-1)
        # get old state
        state_old = agent.get_state(level)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = level.input(final_move)
        state_new = agent.get_state(level)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            level.restart()
            agent.n_games += 1
            agent.train_long_memory()
            #agent.train_short_memory(state_old, final_move, reward, state_new, done)

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score,', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()
