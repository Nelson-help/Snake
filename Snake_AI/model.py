from Constants import MAX_MEMORY, BATCH_SIZE, LEARNING_RATE, LEARNING_GAMMA
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as func
import os # Operating System
import random

class LinearQNet(nn.Module):
    modelPath = os.path.join(os.path.dirname(__name__), "model.pth")
    def __init__(self, input_count, hidden_count, output_count):
        super().__init__()

        self.linear1 = nn.Linear(input_count, hidden_count)
        self.linear2 = nn.Linear(hidden_count, output_count)
        if os.path.exists(self.modelPath): self.load() # If path exists, load model

    def forward(self, x):
        x = func.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
    def load(self):
        state_dict = torch.load(self.modelPath)
        print("Loaded", state_dict["linear1.weight"][0][:11], state_dict["linear2.weight"][0][:11])
        self.load_state_dict(state_dict) # Weights_only means only the weight, not node
    
    def save(self):
        state_dict = self.state_dict()
        print("Saved", state_dict["linear1.weight"][0][:11], state_dict["linear2.weight"][0][:11])
        torch.save(state_dict, self.modelPath)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr
        self.gamma = gamma
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss() # Mean Squared Error 
    
    def trainStep(self, state, action, reward, next_state, important):
        state = torch.tensor(state, dtype = torch.float)
        action = torch.tensor(action, dtype = torch.long)
        reward = torch.tensor(reward, dtype = torch.float)
        next_state = torch.tensor(next_state, dtype = torch.float)
        
        pred = self.model(state)

        target = pred.clone()
        if not important:
            Q_new = reward + self.gamma * torch.max(self.model(next_state))
        else:
            Q_new = reward
        target[torch.argmax(action).item()] = Q_new # argmax = index of the max argument

        self.optimizer.zero_grad()

        loss = self.criterion(pred, target)
        loss.backward()
        self.optimizer.step()

class QBrain:
    def __init__(self) -> None:
        self.memory = []
        self.model = LinearQNet(11, 256, 3) # Neuron model
        self.trainer = QTrainer(self.model, lr = LEARNING_RATE, gamma = LEARNING_GAMMA)

    def think(self, currentState, useRandom):
        action = [0, 0, 0] # 3 booleans [3 directions]
        if useRandom:
            action[random.randint(0, 2)] = 1 # Random choose one direction to make True
        else:
            stateInput = torch.tensor(currentState, dtype = torch.float) # dtype = data type
            prediction = self.model(stateInput)
            bestIndex = int(torch.argmax(prediction).item()) # item() = Value of the tensor as a no.
            action[bestIndex] = 1 # Changes the "bestIndex"th variable of the list to 1
        return action

    def memorize(self, state, action, reward, next_state, important):
        self.memory.append((state, action, reward, next_state, important)) # Record the stats of each movement
        if len(self.memory) > MAX_MEMORY: self.memory.pop(0) # Remove from memory [pop() = remove nth value]

        if not important:
            self.trainer.trainStep(state, action, reward, next_state, important)
            return
        
        if len(self.memory) > BATCH_SIZE: # import old learning
            sample_memory = random.sample(self.memory, BATCH_SIZE) # Choose BATCH_SIZE of memories from self.memory
        else:
            sample_memory = self.memory

        for state, action, reward, next_state, important in sample_memory:
            self.trainer.trainStep(state, action, reward, next_state, important)
