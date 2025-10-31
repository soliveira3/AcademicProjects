import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# inputting and parsing data
data = pd.read_csv('D3.csv')
X = data.iloc[:, :-1].values
y = data.iloc[:, -1].values.reshape(-1, 1)
m, n = X.shape

# Standardizing the data
# I used the standardization on page 46 of lecture 4
mean = np.mean(X, 0)
stdDev = np.std(X, 0)
X = (X - mean) / stdDev
X = np.c_[np.ones((m, 1)), X]

# Setting the variables for gradient decent
theta = np.zeros((n+1, 1))
learningRate = 0.01
costFunction = []

# Doing gradient decent
for i in range(15000):
    # Calculate the hypothesis values using matrix multiplication
    h = X.dot(theta)
    # Calculate the error
    # This is the cost function that will measure our error
    # We are using squared distance as our cost function
    # (1 / (2*m)) * sum( (h - y) ^ 2 )
    costFunction.append((1/(2*m)) * np.sum(np.square(h - y)))
    error = np.dot(X.T, (h - y))
    # Update theta
    # We are multiplying by the learning rate and then scaling by m and multiplying by the error
    theta -= (learningRate / m) * error

# Plotting the cost function
plt.plot(range(15000), costFunction)
plt.ylabel('Cost J(Theta)')
plt.show()

# Convert coefficients back to no standardization
finalTheta = theta.copy()
finalTheta[0] = theta[0] - np.sum(theta[1:].T * mean/stdDev)
finalTheta[1:] = theta[1:] / stdDev.reshape(-1, 1)

# Printing final coefficients
print("\nFinal Coefficients:\n")
for i in range(4):
    print(f"\tTheta {i}'s Coefficient: {finalTheta[i][0]:.6f}")

# Predict h for the new x values and applying the same process as earlier
newX = np.array([[1, 1, 1], [2, 0, 4], [3, 2, 1]])
newX = (newX - mean) / stdDev
newX = np.c_[np.ones((newX.shape[0], 1)), newX]

# Make h using the final learned coefficients.
h = np.dot(newX, theta)

# Outputting our predicted values for the new input
print("\nPredicted y values for new input:\n")
for i, pred in enumerate(h):
    print(f"\t({newX[i, 0]}, {newX[i, 1]}, {newX[i, 2]}): {pred[0]:.6f}")
    print("\n")
