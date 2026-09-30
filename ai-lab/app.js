import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.2";

env.allowLocalModels = false;
env.useBrowserCache = true;

const $ = (id) => document.getElementById(id);
let generator = null;
let activeModel = "";

const MODEL_FILE = "./models.json";

function setStatus(text, tone="normal") {
  const el = $("status");
  el.textContent = text;
  el.dataset.tone = tone;
}

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = "msg " + role;
  el.textContent = text;
  $("messages").appendChild(el);
  el.scrollIntoView({ behavior: "smooth", block: "end" });
}

function taskInstruction(task) {
  const map = {
    chat: "Answer the user naturally and clearly.",
    explain: "Explain the user's request simply and step by step.",
    summarize: "Summarize the user's text accurately and briefly.",
    rewrite: "Rewrite the user's text clearly while keeping its meaning.",
    code: "Help with the user's programming request and provide usable code."
  };
  return map[task] || map.chat;
}

function extractText(output) {
  const value = output?.[0]?.generated_text;
  if (Array.isArray(value)) {
    const last = value[value.length - 1];
    return last?.content ?? JSON.stringify(last);
  }
  if (typeof value === "string") return value;
  return String(value ?? "");
}

async function loadModels() {
  const data = await fetch(MODEL_FILE).then(r => {
    if (!r.ok) throw new Error("Could not load model list.");
    return r.json();
  });

  const select = $("model");
  select.innerHTML = "";
  for (const item of data) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.name;
    option.title = item.note || "";
    select.appendChild(option);
  }
}

async function loadModel() {
  const model = $("customModel").value.trim() || $("model").value;
  if (!model) return;

  $("load").disabled = true;
  setStatus("Loading model… first load can take time and use storage.", "busy");

  try {
    const device = "gpu" in navigator ? "webgpu" : "wasm";
    generator = await pipeline("text-generation", model, {
      device,
      dtype: device === "webgpu" ? "q4f16" : "q8"
    });
    activeModel = model;
    setStatus("Model loaded. Inference runs in this browser.", "ok");
  } catch (error) {
    generator = null;
    activeModel = "";
    setStatus("Model load failed. Try the default model or another browser-compatible ONNX model.", "error");
    addMessage("ai", "Model error: " + (error?.message || error));
  } finally {
    $("load").disabled = false;
  }
}

$("load").addEventListener("click", loadModel);
$("clear").addEventListener("click", () => {
  $("messages").innerHTML = '<div class="welcome"><h2>Chat cleared</h2><p>Ask something new.</p></div>';
});
$("temperature").addEventListener("input", () => {
  $("tempValue").textContent = $("temperature").value;
});
$("model").addEventListener("change", () => {
  $("customModel").value = "";
});
$("customModel").addEventListener("input", () => {
  if ($("customModel").value.trim()) $("model").selectedIndex = -1;
});

$("chatForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const prompt = $("prompt").value.trim();
  if (!prompt) return;
  if (!generator) {
    addMessage("ai", "Pehle model select karke Load model dabao.");
    return;
  }

  addMessage("user", prompt);
  $("prompt").value = "";
  $("send").disabled = true;
  $("send").textContent = "…";

  try {
    const instruction = taskInstruction($("task").value);
    const messages = [
      { role: "system", content: instruction },
      { role: "user", content: prompt }
    ];
    setStatus("Generating with " + activeModel + "…", "busy");
    const output = await generator(messages, {
      max_new_tokens: 256,
      do_sample: true,
      temperature: Number($("temperature").value),
      top_p: 0.9,
      repetition_penalty: 1.05
    });
    addMessage("ai", extractText(output));
    setStatus("Done — inference stayed in the browser.", "ok");
  } catch (error) {
    addMessage("ai", "Generation error: " + (error?.message || error));
    setStatus("Generation failed.", "error");
  } finally {
    $("send").disabled = false;
    $("send").textContent = "Send";
  }
});

loadModels().catch(error => setStatus(error.message, "error"));