import {
  DEFAULT_GRID_SIZE,
  createInitialState,
  restartGame,
  setDirection,
  stepGame,
  togglePause,
} from "./snake.js";

const TICK_MS = 140;

const boardElement = document.getElementById("board");
const scoreElement = document.getElementById("score");
const statusElement = document.getElementById("status");
const pauseButton = document.getElementById("pauseButton");
const restartButton = document.getElementById("restartButton");
const touchControlButtons = document.querySelectorAll(".touch-controls button[data-direction]");

let state = createInitialState({ gridSize: DEFAULT_GRID_SIZE });

function render() {
  const cells = new Array(state.gridSize * state.gridSize).fill("cell");

  for (const segment of state.snake) {
    const snakeIndex = segment.y * state.gridSize + segment.x;
    cells[snakeIndex] = `${cells[snakeIndex]} snake`;
  }

  if (state.food) {
    const foodIndex = state.food.y * state.gridSize + state.food.x;
    cells[foodIndex] = `${cells[foodIndex]} food`;
  }

  boardElement.innerHTML = cells.map((className) => `<div class="${className}"></div>`).join("");
  scoreElement.textContent = String(state.score);

  if (state.isGameOver) {
    statusElement.textContent = "Game over";
    pauseButton.disabled = true;
  } else if (state.isPaused) {
    statusElement.textContent = "Paused";
    pauseButton.disabled = false;
  } else {
    statusElement.textContent = "Running";
    pauseButton.disabled = false;
  }

  pauseButton.textContent = state.isPaused ? "Resume" : "Pause";
}

function handleDirectionInput(directionName) {
  state = setDirection(state, directionName);
  render();
}

function onKeyDown(event) {
  const keyMap = {
    ArrowUp: "up",
    ArrowDown: "down",
    ArrowLeft: "left",
    ArrowRight: "right",
    w: "up",
    W: "up",
    s: "down",
    S: "down",
    a: "left",
    A: "left",
    d: "right",
    D: "right",
  };

  if (event.key === " ") {
    event.preventDefault();
    state = togglePause(state);
    render();
    return;
  }

  const directionName = keyMap[event.key];
  if (!directionName) {
    return;
  }

  event.preventDefault();
  handleDirectionInput(directionName);
}

function tick() {
  state = stepGame(state);
  render();
}

pauseButton.addEventListener("click", () => {
  state = togglePause(state);
  render();
});

restartButton.addEventListener("click", () => {
  state = restartGame(state);
  render();
});

touchControlButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const directionName = button.getAttribute("data-direction");
    handleDirectionInput(directionName);
  });
});

document.addEventListener("keydown", onKeyDown);

setInterval(tick, TICK_MS);
render();