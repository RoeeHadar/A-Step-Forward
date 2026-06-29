const {writeFileSync}=require('fs');
const {join}=require('path');
const out=join(__dirname,'seed_data/lessons/statistics_descriptive.json');
const lesson=JSON.parse(process.argv[1]);
writeFileSync(out, JSON.stringify(lesson,null,2)+'\n','utf8');
console.log('Wrote', out);
