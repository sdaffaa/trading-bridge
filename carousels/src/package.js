import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { carousels, HANDLE } from './content.js';

const PNG='out/png', PDF='dist', DELIV='dist/liquidity-state-carousels';
const slug=(c,p)=>`${c.idx}_${String(p).padStart(2,'0')}_${c.slug}`;

// ---- assemble delivery folder ----
fs.rmSync(DELIV,{recursive:true,force:true});
fs.mkdirSync(path.join(DELIV,'png'),{recursive:true});
fs.mkdirSync(path.join(DELIV,'pdf'),{recursive:true});
for(const c of carousels) for(let i=1;i<=6;i++){const n=slug(c,i)+'.png';fs.copyFileSync(path.join(PNG,n),path.join(DELIV,'png',n));}
for(const c of carousels){const n=`${c.idx}_${c.slug}.pdf`;fs.copyFileSync(path.join(PDF,n),path.join(DELIV,'pdf',n));}
fs.copyFileSync(path.join(PDF,'liquidity-state-batch_30pages.pdf'),path.join(DELIV,'pdf','00_liquidity-state-batch_30pages.pdf'));
fs.copyFileSync('out/contact-sheet.png',path.join(DELIV,'contact-sheet.png'));

// ---- Arabic README ----
const pageTitle = s => s.kind==='cover'?'الغلاف (هوك)':s.kind==='cta'?'CTA (كلمة مفتاحية)':(s.h1||s.eyebrow);
let md = `# Liquidity State — دفعة الكاروسيلات (5 × 6 = 30 صفحة)\n\n`;
md += `دفعة تعليمية متكاملة لحساب **${HANDLE}** تغطّي سبعة مجالات: ICT · SMC · Footprint · Volume Profile · VWAP · Volume · علم النفس.\n`;
md += `كل الشارتات **رسوم توضيحية تعليمية** بأرقام تعليمية — ليست بيانات حقيقية ولا توصيات تداول.\n\n`;
md += `المقاس: 1080×1350 (4:5) · RGB · الخط: Tajawal · الاتجاه: RTL.\n\n`;
md += `## المحتويات\n\n`;
md += `- \`png/\` — 30 صورة PNG مرقّمة \`CC_PP_slug.png\` (CC = رقم الكاروسيل، PP = رقم الصفحة).\n`;
md += `- \`pdf/\` — 5 ملفات PDF (6 صفحات لكل كاروسيل) + \`00_...batch_30pages.pdf\` الموحّد (30 صفحة).\n`;
md += `- \`contact-sheet.png\` — لوح معاينة لكل الصفحات الثلاثين.\n\n`;
md += `## ترتيب النشر\n\nانشر كل كاروسيل بصفحاته الست بالترتيب من 01 إلى 06 (الغلاف أولًا، ثم المحتوى، ثم صفحة الـCTA).\n\n`;
md += `> ملاحظة RTL: في لوح المعاينة تظهر الصفحة 01 (الغلاف) على يمين كل صف والصفحة 06 على يساره.\n\n`;
md += `## الكاروسيلات\n\n`;
const typeMap={};
for(const c of carousels){
  md += `### ${c.idx} — ${c.title}\n\n`;
  md += `| الحقل | القيمة |\n|---|---|\n`;
  md += `| النوع | ${c.type} |\n`;
  md += `| المجال | ${c.domains} |\n`;
  md += `| الكلمة المفتاحية (ManyChat) | \`${c.kw}\` |\n`;
  md += `| الهوك | ${c.hookAlts[0]} |\n`;
  md += `| الصفحات | ${c.slides.map((s,i)=>`0${i+1} ${pageTitle(s)}`).join(' · ')} |\n\n`;
  md += `**المصادر:**\n`;
  md += c.sources.map(s=>`- ${s}`).join('\n')+'\n\n';
}
md += `## تنويه\n\nكل النماذج تعليمية لتوضيح المفهوم فقط، وليست توصيات ولا صفقات مضمونة. الأرقام على شارتات الفوت برنت وبروفايل الحجم أرقام تعليمية.\n`;
fs.writeFileSync(path.join(DELIV,'README.md'),md);

// ---- zip ----
const zipName='liquidity-state-carousels.zip';
execSync(`cd dist && rm -f ${zipName} && zip -qr ${zipName} liquidity-state-carousels`,{stdio:'inherit'});
console.log('packaged →', path.join(PDF,zipName));
console.log('README bytes', md.length);
