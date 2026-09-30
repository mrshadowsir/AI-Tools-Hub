import { pipeline, env } from "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1";
env.allowLocalModels=false;env.useBrowserCache=true;env.useWasmCache=true;
const $=id=>document.getElementById(id);
const cache=new Map();let categories=[],categoryModels=[],filteredModels=[],selectedModel="onnx-community/SmolLM2-360M-Instruct-ONNX",loaded=null,loadedTask="",loadedModel="",mode="chat",presets=null,imageBlob=null,audioBlob=null,videoUrl="",frameBlob=null,limit=100;
const HISTORY="ai-tools-hub-history-v3";
const WEB_TEXT_MODELS=new Set(["onnx-community/SmolLM2-360M-Instruct-ONNX","onnx-community/Qwen2.5-0.5B-Instruct"]);
function isBrowserTextModel(name){return WEB_TEXT_MODELS.has(name)}
function syncLoadButton(){
  const ready=isBrowserTextModel(selectedModel);
  $("loadModel").disabled=!ready;
  $("loadModel").textContent=ready?"⚡ Load model":"📚 Catalog only";
}
function selectModel(m){
  selectedModel=m.name;
  $("selectedModel").innerHTML="<b>"+m.name+"</b><span>"+m.family+" • "+m.license+" • "+m.category+"</span>";
  paint();
  status(isBrowserTextModel(m.name)?"Browser-ready model selected. Click Load model.":"Catalog model selected — this exact model is not confirmed browser/ONNX compatible. Choose a Browser-ready model to run it.");
  syncLoadButton();
}
function loadSelectedTextModel(){
  if(!isBrowserTextModel(selectedModel)){
    status("This model is catalog-only here. Choose SmolLM2 360M or Qwen2.5 0.5B browser preset.","error");
    return;
  }
  pipe("text-generation",selectedModel).catch(e=>status("Browser model failed to load: "+(e?.message||e),"error"));
}

