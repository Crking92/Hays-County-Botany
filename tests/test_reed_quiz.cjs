/* Offline CI test for exactly the licensed source-photo quizzes that can
   appear in the public noncommercial Hays Botany website. */
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
const context={window:{}};
const src=fs.readFileSync(path.join(root,'assets/js/reed-quiz.js'),'utf8');
vm.runInNewContext(src,context,{filename:'reed-quiz.js'});
const tool=context.window.HaysReedQuiz;
assert.ok(tool&&typeof tool.build==='function');
assert.equal(tool.requiredSpecies.length,3);
const cards={};
for(const id of tool.requiredSpecies){
 const [genus]=id.split('-');
 const dirs={ 'arundo-donax':'Arundo','phragmites-australis':'Phragmites','zizaniopsis-miliacea':'Zizaniopsis' };
 const p=path.join(root,'content/taxa/Poaceae',dirs[id],id,'species.json');
 const data=JSON.parse(fs.readFileSync(p,'utf8'));
 assert.equal(data.id,id);
 cards[id]=data;
}
const questions=tool.build(cards);
assert.equal(questions.length,10,'All ten curated questions must have licensed source photos');
const identifiers=new Set(), study=new Set(), sources=new Set();
for(const q of questions){
 assert.ok(!identifiers.has(q.id),'duplicate question');
 identifiers.add(q.id);
 assert.equal(q.mode,'reed');
 assert.equal(q.choices.length,4);
 assert.equal(new Set(q.choices.map(x=>x.id)).size,4);
 assert.equal(new Set(q.choices.map(x=>x.label)).size,4);
 assert.ok(q.question.length>35);
 assert.ok(q.answer&&q.choices.some(x=>x.id===q.answer.id));
 assert.ok(q.choices.every(x=>x.feedback&&x.feedback.length>25));
 assert.ok(q.explanation&&q.explanation.length>30);
 assert.ok(/^content\/taxa\/Poaceae\//.test(q.photo.thumbnail));
 assert.ok(fs.existsSync(path.join(root,q.photo.thumbnail)),q.photo.thumbnail);
 assert.ok(q.photo.thumbnail_creator&&!/Neil Reese|SDSU/i.test(q.photo.thumbnail_creator));
 assert.ok(/CC BY|Public domain/i.test(q.photo.thumbnail_license));
 assert.ok(q.photo.thumbnail_source.startsWith('https://'));
 study.add(q.study);sources.add(q.photo.thumbnail);
}
for(const id of tool.requiredSpecies)assert.ok(study.has(id),'missing look-alike species '+id);
assert.ok(sources.size>=7,'questions should teach from several different real images');
const quizUI=fs.readFileSync(path.join(root,'assets/js/quiz-tiles.js'),'utf8');
const fieldUI=fs.readFileSync(path.join(root,'assets/js/field-id-tiles.js'),'utf8');
const quizHtml=fs.readFileSync(path.join(root,'quiz.html'),'utf8');
assert.ok(quizHtml.indexOf('reed-quiz.js')<quizHtml.indexOf('quiz-tiles.js'));
assert.ok(quizUI.includes("mode==='reed'")&&quizUI.includes('HaysReedQuiz.build'));
assert.ok(fieldUI.includes('data-compare-species')&&fieldUI.includes('compareReeds('));
for(const species of ['arundo-donax','phragmites-australis','zizaniopsis-miliacea']){
 assert.ok(fieldUI.includes(species),'comparison option absent: '+species);
}
assert.ok(fieldUI.includes("new URLSearchParams(window.location.search)"));
console.log('PASS: 10 source-validated reed quiz questions, 3 look-alikes, 4 options each, licenses, real files, deep links.');
