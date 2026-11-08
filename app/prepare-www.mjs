// 把網站的 index.html 複製成 App 的內容，前面加上 Capacitor 的小程式（App 裡才用得到：返回鍵、分享選單）
import {readFileSync,writeFileSync,mkdirSync,copyFileSync} from 'node:fs';
mkdirSync('www',{recursive:true});
copyFileSync('node_modules/@capacitor/core/dist/capacitor.js','www/capacitor.js');
let html=readFileSync('../index.html','utf8');
if(!html.includes('<script src="capacitor.js"></script>'))html=html.replace('<head>','<head>\n<script src="capacitor.js"></script>');
writeFileSync('www/index.html',html);
console.log('www/index.html',html.length,'bytes');