function status(t,tone="normal"){const e=$("status");e.textContent=t;e.dataset.tone=tone}
function add(role,t){const e=document.createElement("div");e.className="msg "+role;e.textContent=t;$("messages").appendChild(e);e.scrollIntoView({behavior:"smooth",block:"end"})}
function msgs(){return [...$("messages").querySelectorAll(".msg")].map(e=>({role:e.classList.contains("user")?"user":"assistant",text:e.textContent}))}
function saveHistory(title,items){try{const a=JSON.parse(localStorage.getItem(HISTORY)||"[]");a.unshift({id:String(Date.now()),title,model:loadedModel||selectedModel,time:new Date().toLocaleString(),items});localStorage.setItem(HISTORY,JSON.stringify(a.slice(0,50)))}catch{}}
function history(){const box=$("historyList"),a=JSON.parse(localStorage.getItem(HISTORY)||"[]");box.innerHTML="";if(!a.length){box.innerHTML='<div class="empty">No saved chats yet.</div>';return}for(const x of a){const b=document.createElement("button");b.className="history-card";b.innerHTML="<b></b><small></small><span></span>";b.querySelector("b").textContent=x.title||"Chat";b.querySelector("small").textContent=x.time+" • "+(x.model||"");b.querySelector("span").textContent=(x.items?.find(i=>i.role==="user")?.text||"Saved").slice(0,160);b.onclick=()=>{setMode("chat");$("messages").innerHTML="";for(const m of x.items||[])add(m.role,m.text)};box.appendChild(b)}}
function setMode(m){mode=m;document.body.dataset.mode=m;document.querySelectorAll(".mode").forEach(b=>b.classList.toggle("active",b.dataset.mode===m));document.querySelectorAll(".view").forEach(v=>v.classList.remove("active"));$("view-"+m).classList.add("active");syncLoadButton();if(m==="history")history()}
function parse(md,cat){const a=[];for(const line of md.split(/\r?\n/)){if(!line.startsWith("|")||line.includes("|---"))continue;const c=line.split("|").map(x=>x.trim()).filter((x,i,z)=>i>0&&i<z.length-1);if(c.length<7||!/^[0-9]+$/.test(c[0]))continue;const m=(c[1].match(/\*\*([^*]+)\*\*/)||[])[1];if(m)a.push({name:m,family:c[2],license:c[3],downloads:(c[4]||"0").replace(/,/g,""),likes:(c[5]||"0").replace(/,/g,""),category:cat})}return a}
async function selectCategory(cat){$("category").value=cat.name;if(!cat.file){categoryModels=[];return render()}$("modelList").innerHTML='<div class="loading">Loading category…</div>';try{if(cache.has(cat.file))categoryModels=cache.get(cat.file);else{const md=await fetch("./"+cat.file).then(r=>{if(!r.ok)throw Error("Category unavailable");return r.text()});categoryModels=parse(md,cat.name);cache.set(cat.file,categoryModels)}render()}catch(e){categoryModels=[];render();status(e.message,"error")}}
function render(){const q=$("modelSearch").value.trim().toLowerCase();filteredModels=categoryModels.filter(m=>!q||(m.name+" "+m.family+" "+m.license).toLowerCase().includes(q));limit=100;paint()}
function paint(){const box=$("modelList");box.innerHTML="";const v=filteredModels.slice(0,limit);$("modelInfo").textContent=filteredModels.length?v.length+" of "+filteredModels.length+" models":"No models found.";for(const m of v){const b=document.createElement("button");b.className="model-card"+(m.name===selectedModel?" selected":"");const s=document.createElement("strong"),p=document.createElement("span"),sm=document.createElement("small");s.textContent=m.name;p.textContent=m.family+" • "+m.license;sm.textContent="↓ "+Number(m.downloads||0).toLocaleString()+" • ♥ "+Number(m.likes||0).toLocaleString();b.append(s,p,sm);b.onclick=()=>selectModel(m);box.appendChild(b)}$("moreModels").classList.toggle("hidden",v.length>=filteredModels.length)}
function options(){const gpu=!!navigator.gpu;return{device:gpu?"webgpu":"wasm",dtype:gpu?"q4f16":"q8",progress_callback:i=>{if(i.status==="progress_total"){$("progressBar").style.width=Math.min(100,Math.max(0,Number(i.progress)||0))+"%";status("Loading "+Math.round(i.progress||0)+"%…","busy")}if(i.status==="ready")$("progressBar").style.width="100%"}}}
function release(){try{loaded?.dispose?.()}catch{}loaded=null;loadedTask="";loadedModel=""}
async function pipe(task,model){if(loaded&&loadedTask===task&&loadedModel===model)return loaded;release();$("progressBar").style.width="0%";status("Loading "+model+"…","busy");loaded=await pipeline(task,model,options());loadedTask=task;loadedModel=model;status("✅ Ready ("+(navigator.gpu?"WebGPU":"WASM")+")","ok");return loaded}
function generated(o){const v=o?.[0]?.generated_text;if(Array.isArray(v)){const z=v[v.length-1];return z?.content??JSON.stringify(z)}return typeof v==="string"?v:String(v??"")}
async function textRun(prompt){
  if(mode==="code" && !isBrowserTextModel(selectedModel)) selectedModel=presets.code.model;
  if(mode==="chat" && !isBrowserTextModel(selectedModel)) selectedModel=presets.chat.model;
  syncLoadButton();
  const p=await pipe("text-generation",selectedModel||presets.chat.model);const sys=mode==="code"?"You are a precise coding assistant. Provide usable code and concise explanations.":"Answer clearly and helpfully.";return p([{role:"system",content:sys},{role:"user",content:prompt}],{max_new_tokens:512,do_sample:true,temperature:Number($("temperature").value),top_p:.9,repetition_penalty:1.05})}
