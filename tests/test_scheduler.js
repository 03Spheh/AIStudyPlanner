const fs=require('fs'), path=require('path');
let html=fs.readFileSync(path.join(__dirname,'..','templates','timetable.html'),'utf8').replace(/\r\n/g,'\n');
let a=html.indexOf('const days = ['), b=html.lastIndexOf('/* ----',html.indexOf('   DISPLAY RESULTS'));
let src=html.slice(a,b);
global.fetch=function(){return Promise.resolve({});};
let captured=null, err=null;
const stubs=`
var __mods=[], __avail=[];
function hideError(){}
function showError(m){ __err=m; }
function displayTimetable(s,m,tm,ts,c){ __out={s,m,tm,ts}; }
var document={getElementById:function(){return {value:'yes'}}};
var __err=null,__out=null;
`;
function iso(d){const x=new Date();x.setDate(x.getDate()+d);return x.toISOString().slice(0,10);}
const run=(mods,avail)=>{
  const body=stubs+src+`
  getModules=function(){return ${JSON.stringify(mods)}.map(m=>Object.assign({sessions:0,lastStudiedDay:null},m));};
  getAvailability=function(i){return ${JSON.stringify(avail)}[i]||null;};
  generateTimetable(); return {err:__err,out:__out};`;
  return new Function(body)();
};
let pass=0,total=0; function check(n,c){total++; if(c)pass++; console.log((c?'PASS ':'FAIL ')+n);}
// priority ordering
const pf=new Function(stubs+src+`return {base:calculateBasePriority};`)();
const exam=pf.base({credits:30,assessment:'Exam',dueDate:iso(2)});
const assign=pf.base({credits:10,assessment:'Assignment',dueDate:iso(40)});
check('Priority: high-credit near exam ranks above low-credit distant assignment', exam>assign);
const near=pf.base({credits:15,assessment:'Test',dueDate:iso(3)}), far=pf.base({credits:15,assessment:'Test',dueDate:iso(35)});
check('Priority: nearer deadline ranks above distant deadline (same credits/type)', near>far);
// schedule constraints: Mon 18:00-22:00, Wed 09:00-12:00, rest unavailable
const mods=[{name:'Maths',credits:30,assessment:'Exam',dueDate:iso(5)},{name:'Physics',credits:15,assessment:'Test',dueDate:iso(10)},{name:'Ethics',credits:10,assessment:'Assignment',dueDate:iso(20)}];
const av={0:{startMinutes:1080,endMinutes:1320,totalMinutes:240},2:{startMinutes:540,endMinutes:720,totalMinutes:180}};
const r=run(mods,av);
check('Schedule generated without error', !r.err && r.out);
const s=r.out.s;
let inside=true, overlap=false, maxMods=true, unavail=true;
s.forEach((d,i)=>{
  const a=av[i];
  if(!a){ if(d.sessions.length) unavail=false; return;}
  let prevEnd=-1; const names=new Set();
  d.sessions.forEach(x=>{ if(x.start<a.startMinutes||x.end>a.endMinutes) inside=false; if(x.start<prevEnd) overlap=true; prevEnd=x.end; if(!x.break) names.add(x.module);});
  if(names.size>2) maxMods=false;
});
check('All sessions fall inside the available windows', inside);
check('No sessions on unavailable days', unavail);
check('No overlapping sessions', !overlap);
check('No more than 2 different modules per day', maxMods);
check('Sessions are 60 minutes long', s.flatMap(d=>d.sessions).filter(x=>!x.break).every(x=>x.end-x.start===60));
const none=run(mods,{});
check('Error shown when no day is available', !!none.err);
const mods2=[{name:'A',credits:30,assessment:'Exam',dueDate:iso(3)}];
const bad=run([{name:'',credits:10,assessment:'Exam',dueDate:iso(3)}],av);
check('Validation rejects module without a name', !!bad.err);
console.log(pass+' / '+total);
