import { writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '../../..');
const pages = await (await fetch('http://127.0.0.1:9226/json')).json();
const socket = new WebSocket(pages.find(p => p.type === 'page').webSocketDebuggerUrl);
await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
const pending = new Map(); let sequence = 0;
const errors = [], failed = [];
socket.onmessage = ({ data }) => {
  const m = JSON.parse(data);
  if (m.id) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result); }
  if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.text);
  if (m.method === 'Network.loadingFailed') failed.push(m.params.errorText);
};
const send = (method, params={}) => new Promise((resolve,reject) => { const id=++sequence; pending.set(id,{resolve,reject}); socket.send(JSON.stringify({id,method,params})); });
async function ev(expression) {
  const r = await send('Runtime.evaluate',{expression,awaitPromise:true,returnByValue:true});
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
  return r.result.value;
}
const temp = path.join(root, 'tmp/pdfs/power-semiconductors');
await mkdir(temp, {recursive:true});
try {
  await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
  await send('Page.navigate',{url:pathToFileURL(path.join(here,'答案.html')).href});
  for(let i=0;i<100;i++) {
    if(await ev('document.readyState === "complete" && document.querySelectorAll(".katex").length > 50')) break;
    await new Promise(r=>setTimeout(r,50));
  }
  await ev('document.fonts.ready');
  const checks = [];
  for(const width of [390, 1000, 1440]) {
    await send('Emulation.setDeviceMetricsOverride',{width,height:1100,deviceScaleFactor:1,mobile:false});
    await ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');
    const data = await ev(`({width:innerWidth,documentWidth:document.documentElement.scrollWidth,brokenInternalLinks:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash),mathErrors:document.querySelectorAll('.katex-error').length,figures:document.querySelectorAll('figure').length,sheets:document.querySelectorAll('.sheet').length})`);
    if(data.documentWidth > width || data.brokenInternalLinks.length || data.mathErrors || data.figures !== 5 || data.sheets !== 9) throw new Error(JSON.stringify(data));
    checks.push(data);
  }
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1100,deviceScaleFactor:1,mobile:false});
  for(const id of ['q1','q2','q3','q4','review']) {
    await ev(`document.getElementById(${JSON.stringify(id)}).scrollIntoView()`);
    await ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');
    const screenshot = await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    await writeFile(path.join(temp,id+'.png'),Buffer.from(screenshot.data,'base64'));
  }
  await send('Emulation.setEmulatedMedia',{media:'print'});
  const pdf = await send('Page.printToPDF',{printBackground:true,preferCSSPageSize:true,displayHeaderFooter:false});
  const output = path.resolve(root, process.argv[2] || 'output/pdf/功率半导体器件-第二章测试答案-完整版.pdf');
  await writeFile(output, Buffer.from(pdf.data,'base64'));
  if(errors.length || failed.length) throw new Error(JSON.stringify({errors,failed}));
  await writeFile(path.join(temp,'browser-checks.json'),JSON.stringify({checks,errors,failed,pdf:output},null,2));
  console.log(JSON.stringify({checks,errors,failed,pdf:output},null,2));
} finally { socket.close(); }
