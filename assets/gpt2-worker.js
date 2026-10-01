import { pipeline, env } from 'https://cdn.jsdelivr.net/npm/@xenova/transformers@2.17.2';

env.allowLocalModels = false;

let generatorPromise = null;

function getGenerator() {
  if (!generatorPromise) {
    generatorPromise = pipeline('text-generation', 'Xenova/gpt2', {
      quantized: true,
      progress_callback: ({ status, file, progress }) => {
        if (status === 'progress' && file?.endsWith('.onnx') && Number.isFinite(progress)) {
          self.postMessage({ type: 'progress', percent: Math.round(progress) });
        }
      },
    });
  }
  return generatorPromise;
}

self.onmessage = async ({ data }) => {
  if (data.type === 'load') {
    try {
      await getGenerator();
      self.postMessage({ type: 'ready' });
    } catch {
      generatorPromise = null;
      self.postMessage({ type: 'error', stage: 'load' });
    }
  } else if (data.type === 'generate') {
    try {
      const generator = await getGenerator();
      const output = await generator(data.prompt, {
        max_new_tokens: 64,
        do_sample: true,
        temperature: 0.8,
        top_k: 50,
        return_full_text: false,
      });
      const raw = output[0]?.generated_text ?? '';
      const text = String(raw).split(/\n(?:Human|Assistant):/)[0].trim();
      self.postMessage({ type: 'result', text });
    } catch {
      self.postMessage({ type: 'error', stage: 'generate' });
    }
  }
};