async function imageRun(){if(!imageBlob)return $("imageOutput").textContent="Choose an image first.";const p=await pipe($("imageTask").value==="caption"?"image-to-text":"image-classification",$("imageTask").value==="caption"?presets["image-caption"].model:presets["image-classify"].model);const o=await p(imageBlob,$("imageTask").value==="caption"?{max_new_tokens:128}:{top_k:5});$("imageOutput").textContent=JSON.stringify(o,null,2)}
async function audioRun(){if(!audioBlob)return $("audioOutput").textContent="Choose audio first.";const p=await pipe("automatic-speech-recognition",presets.audio.model),u=URL.createObjectURL(audioBlob);try{$("audioOutput").textContent=(await p(u,{chunk_length_s:20,return_timestamps:true}))?.text||"No text"}finally{URL.revokeObjectURL(u)}}
async function frameRun(){if(!frameBlob)return $("videoOutput").textContent="Capture a frame first.";const p=await pipe("image-to-text",presets["image-caption"].model);$("videoOutput").textContent=JSON.stringify(await p(frameBlob,{max_new_tokens:128}),null,2)}
document.querySelectorAll(".mode").forEach(b=>b.onclick=()=>setMode(b.dataset.mode));$("category").onchange=async()=>{const c=categories.find(x=>x.name===$("category").value);if(c)await selectCategory(c)};$("modelSearch").oninput=render;$("moreModels").onclick=()=>{limit+=100;paint()};$("loadModel").onclick=loadSelectedTextModel;$("temperature").oninput=()=>$("tempValue").textContent=$("temperature").value;
$("textForm").onsubmit=async e=>{e.preventDefault();const p=$("prompt").value.trim();if(!p)return;add("user",p);$("prompt").value="";add("assistant","⏳");try{$("messages").lastElementChild.textContent=generated(await textRun(p));status("Done.","ok");saveHistory(p.slice(0,60),msgs())}catch(err){$("messages").lastElementChild.textContent="Error: "+(err?.message||err);status("Generation failed.","error")}};
$("runCode").onclick=async()=>{const p=$("codePrompt").value.trim();if(!p)return;const old=mode;mode="code";try{$("codeOutput").textContent=generated(await textRun(p))}catch(e){$("codeOutput").textContent="Error: "+(e?.message||e)}finally{mode=old}};
$("imageFile").onchange=()=>{const f=$("imageFile").files[0];if(!f)return;imageBlob=f;$("imagePreview").src=URL.createObjectURL(f);$("imagePreview").classList.remove("hidden")};$("analyzeImage").onclick=async()=>{try{await imageRun()}catch(e){$("imageOutput").textContent="Error: "+(e?.message||e)}};
$("audioFile").onchange=()=>{const f=$("audioFile").files[0];if(!f)return;audioBlob=f;$("audioPreview").src=URL.createObjectURL(f);$("audioPreview").classList.remove("hidden")};$("transcribeAudio").onclick=async()=>{try{await audioRun()}catch(e){$("audioOutput").textContent="Error: "+(e?.message||e)}};
$("videoFile").onchange=()=>{const f=$("videoFile").files[0];if(!f)return;videoUrl=URL.createObjectURL(f);const v=$("videoPreview");v.src=videoUrl;v.classList.remove("hidden");v.onloadedmetadata=()=>{$("videoTime").max=v.duration||0}};$("videoTime").oninput=()=>{$("videoPreview").currentTime=Number($("videoTime").value);$("videoTimeLabel").textContent=Number($("videoPreview").currentTime).toFixed(1)+"s"};$("captureFrame").onclick=()=>{const v=$("videoPreview"),c=$("videoCanvas");if(!v.videoWidth)return $("videoOutput").textContent="Choose a video first.";c.width=v.videoWidth;c.height=v.videoHeight;c.getContext("2d").drawImage(v,0,0,c.width,c.height);c.toBlob(b=>{frameBlob=b;$("framePreview").src=URL.createObjectURL(b);$("framePreview").classList.remove("hidden")},"image/jpeg",.85)};$("analyzeFrame").onclick=async()=>{try{await frameRun()}catch(e){$("videoOutput").textContent="Error: "+(e?.message||e)}};
$("clearChat").onclick=()=>{$("messages").innerHTML='<div class="welcome"><h2>Chat cleared</h2><p>Select a model and start again.</p></div>'};$("clearHistory").onclick=()=>{localStorage.removeItem(HISTORY);history()};
$("runtimeBadge").textContent=navigator.gpu?"⚡ WebGPU available":"CPU/WASM mode";document.body.dataset.mode="chat";
try{presets=await fetch("./models.json").then(r=>r.json());categories=await fetch("./categories.json").then(r=>r.json());$("category").innerHTML=categories.map(c=>'<option value="'+c.name.replace(/"/g,"&quot;")+'">'+c.name+"</option>").join("");$("selectedModel").innerHTML="<b>"+selectedModel+"</b><span>Small + fast browser preset</span>";syncLoadButton();await selectCategory(categories[1]||categories[0])}catch(e){$("modelInfo").textContent="Setup error: "+(e?.message||e)};