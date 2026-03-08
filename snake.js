export const DEFAULT_GRID_SIZE = 20;

const DIRECTION_VECTORS = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

function isSamePosition(a, b) {
  return a.x === b.x && a.y === b.y;
}

function isOppositeDirection(current, next) {
  return current.x + next.x === 0 && current.y + next.y === 0;
}

function randomInt(max, rng) {
  return Math.floor(rng() * max);
}

function createInitialSnake(gridSize) {
  const center = Math.floor(gridSize / 2);
  return [
    { x: center, y: center },
    { x: center - 1, y: center },
    { x: center - 2, y: center },
  ];
}

export function placeFood(gridSize, snake, rng = Math.random) {
  const occupied = new Set(snake.map((segment) => `${segment.x},${segment.y}`));
  const freeCells = [];

  for (let y = 0; y < gridSize; y += 1) {
    for (let x = 0; x < gridSize; x += 1) {
      const key = `${x},${y}`;
      if (!occupied.has(key)) {
        freeCells.push({ x, y });
      }
    }
  }

  if (freeCells.length === 0) {
    return null;
  }

  return freeCells[randomInt(freeCells.length, rng)];
}

export function createInitialState({ gridSize = DEFAULT_GRID_SIZE, rng = Math.random } = {}) {
  const snake = createInitialSnake(gridSize);

  return {
    gridSize,
    snake,
    direction: DIRECTION_VECTORS.right,
    queuedDirection: null,
    food: placeFood(gridSize, snake, rng),
    score: 0,
    isPaused: false,
    isGameOver: false,
  };
}

export function setDirection(state, directionName) {
  const nextDirection = DIRECTION_VECTORS[directionName];
  if (!nextDirection || state.isGameOver) {
    return state;
  }

  const activeDirection = state.queuedDirection ?? state.direction;
  if (isOppositeDirection(activeDirection, nextDirection)) {
    return state;
  }

  return { ...state, queuedDirection: nextDirection };
}

function collidesWithSelf(nextHead, snake, willGrow) {
  const bodyToCheck = willGrow ? snake : snake.slice(0, -1);
  return bodyToCheck.some((segment) => isSamePosition(segment, nextHead));
}

function outOfBounds(position, gridSize) {
  return position.x < 0 || position.x >= gridSize || position.y < 0 || position.y >= gridSize;
}

export function togglePause(state) {
  if (state.isGameOver) {
    return state;
  }

  return { ...state, isPaused: !state.isPaused };
}

export function restartGame(state, rng = Math.random) {
  return createInitialState({ gridSize: state.gridSize, rng });
}

export function stepGame(state, rng = Math.random) {
  if (state.isPaused || state.isGameOver) {
    return state;
  }

  const direction = state.queuedDirection ?? state.direction;
  const head = state.snake[0];
  const nextHead = { x: head.x + direction.x, y: head.y + direction.y };

  if (outOfBounds(nextHead, state.gridSize)) {
    return {
      ...state,
      direction,
      queuedDirection: null,
      isGameOver: true,
    };
  }

  const willGrow = state.food !== null && isSamePosition(nextHead, state.food);
  if (collidesWithSelf(nextHead, state.snake, willGrow)) {
    return {
      ...state,
      direction,
      queuedDirection: null,
      isGameOver: true,
    };
  }

  const nextSnake = [nextHead, ...state.snake];
  if (!willGrow) {
    nextSnake.pop();
  }

  const nextFood = willGrow ? placeFood(state.gridSize, nextSnake, rng) : state.food;
  const isBoardFull = willGrow && nextFood === null;

  return {
    ...state,
    snake: nextSnake,
    direction,
    queuedDirection: null,
    food: nextFood,
    score: state.score + (willGrow ? 1 : 0),
    isGameOver: isBoardFull,
  };
}