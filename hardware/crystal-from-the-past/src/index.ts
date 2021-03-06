import fs from 'fs';
import { PNG } from 'pngjs/browser';

function parse(st: string) {
    return st.match(/../g).reverse().join('');
}

const size = 1000;

const dst = new PNG({ colorType:0, width: size, height: size });


for(let row of fs.readFileSync("src/challenge.csv", 'ascii').split("\n")){
    const parts = row.split(",");
    const part = parts[6].split("\"")[1];
    const bytes = [2,2,2];
    let i = 0;
    const parsed: any[] = [];
    for(let b of bytes){
        const p = parse(part.substring(i, i + b * 2));
        parsed.push(p);
        i = i + b * 2;
    }
    parsed.push(part.substring(i));

    let x = parseInt(parsed[1], 16);
    let y = parseInt(parsed[2], 16);

    x= Math.floor(x/50);
    y= Math.floor(y/50);
    if(x > size || y > size){
        continue;
    }
    let ptr = (y * size  + x) * 4;


    const c = parsed[0] == 'a102' ? 255 : 0;

    if (c != 0){
        dst.data[ptr] = c;
        dst.data[ptr+1] = c;
        dst.data[ptr+2] = c;
        dst.data[ptr+3] = 255;
    }
}

const buffer = PNG.sync.write(dst);
fs.writeFileSync("out.png", buffer);