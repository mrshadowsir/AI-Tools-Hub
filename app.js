import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.7.2";

env.allowLocalModels = false;
env.useBrowserCache = true;

const $ = (id) => document.getElementById(id);
let generator = null;
let activeModel = "";

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
  return {
    chat: "Answer the user clearly and naturally.",
    explain: "Explain the user's request simply and step by step.",
    summarize: "Summarize the user's text accurately and briefly.",
    rewrite: "Rewrite the user's text clearly while keeping the meaning.",
    code: "Help with the programming request and provide usable code."
  }[task] || "Answer the user clearly and naturally.";
}

function extractText(output) {
  const value = output?.[0]?.generated_text;
  if (Array.isArray(value)) {
    const last = value[value.length - 1];
    return last?.content ?? JSON.stringify(last);
  }
  return typeof value === "string" ? value : String(value ?? "");
}

async function loadModelList() {
  const data = await fetch("./models.json").then(r => {
    if (!r.ok) throw new Error("Model list could not be loaded.");
    return r.json();
  });
  $("model").innerHTML = "";
  for (const item of data) {
    const o = document.createElement("option");
    o.value = item.id;
    o.textContent = item.name;
    o.title = item.note || "";
    $("model").appendChild(o);
  }
}

async function loadModel() {
  const model = $("customModel").value.trim() || $("model").value;
  if (!model) return;

  $("load").disabled = true;
  setStatus("Loading model… first load may take time.", "busy");
  try {
    const device = "gpu" in navigator ? "webgpu" : "wasm";
    generator = await pipeline("text-generation", model, {
      device,
      dtype: device === "webgpu" ? "q4f16" : "q8"
    });
    activeModel = model;
    setStatus("Model loaded — inference runs in this browser.", "ok");
  } catch (e) {
    generator = null;
    activeModel = "";
    setStatus("Model load failed. Try a browser-compatible ONNX model.", "error");
    addMessage("ai", "Model error: " + (e?.message || e));
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
$("model").addEventListener("change", () => $("customModel").value = "");

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
    setStatus("Generating with " + activeModel + "…", "busy");
    const output = await generator(
      [
        { role: "system", content: taskInstruction($("task").value) },
        { role: "user", content: prompt }
      ],
      {
        max_new_tokens: 256,
        do_sample: true,
        temperature: Number($("temperature").value),
        top_p: 0.9,
        repetition_penalty: 1.05
      }
    );
    addMessage("ai", extractText(output));
    setStatus("Done — inference stayed in the browser.", "ok");
  } catch (e) {
    addMessage("ai", "Generation error: " + (e?.message || e));
    setStatus("Generation failed.", "error");
  } finally {
    $("send").disabled = false;
    $("send").textContent = "Send";
  }
});

loadModelList().catch(e => setStatus(e.message, "error"));