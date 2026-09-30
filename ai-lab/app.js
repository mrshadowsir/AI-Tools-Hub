const $=id=>document.getElementById(id);
function addMessage(role,text){const el=document.createElement("div");el.className="msg "+role;el.textContent=text;$("messages").appendChild(el);el.scrollIntoView({behavior:"smooth"});}
function setStatus(t){$("status").textContent=t;}
async function api(path,opts={}){const r=await fetch(path,opts);if(!r.ok)throw new Error(await r.text());return r.json();}
async function loadOllamaModels(){const s=$("model");s.innerHTML="";try{const d=await api("/api/ollama/models");if(!d.models.length){s.innerHTML='<option value="">No local models installed</option>';setStatus("Ollama detected; install a local model first.");return;}for(const m of d.models){const o=document.createElement("option");o.value=m.name;o.textContent=m.name;s.appendChild(o);}setStatus("Ollama ready — inference stays on your PC.");}catch(e){s.innerHTML='<option value="">Ollama unavailable</option>';setStatus("Ollama not reachable. Start Ollama or switch to Hugging Face Local.");}}
$("runtime").addEventListener("change",()=>{const hf=$("runtime").value==="huggingface";$("model").classList.toggle("hidden",hf);$("refresh").classList.toggle("hidden",hf);$("hfModel").classList.toggle("hidden",!hf);if(!hf)loadOllamaModels();else setStatus("Hugging Face Local — weights run on your PC.");});
$("refresh").addEventListener("click",loadOllamaModels);

$("searchBtn").addEventListener("click",async ()=>{
  const q=$("search").value.trim();
  if(!q) return;
  try{
    const d=await api("/api/catalog/search?q="+encodeURIComponent(q)+"&limit=100");
    const s=$("catalog"); s.innerHTML="";
    for(const m of d.models){
      const o=document.createElement("option");
      o.value=m.name;
      o.textContent=m.name+" — "+m.category;
      s.appendChild(o);
    }
    setStatus(d.models.length ? d.models.length+" open-source models found. Select one." : "No matching open-source models found.");
  }catch(e){ setStatus("Catalog search failed: "+e.message); }
});

$("catalog").addEventListener("change",()=>{
  const id=$("catalog").value;
  if(id){ $("runtime").value="huggingface"; $("model").classList.add("hidden"); $("refresh").classList.add("hidden"); $("hfModel").classList.remove("hidden"); $("hfModel").value=id; setStatus("Selected "+id+". It will run locally when supported."); }
});
$("clear").addEventListener("click",()=>{$("messages").innerHTML="";});
$("temperature").addEventListener("input",()=>$("tempValue").textContent=$("temperature").value);
$("chatForm").addEventListener("submit",async e=>{e.preventDefault();const prompt=$("prompt").value.trim();if(!prompt)return;addMessage("user",prompt);$("prompt").value="";$("send").disabled=true;$("send").textContent="…";try{const runtime=$("runtime").value;const model=runtime==="ollama"?$("model").value:$("hfModel").value.trim();if(!model)throw new Error("Select or enter a model first.");const d=await api("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({runtime,model,task:$("task").value,temperature:Number($("temperature").value),prompt})});addMessage("ai",d.response);}catch(err){addMessage("ai","Error: "+err.message);}finally{$("send").disabled=false;$("send").textContent="Send";}});
loadOllamaModels();