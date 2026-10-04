(() => {
  const MAX_DIMENSION = 192;
  const upload = document.getElementById('svdUpload');
  const slider = document.getElementById('svdRank');
  const rankValue = document.getElementById('svdRankValue');
  const status = document.getElementById('svdStatus');
  const original = document.getElementById('svdOriginalImage');
  const canvas = document.getElementById('svdResultCanvas');
  if (!upload || !slider || !rankValue || !status || !original || !canvas) return;

  let activeJob = 0;
  let currentBlobUrl = null;
  let reconstruction = null;

  const nextFrame = () => new Promise(resolve => setTimeout(resolve, 0));

  function grayscalePixels(image) {
    const scale = Math.min(1, MAX_DIMENSION / Math.max(image.naturalWidth, image.naturalHeight));
    const width = Math.max(1, Math.round(image.naturalWidth * scale));
    const height = Math.max(1, Math.round(image.naturalHeight * scale));
    const sourceCanvas = document.createElement('canvas');
    sourceCanvas.width = width;
    sourceCanvas.height = height;
    const context = sourceCanvas.getContext('2d', { willReadFrequently: true });
    context.fillStyle = '#fff';
    context.fillRect(0, 0, width, height);
    context.drawImage(image, 0, 0, width, height);
    const imageData = context.getImageData(0, 0, width, height);
    const rgba = imageData.data;
    const pixels = new Float64Array(width * height);
    for (let i = 0; i < pixels.length; i += 1) {
      const offset = i * 4;
      const value = Math.round(0.299 * rgba[offset] + 0.587 * rgba[offset + 1] + 0.114 * rgba[offset + 2]);
      pixels[i] = value;
      rgba[offset] = value;
      rgba[offset + 1] = value;
      rgba[offset + 2] = value;
      rgba[offset + 3] = 255;
    }
    context.putImageData(imageData, 0, 0);
    return { pixels, width, height, preview: sourceCanvas.toDataURL('image/png') };
  }

  // One-sided Jacobi SVD: rotate image columns until they are orthogonal.
  // A = B V^T, so each approximation adds one sorted column of B V^T.
  async function decompose({ pixels, width, height }, job) {
    const transposed = width > height;
    const rows = transposed ? width : height;
    const columns = transposed ? height : width;
    const b = new Float64Array(rows * columns);
    const v = new Float64Array(columns * columns);

    for (let row = 0; row < rows; row += 1) {
      for (let column = 0; column < columns; column += 1) {
        b[row * columns + column] = transposed
          ? pixels[column * width + row]
          : pixels[row * width + column];
      }
    }
    for (let i = 0; i < columns; i += 1) v[i * columns + i] = 1;

    for (let sweep = 0; sweep < 12; sweep += 1) {
      let rotations = 0;
      for (let p = 0; p < columns - 1; p += 1) {
        for (let q = p + 1; q < columns; q += 1) {
          let alpha = 0;
          let beta = 0;
          let gamma = 0;
          for (let row = 0; row < rows; row += 1) {
            const offset = row * columns;
            const bp = b[offset + p];
            const bq = b[offset + q];
            alpha += bp * bp;
            beta += bq * bq;
            gamma += bp * bq;
          }
          if (Math.abs(gamma) <= 1e-7 * Math.sqrt(alpha * beta)) continue;

          const zeta = (beta - alpha) / (2 * gamma);
          const tangent = zeta >= 0
            ? 1 / (zeta + Math.sqrt(1 + zeta * zeta))
            : -1 / (-zeta + Math.sqrt(1 + zeta * zeta));
          const cosine = 1 / Math.sqrt(1 + tangent * tangent);
          const sine = cosine * tangent;
          for (let row = 0; row < rows; row += 1) {
            const offset = row * columns;
            const bp = b[offset + p];
            const bq = b[offset + q];
            b[offset + p] = cosine * bp - sine * bq;
            b[offset + q] = sine * bp + cosine * bq;
          }
          for (let row = 0; row < columns; row += 1) {
            const offset = row * columns;
            const vp = v[offset + p];
            const vq = v[offset + q];
            v[offset + p] = cosine * vp - sine * vq;
            v[offset + q] = sine * vp + cosine * vq;
          }
          rotations += 1;
        }
        if ((p & 7) === 7) {
          if (job !== activeJob) return null;
          await nextFrame();
        }
      }
      if (job !== activeJob) return null;
      if (rotations === 0) break;
      await nextFrame();
    }

    const order = Array.from({ length: columns }, (_, index) => {
      let energy = 0;
      for (let row = 0; row < rows; row += 1) {
        const value = b[row * columns + index];
        energy += value * value;
      }
      return { index, energy };
    }).sort((a, b) => b.energy - a.energy).map(component => component.index);

    return { b, v, order, rows, columns, width, height, transposed };
  }

  function addComponent(state, componentNumber, sign) {
    const { b, v, order, rows, columns, width, transposed } = state.decomposition;
    const component = order[componentNumber];
    for (let row = 0; row < rows; row += 1) {
      const scaled = sign * b[row * columns + component];
      for (let column = 0; column < columns; column += 1) {
        const pixelIndex = transposed ? column * width + row : row * width + column;
        state.accumulator[pixelIndex] += scaled * v[column * columns + component];
      }
    }
  }

  function draw(state) {
    const rgba = state.imageData.data;
    for (let i = 0; i < state.accumulator.length; i += 1) {
      const value = Math.max(0, Math.min(255, Math.round(state.accumulator[i])));
      const offset = i * 4;
      rgba[offset] = value;
      rgba[offset + 1] = value;
      rgba[offset + 2] = value;
      rgba[offset + 3] = 255;
    }
    state.context.putImageData(state.imageData, 0, 0);
  }

  function step(state) {
    if (state !== reconstruction) return;
    const difference = state.pendingRank - state.currentRank;
    const count = Math.min(8, Math.abs(difference));
    for (let i = 0; i < count; i += 1) {
      if (difference > 0) {
        addComponent(state, state.currentRank, 1);
        state.currentRank += 1;
      } else {
        state.currentRank -= 1;
        addComponent(state, state.currentRank, -1);
      }
    }
    draw(state);
    if (state.currentRank !== state.pendingRank) {
      setTimeout(() => step(state), 0);
    } else {
      state.frameRequested = false;
    }
  }

  function setRank(rank) {
    if (!reconstruction) return;
    reconstruction.pendingRank = rank;
    rankValue.value = String(rank);
    if (!reconstruction.frameRequested) {
      reconstruction.frameRequested = true;
      setTimeout(() => step(reconstruction), 0);
    }
  }

  async function useImage(source, label) {
    const job = ++activeJob;
    reconstruction = null;
    slider.disabled = true;
    status.textContent = `Preparing ${label}…`;
    original.src = source;
    try {
      await original.decode();
      if (job !== activeJob) return;
      const input = grayscalePixels(original);
      original.src = input.preview;
      status.textContent = 'Computing the approximation…';
      await nextFrame();
      const decomposition = await decompose(input, job);
      if (!decomposition || job !== activeJob) return;

      canvas.width = decomposition.width;
      canvas.height = decomposition.height;
      const context = canvas.getContext('2d');
      if (!context) throw new Error('Canvas is unavailable.');
      reconstruction = {
        decomposition,
        context,
        imageData: context.createImageData(canvas.width, canvas.height),
        accumulator: new Float64Array(canvas.width * canvas.height),
        currentRank: 0,
        pendingRank: 0,
        frameRequested: false,
      };
      slider.max = String(decomposition.columns);
      slider.value = String(Math.min(50, decomposition.columns));
      slider.disabled = decomposition.columns <= 1;
      status.textContent = 'Drag the rank slider to change the image.';
      setRank(Number(slider.value));
    } catch (error) {
      if (job === activeJob) status.textContent = 'Could not read that image. Try a PNG, JPEG, or WebP file.';
    }
  }

  slider.addEventListener('input', () => setRank(Number(slider.value)));
  upload.addEventListener('change', () => {
    const file = upload.files && upload.files[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      status.textContent = 'Choose an image file.';
      return;
    }
    const previousUrl = currentBlobUrl;
    currentBlobUrl = URL.createObjectURL(file);
    useImage(currentBlobUrl, 'your image');
    if (previousUrl) URL.revokeObjectURL(previousUrl);
  });

  useImage(original.src, 'the example image');
})();
